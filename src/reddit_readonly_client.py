"""Sanitized read-only Reddit OAuth client for API-review purposes.

This file intentionally contains no credentials, trading logic, brokerage integration,
or strategy implementation. It demonstrates the Reddit-facing behavior relevant to the
requested API access.
"""

from __future__ import annotations

import asyncio
import random
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import aiohttp

TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API_BASE_URL = "https://oauth.reddit.com"


class RedditError(RuntimeError):
    """Base Reddit client error."""


class RedditAuthenticationError(RedditError):
    """OAuth credentials/token were rejected."""


class RedditTransportError(RedditError):
    """The network request failed before a usable API response was received."""


class RedditApiError(RedditError):
    def __init__(self, status: int, message: str, *, retryable: bool) -> None:
        super().__init__(message)
        self.status = status
        self.retryable = retryable


@dataclass(frozen=True, slots=True)
class RateLimitState:
    used: float | None = None
    remaining: float | None = None
    reset_seconds: float | None = None

    @classmethod
    def from_headers(cls, headers: Mapping[str, str]) -> "RateLimitState":
        normalized = {key.casefold(): value for key, value in headers.items()}

        def as_number(name: str) -> float | None:
            try:
                return float(normalized[name])
            except (KeyError, TypeError, ValueError):
                return None

        return cls(
            used=as_number("x-ratelimit-used"),
            remaining=as_number("x-ratelimit-remaining"),
            reset_seconds=as_number("x-ratelimit-reset"),
        )

    def recommended_delay(self, *, base_seconds: float, reserve: int) -> float:
        """Spread calls across the remaining window while preserving capacity."""

        if self.remaining is None or self.reset_seconds is None or self.reset_seconds <= 0:
            return base_seconds

        usable = self.remaining - reserve
        if usable <= 0:
            return max(base_seconds, self.reset_seconds)

        return max(base_seconds, self.reset_seconds / usable)


@dataclass(frozen=True, slots=True)
class FetchedListing:
    payload: Mapping[str, Any]
    received_at: datetime
    rate_limit: RateLimitState


class RedditRateLimited(RedditApiError):
    def __init__(self, retry_after_seconds: float, state: RateLimitState) -> None:
        super().__init__(429, "Reddit rate limit reached", retryable=True)
        self.retry_after_seconds = retry_after_seconds
        self.rate_limit = state


@dataclass(frozen=True, slots=True)
class BackoffPolicy:
    base_seconds: float = 1.0
    maximum_seconds: float = 60.0
    jitter_ratio: float = 0.2

    def delay(self, attempt: int) -> float:
        exponential = min(self.maximum_seconds, self.base_seconds * (2 ** min(attempt, 20)))
        jitter = 1 + (((random.random() * 2) - 1) * self.jitter_ratio)
        return min(self.maximum_seconds, max(0.0, exponential * jitter))


class RedditReadOnlyClient:
    """Small OAuth client restricted to public listing reads."""

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        user_agent: str,
        subreddit: str = "wallstreetbets",
        listing_limit: int = 100,
        request_timeout_seconds: float = 10.0,
    ) -> None:
        if not client_id or not client_secret:
            raise ValueError("Reddit OAuth credentials are required")
        if not user_agent.strip():
            raise ValueError("A descriptive Reddit User-Agent is required")
        if not 1 <= listing_limit <= 100:
            raise ValueError("listing_limit must be between 1 and 100")

        normalized_subreddit = subreddit.strip().removeprefix("r/").removeprefix("/r/")
        if not normalized_subreddit or "/" in normalized_subreddit:
            raise ValueError("subreddit must be one subreddit name")

        self._client_id = client_id
        self._client_secret = client_secret
        self._user_agent = user_agent
        self._subreddit = normalized_subreddit
        self._listing_limit = listing_limit
        self._timeout = aiohttp.ClientTimeout(total=request_timeout_seconds)
        self._session: aiohttp.ClientSession | None = None
        self._access_token: str | None = None
        self._token_expires_at_monotonic = 0.0

    async def __aenter__(self) -> "RedditReadOnlyClient":
        await self._get_session()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def close(self) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession(headers={"User-Agent": self._user_agent})
        return self._session

    async def _get_token(self) -> str:
        now = asyncio.get_running_loop().time()
        if self._access_token and now < self._token_expires_at_monotonic:
            return self._access_token

        session = await self._get_session()
        try:
            async with session.post(
                TOKEN_URL,
                data={"grant_type": "client_credentials"},
                headers={
                    "Authorization": aiohttp.BasicAuth(
                        self._client_id,
                        self._client_secret,
                    ).encode()
                },
                timeout=self._timeout,
            ) as response:
                if response.status != 200:
                    raise RedditAuthenticationError(
                        f"Reddit OAuth rejected the client with HTTP {response.status}"
                    )
                payload = await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as exc:
            raise RedditTransportError(
                f"Reddit OAuth transport failed: {type(exc).__name__}"
            ) from exc

        if not isinstance(payload, Mapping) or not isinstance(payload.get("access_token"), str):
            raise RedditAuthenticationError("Reddit OAuth response contained no access token")

        expires_in = payload.get("expires_in", 3600)
        lifetime = float(expires_in) if isinstance(expires_in, (int, float)) else 3600.0
        self._access_token = payload["access_token"]
        self._token_expires_at_monotonic = now + max(1.0, lifetime - 30.0)
        return self._access_token

    async def fetch_new_submissions(self) -> FetchedListing:
        return await self._fetch_listing("new")

    async def fetch_recent_comments(self) -> FetchedListing:
        return await self._fetch_listing("comments")

    async def _fetch_listing(self, endpoint: str) -> FetchedListing:
        if endpoint not in {"new", "comments"}:
            raise ValueError("Only approved read-only listing endpoints are supported")

        url = f"{API_BASE_URL}/r/{self._subreddit}/{endpoint}"
        session = await self._get_session()

        for auth_attempt in range(2):
            token = await self._get_token()
            try:
                async with session.get(
                    url,
                    params={"limit": self._listing_limit, "raw_json": 1},
                    headers={"Authorization": f"bearer {token}"},
                    timeout=self._timeout,
                ) as response:
                    received_at = datetime.now(UTC)
                    rate_limit = RateLimitState.from_headers(response.headers)

                    if response.status == 401 and auth_attempt == 0:
                        self._access_token = None
                        self._token_expires_at_monotonic = 0.0
                        continue
                    if response.status == 401:
                        raise RedditAuthenticationError("Reddit OAuth token was rejected")
                    if response.status == 429:
                        raw_retry = response.headers.get("Retry-After")
                        try:
                            retry_after = float(raw_retry) if raw_retry else 1.0
                        except ValueError:
                            retry_after = 1.0
                        raise RedditRateLimited(retry_after, rate_limit)
                    if response.status >= 400:
                        raise RedditApiError(
                            response.status,
                            f"Reddit listing returned HTTP {response.status}",
                            retryable=response.status >= 500,
                        )

                    payload = await response.json(content_type=None)
            except (aiohttp.ClientError, TimeoutError) as exc:
                raise RedditTransportError(
                    f"Reddit listing transport failed: {type(exc).__name__}"
                ) from exc

            if not isinstance(payload, Mapping):
                raise RedditApiError(200, "Reddit listing was not a JSON object", retryable=True)

            return FetchedListing(
                payload=payload,
                received_at=received_at,
                rate_limit=rate_limit,
            )

        raise RedditAuthenticationError("OAuth retry exhausted")

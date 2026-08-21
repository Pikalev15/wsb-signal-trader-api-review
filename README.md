# WSB Signal Trader — Reddit API Review Package

This repository is a sanitized review package for Reddit's Data API application process.
It documents only the Reddit-facing, read-only portion of the project. It intentionally omits
brokerage execution code, private configuration, credentials, proprietary strategy logic, and
other unrelated implementation details.

## Purpose

WSB Signal Trader is a private, non-commercial software-development project that evaluates
whether aggregate discussion activity in `r/wallstreetbets` has measurable relationships with
public market activity. Reddit data is one external input to a larger local analytics pipeline.

The initial Reddit scope is deliberately narrow:

- `r/wallstreetbets` only
- public submissions and public comments only
- OAuth-authenticated Reddit Data API only
- read-only access
- bounded listing requests
- no posting, voting, messaging, moderation, or engagement automation
- no HTML scraping or unofficial mirrors
- no rate-limit circumvention
- no sale or redistribution of Reddit data
- no AI/LLM/model training on Reddit content
- no live-trading authority in the Reddit component

## High-level data flow

```text
Reddit OAuth Data API
        |
        v
bounded recent-listing fetches
        |
        v
observation timestamp + rate-limit state
        |
        v
deduplication + deterministic parsing
        |
        v
candidate security/ticker extraction
        |
        v
aggregate mention statistics
        |
        v
external market-data comparison
        |
        v
paper-trading / observe-only evaluation
```

Reddit content does not directly issue brokerage instructions. The Reddit ingestion layer is
isolated from financial-market and execution providers.

## API behavior shown in this review package

The included example client demonstrates the same safety-relevant behavior used by the project:

- Reddit OAuth `client_credentials` authentication
- descriptive User-Agent support
- access-token caching and refresh
- one retry after an HTTP 401 token rejection
- `X-Ratelimit-Used`, `X-Ratelimit-Remaining`, and `X-Ratelimit-Reset` parsing
- HTTP 429 / `Retry-After` handling
- request timeouts
- bounded exponential backoff helper
- read-only requests for recent submissions and comments
- bounded `limit` values

The example intentionally contains **no credentials**. Credentials are supplied at runtime from
local environment configuration and must never be committed.

## Requested Reddit scope

The intended read-only calls are equivalent to:

```text
GET https://oauth.reddit.com/r/wallstreetbets/new
GET https://oauth.reddit.com/r/wallstreetbets/comments
```

with bounded `limit` and `raw_json=1` parameters.

## Why this is external rather than a Devvit app

The core product is not a Reddit user experience. Reddit observations are combined with external
financial reference data, market data, local deterministic processing, persistence/replay,
health monitoring, and a paper-trading environment. The Reddit layer therefore needs to operate
as an authenticated external data source in a larger Python application.

See:

- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`PRIVACY.md`](PRIVACY.md)
- [`SECURITY.md`](SECURITY.md)
- [`REDDIT_API_APPLICATION.md`](REDDIT_API_APPLICATION.md)
- [`src/reddit_readonly_client.py`](src/reddit_readonly_client.py)

## Commercial status

Current intended use is non-commercial and private. There are no customers, subscriptions,
advertisements, resale of Reddit data, paid signal products, or third-party API access.

Any future material expansion of the approved use case should be reviewed against Reddit's then-
current policies and permissions before that expanded use is enabled.

## Repository note

This is a public, sanitized review repository for Reddit reviewers. It is not the full trading
repository and does not contain credentials, brokerage execution code, or unrelated proprietary
strategy logic.

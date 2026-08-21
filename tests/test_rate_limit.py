from reddit_readonly_client import BackoffPolicy, RateLimitState


def test_rate_limit_headers_are_case_insensitive() -> None:
    state = RateLimitState.from_headers(
        {
            "X-Ratelimit-Used": "12",
            "x-ratelimit-remaining": "88",
            "X-RATELIMIT-RESET": "600",
        }
    )

    assert state.used == 12
    assert state.remaining == 88
    assert state.reset_seconds == 600


def test_delay_preserves_reserve() -> None:
    state = RateLimitState(used=95, remaining=5, reset_seconds=60)

    assert state.recommended_delay(base_seconds=2, reserve=5) == 60


def test_delay_spreads_requests_across_window() -> None:
    state = RateLimitState(used=10, remaining=90, reset_seconds=600)

    assert state.recommended_delay(base_seconds=2, reserve=5) > 7


def test_backoff_is_bounded() -> None:
    policy = BackoffPolicy(base_seconds=1, maximum_seconds=60, jitter_ratio=0)

    assert policy.delay(0) == 1
    assert policy.delay(10) == 60

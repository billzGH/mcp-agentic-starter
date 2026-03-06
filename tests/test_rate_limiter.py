"""Tests for examples/web-api/server.py — RateLimiter class."""

from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# acquire — under the limit
# ---------------------------------------------------------------------------


async def test_acquire_under_limit_does_not_block(web_api_mod):
    """Calls well under the limit should return without sleeping."""
    limiter = web_api_mod.RateLimiter(max_calls=10, period=60)
    # Make 5 calls — all should pass through instantly
    for _ in range(5):
        await limiter.acquire()
    assert len(limiter.calls) == 5


async def test_acquire_tracks_call_times(web_api_mod):
    limiter = web_api_mod.RateLimiter(max_calls=10, period=60)
    await limiter.acquire()
    assert len(limiter.calls) == 1
    assert isinstance(limiter.calls[0], datetime)


# ---------------------------------------------------------------------------
# acquire — old call cleanup
# ---------------------------------------------------------------------------


async def test_acquire_cleans_up_expired_calls(web_api_mod):
    """Calls older than the period window should be discarded."""
    limiter = web_api_mod.RateLimiter(max_calls=3, period=60)
    # Inject two calls that are outside the time window (61 seconds ago)
    old_time = datetime.now() - timedelta(seconds=61)
    limiter.calls = [old_time, old_time]

    # This call should clean up the old ones and succeed without blocking
    await limiter.acquire()
    # Only the new call should remain
    assert len(limiter.calls) == 1


async def test_acquire_does_not_clean_recent_calls(web_api_mod):
    """Calls within the period window should not be discarded."""
    limiter = web_api_mod.RateLimiter(max_calls=10, period=60)
    recent = datetime.now() - timedelta(seconds=30)
    limiter.calls = [recent, recent]

    await limiter.acquire()
    assert len(limiter.calls) == 3  # 2 existing + 1 new

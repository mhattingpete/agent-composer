"""Async-to-sync bridge for wrapping async MCP tools."""

import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Coroutine, TypeVar

T = TypeVar("T")


def make_sync_wrapper(async_func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    """Create a synchronous wrapper for an async function.

    This is needed because MCP tools are async, but Python's built-in
    code execution runs in a synchronous context. This wrapper handles
    two cases:

    1. Called from sync context: uses asyncio.run()
    2. Called from async context: uses thread pool to avoid nested event loops

    Args:
        async_func: The async function to wrap

    Returns:
        A synchronous function that calls the async function
    """

    @functools.wraps(async_func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            # Check if we're already in an async context
            asyncio.get_running_loop()
            # We're in an async context - need to run in thread pool
            # to avoid "cannot run nested event loop" error
            with ThreadPoolExecutor(max_workers=1) as executor:

                def run_in_thread() -> T:
                    return asyncio.run(async_func(*args, **kwargs))

                future = executor.submit(run_in_thread)
                return future.result()
        except RuntimeError:
            # No running event loop - safe to use asyncio.run()
            return asyncio.run(async_func(*args, **kwargs))

    return sync_wrapper


def is_async_callable(func: Callable) -> bool:
    """Check if a function is async."""
    return asyncio.iscoroutinefunction(func)

"""Regression: the optimize SSE stream must stop a live run when the client drops.

cross_repo_audit finding — `GET /optimize/stream/{run_id}` never checked for disconnect, so a
dropped viewer left the background optimizer running its full budget while its event queue grew
without bound. The fix polls `request.is_disconnected()`, signals the runner's stop_event on
disconnect (and on ASGI-server cancellation), and hard-bounds the queue with drop-oldest
semantics that still preserve the None done-sentinel.

These drive the route's async generator directly (via ``asyncio.run``) so no live SPICE, uvicorn,
or pytest-asyncio is needed.
"""
from __future__ import annotations

import asyncio
from typing import AsyncGenerator, cast

from spicexplorer_api.routes import optimize as optimize_route
from spicexplorer_api.services import optimizer_runner as runner


def _sse_stream(resp: object) -> AsyncGenerator[str, None]:
    """The route yields ``str`` SSE chunks; body_iterator is typed as the broader
    ``AsyncContentStream`` (str | bytes), so narrow it for the assertions below."""
    return cast("AsyncGenerator[str, None]", resp.body_iterator)  # type: ignore[attr-defined]


def _register_run(run_id: str, loop: asyncio.AbstractEventLoop) -> runner.RunState:
    state = runner.RunState(
        run_id=run_id,
        queue=asyncio.Queue(maxsize=runner._QUEUE_MAXSIZE),
        loop=loop,
        budget=10,
    )
    runner._runs[run_id] = state
    return state


async def _poll_disconnect_flow() -> None:
    loop = asyncio.get_running_loop()
    run_id = "test-stream-poll"
    state = _register_run(run_id, loop)
    try:
        # Two real trial events queued; the run is still in flight (no None sentinel).
        state.queue.put_nowait({"iter": 1, "score": 1.0})
        state.queue.put_nowait({"iter": 2, "score": 2.0})

        class _Req:
            def __init__(self) -> None:
                self.calls = 0

            async def is_disconnected(self) -> bool:
                self.calls += 1
                return self.calls >= 3  # 1st/2nd poll connected, 3rd reports the drop

        resp = await optimize_route.stream_run(run_id, _Req())  # type: ignore[arg-type]
        chunks = [chunk async for chunk in _sse_stream(resp)]

        # Both in-flight events were delivered, then the stream ended WITHOUT a done event...
        assert any('"iter": 1' in c for c in chunks)
        assert any('"iter": 2' in c for c in chunks)
        assert not any("done" in c for c in chunks)
        # ...and the disconnect signalled the runner to stop (no wasted budget).
        assert state.stop_event.is_set()
    finally:
        runner._runs.pop(run_id, None)


def test_stream_stops_run_on_client_disconnect_poll() -> None:
    asyncio.run(_poll_disconnect_flow())


async def _cancel_disconnect_flow() -> None:
    loop = asyncio.get_running_loop()
    run_id = "test-stream-cancel"
    state = _register_run(run_id, loop)
    try:
        class _Req:
            async def is_disconnected(self) -> bool:
                return False  # never self-reports; the ASGI server cancels the stream instead

        state.queue.put_nowait({"iter": 1, "score": 1.0})
        resp = await optimize_route.stream_run(run_id, _Req())  # type: ignore[arg-type]
        agen = _sse_stream(resp)

        first = await agen.__anext__()  # consume one event; generator suspends at the yield
        assert '"iter": 1' in first
        assert not state.stop_event.is_set()

        # uvicorn's HTTP protocol (ASGI spec 2.3) makes Starlette cancel this generator on
        # disconnect rather than surfacing it through is_disconnected(); aclose() throws the
        # GeneratorExit that finalization does, and the finally must still stop the run.
        await agen.aclose()
        assert state.stop_event.is_set()
    finally:
        runner._runs.pop(run_id, None)


def test_stream_stops_run_on_server_cancellation() -> None:
    asyncio.run(_cancel_disconnect_flow())


async def _completes_flow() -> None:
    loop = asyncio.get_running_loop()
    run_id = "test-stream-done"
    state = _register_run(run_id, loop)
    try:
        class _Req:
            async def is_disconnected(self) -> bool:
                return False

        state.queue.put_nowait({"iter": 1, "score": 1.0})
        state.queue.put_nowait(None)  # runner's end-of-run sentinel
        resp = await optimize_route.stream_run(run_id, _Req())  # type: ignore[arg-type]
        chunks = [chunk async for chunk in _sse_stream(resp)]

        # A genuine end-of-run emits the done event and must NOT re-stop an already-finished run.
        assert any('"done": true' in c for c in chunks)
        assert not state.stop_event.is_set()
    finally:
        runner._runs.pop(run_id, None)


def test_stream_completes_on_done_sentinel_without_stopping() -> None:
    asyncio.run(_completes_flow())


def test_bounded_queue_drops_oldest_and_preserves_sentinel() -> None:
    q: asyncio.Queue = asyncio.Queue(maxsize=3)
    for i in range(3):
        q.put_nowait({"iter": i})
    assert q.full()

    # A 4th event on a full queue evicts the OLDEST (iter 0) and stays bounded.
    runner._put_bounded_nowait(q, {"iter": 99})
    assert q.qsize() == 3

    # The None done-sentinel is never lost even when full — it evicts a stale trial event.
    runner._put_bounded_nowait(q, None)
    assert q.qsize() == 3

    drained = []
    while not q.empty():
        drained.append(q.get_nowait())

    assert {"iter": 0} not in drained  # oldest evicted
    assert {"iter": 99} in drained     # newest data event retained
    assert None in drained             # sentinel preserved
    assert len(drained) == 3

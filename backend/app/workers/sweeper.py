import asyncio
import logging
from sqlalchemy import text

from app.config import settings
from app.db.session import sweeper_session_factory

logger = logging.getLogger(__name__)

_sweeper_task: asyncio.Task | None = None
_stop_event: asyncio.Event | None = None


async def sweep_expired_holds():
    """Single execution pass of the asynchronous lease sweeper worker."""
    async with sweeper_session_factory() as session:
        try:
            # Principle III: Query expired active holds using SKIP LOCKED
            select_expired_sql = text(
                """
                SELECT id
                FROM holds
                WHERE status = 'ACTIVE' AND expires_at < NOW()
                FOR UPDATE SKIP LOCKED;
                """
            )
            res = await session.execute(select_expired_sql)
            expired_rows = res.fetchall()

            if not expired_rows:
                return 0

            expired_hold_ids = [row[0] for row in expired_rows]

            # Recycle associated seats to AVAILABLE & null current_hold_id
            recycle_seats_sql = text(
                """
                UPDATE seats
                SET status = 'AVAILABLE', current_hold_id = NULL
                WHERE current_hold_id = ANY(:hold_ids);
                """
            )
            await session.execute(recycle_seats_sql, {"hold_ids": expired_hold_ids})

            # Update holds status to EXPIRED
            expire_holds_sql = text(
                """
                UPDATE holds
                SET status = 'EXPIRED'
                WHERE id = ANY(:hold_ids);
                """
            )
            await session.execute(expire_holds_sql, {"hold_ids": expired_hold_ids})

            await session.commit()
            count = len(expired_hold_ids)
            logger.info(f"[SWEEPER WORKER] Cleaned up {count} expired hold(s).")
            return count

        except Exception as e:
            await session.rollback()
            logger.error(f"[SWEEPER WORKER] Error during hold cleanup pass: {e}")
            return 0


async def _sweeper_loop():
    logger.info(f"[SWEEPER WORKER] Starting background lease sweeper worker (interval: {settings.SWEEPER_INTERVAL_SECONDS}s)...")
    while _stop_event and not _stop_event.is_set():
        try:
            await sweep_expired_holds()
        except Exception as e:
            logger.error(f"[SWEEPER WORKER] Loop exception: {e}")
        
        # Sleep for interval unless stop event is triggered
        try:
            await asyncio.wait_for(_stop_event.wait(), timeout=settings.SWEEPER_INTERVAL_SECONDS)
            break
        except asyncio.TimeoutError:
            pass
    logger.info("[SWEEPER WORKER] Sweeper worker stopped.")


async def start_sweeper_worker():
    global _sweeper_task, _stop_event
    if _sweeper_task is None or _sweeper_task.done():
        _stop_event = asyncio.Event()
        _sweeper_task = asyncio.create_task(_sweeper_loop())


async def stop_sweeper_worker():
    global _sweeper_task, _stop_event
    if _stop_event:
        _stop_event.set()
    if _sweeper_task and not _sweeper_task.done():
        _sweeper_task.cancel()
        try:
            await _sweeper_task
        except asyncio.CancelledError:
            pass
    _sweeper_task = None
    _stop_event = None

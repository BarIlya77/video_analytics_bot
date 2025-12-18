from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_
from datetime import datetime, timedelta
from .models import Video, VideoSnapshot


class DatabaseOperations:
    """Простые операции с базой данных для тестирования"""

    @staticmethod
    async def count_all_videos(session: AsyncSession) -> int:
        """Сколько всего видео в системе?"""
        stmt = select(func.count()).select_from(Video)
        result = await session.execute(stmt)
        return result.scalar()

    @staticmethod
    async def count_videos_by_creator(session: AsyncSession, creator_id: str) -> int:
        """Сколько видео у конкретного креатора?"""
        stmt = select(func.count()).where(Video.creator_id == creator_id)
        result = await session.execute(stmt)
        return result.scalar()

    @staticmethod
    async def count_videos_by_views_threshold(session: AsyncSession, threshold: int) -> int:
        """Сколько видео с просмотрами больше порога?"""
        stmt = select(func.count()).where(Video.views_count > threshold)
        result = await session.execute(stmt)
        return result.scalar()

    @staticmethod
    async def sum_views_growth_for_date(session: AsyncSession, date: datetime) -> int:
        """Суммарный прирост просмотров за конкретную дату"""
        start_date = date.replace(hour=0, minute=0, second=0)
        end_date = start_date + timedelta(days=1)

        stmt = select(func.coalesce(func.sum(VideoSnapshot.delta_views_count), 0)).where(
            and_(
                VideoSnapshot.created_at >= start_date,
                VideoSnapshot.created_at < end_date
            )
        )
        result = await session.execute(stmt)
        return result.scalar() or 0

    @staticmethod
    async def count_videos_with_views_growth(session: AsyncSession, date: datetime) -> int:
        """Сколько видео получали новые просмотры в дату?"""
        start_date = date.replace(hour=0, minute=0, second=0)
        end_date = start_date + timedelta(days=1)

        # Находим уникальные видео с положительным приростом
        subquery = select(VideoSnapshot.video_id).where(
            and_(
                VideoSnapshot.created_at >= start_date,
                VideoSnapshot.created_at < end_date,
                VideoSnapshot.delta_views_count > 0
            )
        ).distinct()

        stmt = select(func.count()).select_from(subquery.subquery())
        result = await session.execute(stmt)
        return result.scalar()

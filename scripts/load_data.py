import asyncio
import json
import sys
import os
import uuid

from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import AsyncSessionLocal, engine
from database.models import Base, Video, VideoSnapshot

# Маппинг "какое поле → как конвертировать"
VIDEO_CONVERSIONS = {
    'id': lambda v: uuid.UUID(v),
    'video_created_at': lambda v: datetime.fromisoformat(v.replace('Z', '+00:00')).replace(tzinfo=timezone.utc),
    'created_at': lambda v: datetime.fromisoformat(v.replace('Z', '+00:00')).replace(tzinfo=timezone.utc),
    'updated_at': lambda v: datetime.fromisoformat(v.replace('Z', '+00:00')).replace(tzinfo=timezone.utc),
}

SNAPSHOT_CONVERSIONS = {
    'id': lambda v: uuid.UUID(v),
    'created_at': lambda v: datetime.fromisoformat(v.replace('Z', '+00:00')).replace(tzinfo=timezone.utc),
    'updated_at': lambda v: datetime.fromisoformat(v.replace('Z', '+00:00')).replace(tzinfo=timezone.utc),
}


async def load_data():
    with open('../videos.json', 'r') as f:
        data = json.load(f)

    async with AsyncSessionLocal() as session:
        for video_data in data.get('videos', []):
            # Video
            video_fields = {}
            for key, value in video_data.items():
                if key == "snapshots":
                    continue

                if key in VIDEO_CONVERSIONS and isinstance(value, str):
                    value = VIDEO_CONVERSIONS[key](value)

                video_fields[key] = value

            video = Video(**video_fields)
            session.add(video)

            # Snapshots
            for snap_data in video_data.get('snapshots', []):
                snap_fields = snap_data.copy()
                snap_fields['video_id'] = video_fields['id']

                for key, converter in SNAPSHOT_CONVERSIONS.items():
                    if key in snap_fields and isinstance(snap_fields[key], str):
                        snap_fields[key] = converter(snap_fields[key])

                snapshot = VideoSnapshot(**snap_fields)
                session.add(snapshot)

        try:
            await session.commit()
            print("Данные успешно загружены")
        except:
            await session.rollback()
            raise


async def recreate_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def main():
    await recreate_tables()
    await load_data()


if __name__ == "__main__":
    asyncio.run(main())

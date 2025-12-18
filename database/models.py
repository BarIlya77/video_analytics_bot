import uuid
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import create_async_engine
# from sqlalchemy.orm import declarative_base, relationship
# from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

Base = declarative_base()


class Video(Base):
    __tablename__ = 'videos'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # video_created_at = Column(DateTime, nullable=False)
    video_created_at = Column(DateTime(timezone=True), nullable=False)
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    reports_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    creator_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text('NOW()'))
    updated_at = Column(DateTime(timezone=True), server_default=text('NOW()'))
    # updated_at = Column(DateTime, server_default=text('NOW()'), onupdate=text('NOW()'))

    snapshots = relationship("VideoSnapshot", back_populates="video", cascade="all, delete-orphan")

    def __repr__(self):
        return (f"<Video("
                f"id={self.id},\n"
                f"created='{self.video_created_at}',\n"
                f"views='{self.views_count}',\n"
                f"likes='{self.likes_count}',\n"
                f"creator='{self.creator_id}',\n"
                f"created_at={self.created_at})>")


class VideoSnapshot(Base):
    __tablename__ = 'video_snapshots'

    # id = Column(Integer, primary_key=True)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey('videos.id', ondelete='CASCADE'), nullable=False,  default=uuid.uuid4)
    views_count = Column(BigInteger, default=0)
    likes_count = Column(BigInteger, default=0)
    comments_count = Column(BigInteger, default=0)
    reports_count = Column(BigInteger, default=0)
    delta_views_count = Column(BigInteger, default=0)
    delta_likes_count = Column(BigInteger, default=0)
    delta_comments_count = Column(BigInteger, default=0)
    delta_reports_count = Column(BigInteger, default=0)
    created_at = Column(DateTime(timezone=True), server_default=text('NOW()'), nullable=False)
    # updated_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text('NOW()'))
#     updated_at = Column(DateTime, server_default=text('NOW()'))

    video = relationship("Video", back_populates="snapshots")

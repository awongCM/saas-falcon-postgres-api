from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from .Base import Base


def utcnow():
    return datetime.now(timezone.utc)


class ValidationJob(Base):
    __tablename__ = 'validation_jobs'

    id = Column(Integer, primary_key=True)
    celery_task_id = Column(String(255), nullable=False, index=True)
    input_type = Column(String(32), nullable=False)
    input_value = Column(String(512), nullable=False)
    status = Column(String(32), nullable=False, default='PENDING')
    result = Column(Text)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

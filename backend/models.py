from sqlalchemy import Column, Integer, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from backend.database import Base


class Barrier(Base):
    __tablename__ = "barriers"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    type = Column(Text)
    severity = Column(Integer)
    reported_by = Column(UUID(as_uuid=True), nullable=True)
    image_url = Column(Text, nullable=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    barrier_id = Column(Integer, ForeignKey("barriers.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

"""Database models."""

from sqlalchemy import Column, String, Integer, Numeric, Text, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class Player(Base):
    """Player model."""
    __tablename__ = "players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    team = Column(String(10), nullable=False)
    position = Column(String(10), nullable=False)
    bye_week = Column(Integer)
    age = Column(Integer)
    height = Column(String(10))
    weight = Column(Integer)
    xrefs = Column(JSON, default=dict)  # External IDs (sleeper_id, gsis_id, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)


class Projection(Base):
    """Player projections model."""
    __tablename__ = "projections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    season = Column(Integer, nullable=False)
    source = Column(String(50), nullable=False)
    stats = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

    player = relationship("Player", backref="projections")


class HistoricalStats(Base):
    """Historical player stats model."""
    __tablename__ = "historical_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    season = Column(Integer, nullable=False)
    stats = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

    player = relationship("Player", backref="historical_stats")


class DepthChart(Base):
    """Depth chart model."""
    __tablename__ = "depth_charts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team = Column(String(10), nullable=False)
    position = Column(String(10), nullable=False)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    rank = Column(Integer, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

    player = relationship("Player", backref="depth_positions")


class Injury(Base):
    """Player injury model."""
    __tablename__ = "injuries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    status = Column(String(50), nullable=False)  # Healthy, Questionable, Doubtful, Out
    note = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)

    player = relationship("Player", backref="injuries")


class ADP(Base):
    """Average draft position model."""
    __tablename__ = "adp"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    adp = Column(Numeric(5, 2), nullable=False)
    sample_size = Column(Integer, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

    player = relationship("Player", backref="adp_data")


class DraftPick(Base):
    """Draft pick model."""
    __tablename__ = "draft_picks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    league_id = Column(String(100), nullable=False)
    round = Column(Integer, nullable=False)
    pick = Column(Integer, nullable=False)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"))
    team_slot = Column(String(50))
    ts = Column(DateTime, default=datetime.utcnow)

    player = relationship("Player", backref="draft_picks")


class UserSettings(Base):
    """User settings model."""
    __tablename__ = "user_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(100), nullable=False)
    scoring = Column(JSON, nullable=False)
    exposure_limits = Column(JSON, default=dict)
    strategy = Column(JSON, default=dict)


class League(Base):
    """League model."""
    __tablename__ = "leagues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform = Column(String(50), nullable=False)  # sleeper, espn, yahoo, manual
    settings = Column(JSON, nullable=False)
    scoring = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
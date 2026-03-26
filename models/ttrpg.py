import uuid
import datetime
from typing import Optional, List, Any, Dict
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_gm: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    campaigns: Mapped[List["Campaign"]] = relationship(back_populates="gm")
    players: Mapped[List["Player"]] = relationship(back_populates="user")

class Campaign(Base):
    __tablename__ = "campaigns"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    gm_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(20), default="active") # active/paused/completed

    # Relationships
    gm: Mapped["User"] = relationship(back_populates="campaigns")
    players: Mapped[List["Player"]] = relationship(back_populates="campaign")
    characters: Mapped[List["Character"]] = relationship(back_populates="campaign")
    sessions: Mapped[List["GameSession"]] = relationship(back_populates="campaign")
    maps: Mapped[List["Map"]] = relationship(back_populates="campaign")

class Player(Base):
    __tablename__ = "players"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campaigns.id"), index=True)
    joined_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="players")
    campaign: Mapped["Campaign"] = relationship(back_populates="players")
    characters: Mapped[List["Character"]] = relationship(back_populates="player")

class Character(Base):
    __tablename__ = "characters"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    player_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.id"), index=True)
    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campaigns.id"), index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    race: Mapped[str] = mapped_column(String(50))
    char_class: Mapped[str] = mapped_column("class", String(50))
    level: Mapped[int] = mapped_column(Integer, default=1)

    ability_scores: Mapped[Dict[str, Any]] = mapped_column(JSON)
    hp_max: Mapped[int] = mapped_column(Integer)
    hp_current: Mapped[int] = mapped_column(Integer)
    ac: Mapped[int] = mapped_column(Integer)

    proficiencies: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    inventory: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    spells: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    background: Mapped[Optional[str]] = mapped_column(Text)
    alignment: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    player: Mapped["Player"] = relationship(back_populates="characters")
    campaign: Mapped["Campaign"] = relationship(back_populates="characters")

class GameSession(Base):
    __tablename__ = "game_sessions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campaigns.id"), index=True)
    session_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[Optional[str]] = mapped_column(String(100))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    current_scene: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    campaign: Mapped["Campaign"] = relationship(back_populates="sessions")
    encounters: Mapped[List["CombatEncounter"]] = relationship(back_populates="session")

class CombatEncounter(Base):
    __tablename__ = "combat_encounters"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    game_session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("game_sessions.id"), index=True)
    initiative_order: Mapped[Dict[str, Any]] = mapped_column(JSON)
    current_turn_index: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="active") # active/resolved

    # Relationships
    session: Mapped["GameSession"] = relationship(back_populates="encounters")

class Map(Base):
    __tablename__ = "maps"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campaigns.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    grid_size: Mapped[Optional[str]] = mapped_column(String(50))
    image_url: Mapped[Optional[str]] = mapped_column(String(255))
    tokens: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    # Relationships
    campaign: Mapped["Campaign"] = relationship(back_populates="maps")

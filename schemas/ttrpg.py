from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    email: str
    is_gm: bool = False

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Campaign Schemas ---
class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "active"

class CampaignCreate(CampaignBase):
    gm_id: UUID

class CampaignResponse(CampaignBase):
    id: UUID
    gm_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Player Schemas ---
class PlayerBase(BaseModel):
    is_active: bool = True

class PlayerCreate(PlayerBase):
    user_id: UUID
    campaign_id: UUID

class PlayerResponse(PlayerBase):
    id: UUID
    user_id: UUID
    campaign_id: UUID
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Character Schemas ---
class CharacterBase(BaseModel):
    name: str
    race: str
    char_class: str = Field(alias="class")
    level: int = 1
    ability_scores: Dict[str, Any]
    hp_max: int
    hp_current: int
    ac: int
    proficiencies: Optional[Dict[str, Any]] = None
    inventory: Optional[Dict[str, Any]] = None
    spells: Optional[Dict[str, Any]] = None
    background: Optional[str] = None
    alignment: Optional[str] = None

class CharacterCreate(CharacterBase):
    player_id: UUID
    campaign_id: UUID

class CharacterResponse(CharacterBase):
    id: UUID
    player_id: UUID
    campaign_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# --- GameSession Schemas ---
class GameSessionBase(BaseModel):
    session_number: int
    title: Optional[str] = None
    summary: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    current_scene: Optional[str] = None

class GameSessionCreate(GameSessionBase):
    campaign_id: UUID

class GameSessionResponse(GameSessionBase):
    id: UUID
    campaign_id: UUID

    model_config = ConfigDict(from_attributes=True)

# --- CombatEncounter Schemas ---
class CombatEncounterBase(BaseModel):
    initiative_order: Dict[str, Any]
    current_turn_index: int = 0
    status: str = "active"

class CombatEncounterCreate(CombatEncounterBase):
    game_session_id: UUID

class CombatEncounterResponse(CombatEncounterBase):
    id: UUID
    game_session_id: UUID

    model_config = ConfigDict(from_attributes=True)

# --- Map Schemas ---
class MapBase(BaseModel):
    name: str
    grid_size: Optional[str] = None
    image_url: Optional[str] = None
    tokens: Optional[Dict[str, Any]] = None

class MapCreate(MapBase):
    campaign_id: UUID

class MapResponse(MapBase):
    id: UUID
    campaign_id: UUID

    model_config = ConfigDict(from_attributes=True)

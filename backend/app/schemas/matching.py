"""Pydantic schemas for matching API."""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class MatchPreferences(BaseModel):
    """User preferences for finding collaborators."""

    user_skills: List[str] = Field(
        default=[],
        description="Skills the user already has"
    )
    needed_skills: List[str] = Field(
        default=[],
        description="Skills needed from collaborator"
    )
    project_interests: List[str] = Field(
        default=[],
        description="Project domains of interest"
    )
    preferred_experience: Optional[str] = Field(
        default=None,
        description="Preferred experience level: junior, mid-level, senior, lead"
    )
    weekly_availability: int = Field(
        default=15,
        ge=1,
        le=60,
        description="Desired weekly hours (1-60)"
    )
    timezone: str = Field(
        default="UTC+0",
        description="User's timezone (e.g., UTC+5:30)"
    )
    preferred_team_size: Optional[str] = Field(
        default=None,
        description="Preferred team size: small (2-3), medium (4-6), large (7+)"
    )
    collaboration_style: Optional[str] = Field(
        default=None,
        description="Preferred collaboration style: collaborative, independent, flexible"
    )
    communication_preference: Optional[str] = Field(
        default=None,
        description="Communication preference: async, sync, hybrid"
    )

    @field_validator('preferred_experience')
    @classmethod
    def validate_experience(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in ['junior', 'mid-level', 'senior', 'lead']:
            raise ValueError('Invalid experience level')
        return v or None

    @field_validator('collaboration_style')
    @classmethod
    def validate_collaboration(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in ['collaborative', 'independent', 'flexible']:
            raise ValueError('Invalid collaboration style')
        return v or None

    @field_validator('communication_preference')
    @classmethod
    def validate_communication(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in ['async', 'sync', 'hybrid']:
            raise ValueError('Invalid communication preference')
        return v or None


class ScoreBreakdown(BaseModel):
    """Detailed score breakdown by dimension."""
    skills: float
    interests: float
    availability: float
    collaboration_style: float
    communication: float
    timezone: float
    experience: float
    team_size: float


class MatchResult(BaseModel):
    """A single match result with full details."""
    rank: int
    profile_id: int
    name: str
    professional_title: str
    bio: str
    experience_level: str
    years_of_experience: int
    weekly_availability_hours: int
    timezone: str
    collaboration_style: str
    communication_preference: str
    preferred_team_size: str
    overall_score: float
    score_breakdown: ScoreBreakdown
    matched_skills: List[str]
    complementary_skills: List[str]
    shared_interests: List[str]
    match_reasons: List[str]
    trade_offs: List[str]


class MatchResponse(BaseModel):
    """Complete matching response."""
    total_profiles_evaluated: int
    matches_returned: int
    scoring_weights: dict
    matches: List[MatchResult]

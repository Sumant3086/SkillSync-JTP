"""API endpoints for SkillSync."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.collaborator import CollaboratorProfile, Skill, ProjectInterest
from app.schemas.matching import MatchPreferences, MatchResponse, MatchResult, ScoreBreakdown
from app.services.matching_engine import find_matches, SCORING_WEIGHTS


router = APIRouter()


@router.get("/health")
def health_check():
    """
    Health check endpoint.
    
    Returns service status and database connectivity.
    """
    return {
        "status": "healthy",
        "service": "SkillSync Backend",
        "database": "connected"
    }


@router.get("/options")
def get_options(db: Session = Depends(get_db)):
    """
    Get all available options for form selections.
    
    Returns:
        Dictionary containing all valid options for the preference form
    """
    # Get all skills grouped by category
    skills = db.query(Skill).order_by(Skill.category, Skill.name).all()
    skills_by_category = {}
    for skill in skills:
        if skill.category not in skills_by_category:
            skills_by_category[skill.category] = []
        skills_by_category[skill.category].append(skill.name)
    
    # Get all project interests
    interests = db.query(ProjectInterest).order_by(ProjectInterest.name).all()
    interest_list = [interest.name for interest in interests]
    
    return {
        "skills": [skill.name for skill in skills],
        "skills_by_category": skills_by_category,
        "project_interests": interest_list,
        "experience_levels": ["junior", "mid-level", "senior", "lead"],
        "collaboration_styles": ["collaborative", "independent", "flexible"],
        "communication_preferences": ["async", "sync", "hybrid"],
        "team_sizes": ["small (2-3)", "medium (4-6)", "large (7+)"],
        "timezones": [
            "UTC-12", "UTC-11", "UTC-10", "UTC-9", "UTC-8", "UTC-7",
            "UTC-6", "UTC-5", "UTC-4", "UTC-3", "UTC-2", "UTC-1",
            "UTC+0", "UTC+1", "UTC+2", "UTC+3", "UTC+4", "UTC+5",
            "UTC+5:30", "UTC+6", "UTC+7", "UTC+8", "UTC+9", "UTC+10",
            "UTC+11", "UTC+12"
        ]
    }



@router.get("/profiles")
def get_profiles(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get all collaborator profiles.
    
    Args:
        limit: Maximum number of profiles to return
        db: Database session
    
    Returns:
        List of collaborator profiles
    """
    profiles = db.query(CollaboratorProfile).limit(limit).all()
    
    result = []
    for profile in profiles:
        result.append({
            "id": profile.id,
            "name": profile.name,
            "professional_title": profile.professional_title,
            "bio": profile.bio,
            "experience_level": profile.experience_level,
            "years_of_experience": profile.years_of_experience,
            "weekly_availability_hours": profile.weekly_availability_hours,
            "timezone": profile.timezone,
            "collaboration_style": profile.collaboration_style,
            "communication_preference": profile.communication_preference,
            "preferred_team_size": profile.preferred_team_size,
            "skills": [skill.name for skill in profile.skills],
            "interests": [interest.name for interest in profile.interests]
        })
    
    return result


@router.get("/profiles/{profile_id}")
def get_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a single collaborator profile by ID.
    
    Args:
        profile_id: Profile ID
        db: Database session
    
    Returns:
        Profile details
    """
    profile = db.query(CollaboratorProfile).filter(
        CollaboratorProfile.id == profile_id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "id": profile.id,
        "name": profile.name,
        "professional_title": profile.professional_title,
        "bio": profile.bio,
        "experience_level": profile.experience_level,
        "years_of_experience": profile.years_of_experience,
        "weekly_availability_hours": profile.weekly_availability_hours,
        "timezone": profile.timezone,
        "collaboration_style": profile.collaboration_style,
        "communication_preference": profile.communication_preference,
        "preferred_team_size": profile.preferred_team_size,
        "skills": [skill.name for skill in profile.skills],
        "interests": [interest.name for interest in profile.interests]
    }



@router.post("/matches", response_model=MatchResponse)
def find_collaborator_matches(
    preferences: MatchPreferences,
    db: Session = Depends(get_db)
):
    """
    Find matching collaborators based on user preferences.
    
    This endpoint evaluates all collaborator profiles against the user's
    preferences and returns ranked matches with detailed scoring breakdowns
    and explanations.
    
    Args:
        preferences: User's matching preferences
        db: Database session
    
    Returns:
        Ranked list of matching collaborators with scores and explanations
    """
    try:
        # Get total profile count
        total_profiles = db.query(CollaboratorProfile).count()
        
        # Find matches using the matching engine
        matches = find_matches(
            db=db,
            user_skills=preferences.user_skills,
            needed_skills=preferences.needed_skills,
            user_interests=preferences.project_interests,
            preferred_experience=preferences.preferred_experience or "",
            weekly_availability=preferences.weekly_availability,
            user_timezone=preferences.timezone,
            preferred_team_size=preferences.preferred_team_size or "",
            collaboration_style=preferences.collaboration_style or "",
            communication_preference=preferences.communication_preference or "",
            limit=10
        )
        
        # Convert to response schema
        match_results = []
        for match in matches:
            match_results.append(MatchResult(
                rank=match["rank"],
                profile_id=match["profile_id"],
                name=match["name"],
                professional_title=match["professional_title"],
                bio=match["bio"],
                experience_level=match["experience_level"],
                years_of_experience=match["years_of_experience"],
                weekly_availability_hours=match["weekly_availability_hours"],
                timezone=match["timezone"],
                collaboration_style=match["collaboration_style"],
                communication_preference=match["communication_preference"],
                preferred_team_size=match["preferred_team_size"],
                overall_score=match["overall_score"],
                score_breakdown=ScoreBreakdown(**match["score_breakdown"]),
                matched_skills=match["matched_skills"],
                complementary_skills=match["complementary_skills"],
                shared_interests=match["shared_interests"],
                match_reasons=match["match_reasons"],
                trade_offs=match["trade_offs"]
            ))
        
        return MatchResponse(
            total_profiles_evaluated=total_profiles,
            matches_returned=len(match_results),
            scoring_weights=SCORING_WEIGHTS,
            matches=match_results
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error finding matches: {str(e)}"
        )

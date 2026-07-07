"""API endpoints for SkillSync."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.collaborator import CollaboratorProfile, Skill, ProjectInterest
from app.schemas.matching import MatchPreferences, MatchResponse, MatchResult, ScoreBreakdown
from app.services.matching_engine import find_matches, SCORING_WEIGHTS


router = APIRouter()


@router.get("/health")
def health_check():
    """Health check endpoint — returns service status."""
    return {
        "status": "healthy",
        "service": "SkillSync Backend",
        "database": "connected",
    }


@router.get("/options")
def get_options(db: Session = Depends(get_db)):
    """
    Return all valid options for the preference form.

    Groups skills by category so the frontend can render category filters.
    """
    skills = db.query(Skill).order_by(Skill.category, Skill.name).all()

    skills_by_category: dict[str, list[str]] = {}
    for skill in skills:
        skills_by_category.setdefault(skill.category, []).append(skill.name)

    interests = db.query(ProjectInterest).order_by(ProjectInterest.name).all()

    return {
        "skills": [s.name for s in skills],
        "skills_by_category": skills_by_category,
        "project_interests": [i.name for i in interests],
        "experience_levels": ["junior", "mid-level", "senior", "lead"],
        "collaboration_styles": ["collaborative", "independent", "flexible"],
        "communication_preferences": ["async", "sync", "hybrid"],
        "team_sizes": ["small (2-3)", "medium (4-6)", "large (7+)"],
        "timezones": [
            "UTC-12", "UTC-11", "UTC-10", "UTC-9", "UTC-8", "UTC-7",
            "UTC-6", "UTC-5", "UTC-4", "UTC-3", "UTC-2", "UTC-1",
            "UTC+0", "UTC+1", "UTC+2", "UTC+3", "UTC+4", "UTC+5",
            "UTC+5:30", "UTC+6", "UTC+7", "UTC+8", "UTC+9", "UTC+10",
            "UTC+11", "UTC+12",
        ],
    }


@router.get("/profiles")
def get_profiles(limit: int = 50, db: Session = Depends(get_db)):
    """Return a list of all collaborator profiles (for inspection / admin)."""
    profiles = db.query(CollaboratorProfile).limit(limit).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "professional_title": p.professional_title,
            "bio": p.bio,
            "experience_level": p.experience_level,
            "years_of_experience": p.years_of_experience,
            "weekly_availability_hours": p.weekly_availability_hours,
            "timezone": p.timezone,
            "collaboration_style": p.collaboration_style,
            "communication_preference": p.communication_preference,
            "preferred_team_size": p.preferred_team_size,
            "skills": [s.name for s in p.skills],
            "interests": [i.name for i in p.interests],
        }
        for p in profiles
    ]


@router.get("/profiles/{profile_id}")
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    """Return a single collaborator profile by ID."""
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
        "skills": [s.name for s in profile.skills],
        "interests": [i.name for i in profile.interests],
    }


@router.post("/matches", response_model=MatchResponse)
def find_collaborator_matches(
    preferences: MatchPreferences,
    db: Session = Depends(get_db),
):
    """
    Find and rank collaborator matches against the user's preferences.

    The matching engine evaluates all profiles across 7 weighted dimensions
    (skills, interests, availability, collaboration style, communication,
    timezone, experience level) and returns the top 10 ranked results with
    score breakdowns and human-readable explanations.
    """
    try:
        total_profiles = db.query(CollaboratorProfile).count()

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
            limit=10,
        )

        match_results = [
            MatchResult(
                rank=m["rank"],
                profile_id=m["profile_id"],
                name=m["name"],
                professional_title=m["professional_title"],
                bio=m["bio"],
                experience_level=m["experience_level"],
                years_of_experience=m["years_of_experience"],
                weekly_availability_hours=m["weekly_availability_hours"],
                timezone=m["timezone"],
                collaboration_style=m["collaboration_style"],
                communication_preference=m["communication_preference"],
                preferred_team_size=m["preferred_team_size"],
                overall_score=m["overall_score"],
                score_breakdown=ScoreBreakdown(**m["score_breakdown"]),
                matched_skills=m["matched_skills"],
                complementary_skills=m["complementary_skills"],
                shared_interests=m["shared_interests"],
                match_reasons=m["match_reasons"],
                trade_offs=m["trade_offs"],
            )
            for m in matches
        ]

        return MatchResponse(
            total_profiles_evaluated=total_profiles,
            matches_returned=len(match_results),
            scoring_weights=SCORING_WEIGHTS,
            matches=match_results,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error finding matches: {str(exc)}",
        ) from exc

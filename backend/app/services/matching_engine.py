"""
Explainable Collaborator Matching Engine.

This module implements a deterministic, weighted scoring algorithm that evaluates
collaborator compatibility across multiple dimensions without using machine learning.
"""
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.collaborator import CollaboratorProfile, profile_skills


# Scoring weights (must total 100%)
SCORING_WEIGHTS = {
    "skills": 0.35,           # 35% - Required and complementary skills
    "interests": 0.20,        # 20% - Shared project interests
    "availability": 0.15,     # 15% - Weekly availability compatibility
    "collaboration_style": 0.10,  # 10% - Working style compatibility
    "communication": 0.10,    # 10% - Communication preference compatibility
    "timezone": 0.05,         # 5% - Timezone compatibility
    "experience": 0.05        # 5% - Experience level compatibility
}


def calculate_skill_score(
    user_skills: List[str],
    needed_skills: List[str],
    profile_skills_dict: Dict[str, str],
    profile: CollaboratorProfile
) -> Tuple[float, List[str], List[str]]:
    """
    Calculate skills compatibility score.
    
    Evaluates:
    - Coverage of needed skills (primary factor)
    - Complementary skills the user doesn't have
    - Avoids rewarding irrelevant skill quantity
    
    Args:
        user_skills: Skills the user already has
        needed_skills: Skills the user needs from collaborator
        profile_skills_dict: Profile's skills with proficiency levels
        profile: The collaborator profile
    
    Returns:
        Tuple of (score, matched_skills, complementary_skills)
    """
    matched_skills = []
    complementary_skills = []
    
    profile_skill_names = set(profile_skills_dict.keys())
    user_skill_set = set(user_skills)
    needed_skill_set = set(needed_skills)
    
    # Calculate needed skills coverage (70% of skills score)
    if needed_skill_set:
        for skill in needed_skill_set:
            if skill in profile_skill_names:
                matched_skills.append(skill)
        needed_coverage = len(matched_skills) / len(needed_skill_set)
    else:
        needed_coverage = 0.5  # Neutral score if no needs specified
    
    # Calculate complementary skills (30% of skills score)
    # Skills the profile has that the user doesn't have (and didn't explicitly request)
    for skill in profile_skill_names:
        if skill not in user_skill_set and skill not in needed_skill_set:
            complementary_skills.append(skill)
    
    # Bonus for complementary skills, but capped to avoid overwhelming the score
    complementary_bonus = min(len(complementary_skills) * 0.05, 0.3)
    
    # Combine: 70% needed coverage + 30% complementary value
    skill_score = (needed_coverage * 0.7 + complementary_bonus) * 100
    
    # Cap at 100
    skill_score = min(skill_score, 100.0)
    
    return skill_score, matched_skills, complementary_skills[:5]  # Limit complementary list


def calculate_interest_score(
    user_interests: List[str],
    profile_interests: List[str]
) -> Tuple[float, List[str]]:
    """
    Calculate shared project interests score using Jaccard similarity.
    
    Args:
        user_interests: User's project interests
        profile_interests: Profile's project interests
    
    Returns:
        Tuple of (score, shared_interests)
    """
    if not user_interests or not profile_interests:
        return 50.0, []  # Neutral score if no interests specified
    
    user_set = set(user_interests)
    profile_set = set(profile_interests)
    
    intersection = user_set & profile_set
    union = user_set | profile_set
    
    if not union:
        return 50.0, []
    
    # Jaccard similarity: |intersection| / |union|
    jaccard = len(intersection) / len(union)
    score = jaccard * 100
    
    return score, list(intersection)



def calculate_availability_score(
    user_availability: int,
    profile_availability: int
) -> float:
    """
    Calculate availability compatibility score.
    
    Compares user's desired hours with profile's available hours.
    Perfect match when profile has >= user's needs.
    
    Args:
        user_availability: User's desired weekly hours
        profile_availability: Profile's available weekly hours
    
    Returns:
        Compatibility score (0-100)
    """
    if user_availability <= 0:
        return 50.0  # Neutral if no preference
    
    if profile_availability >= user_availability:
        # Profile has enough availability
        # Slight penalty for excessive availability (might indicate overcommitment)
        excess_ratio = profile_availability / user_availability
        if excess_ratio <= 1.5:
            return 100.0
        else:
            # Gradually reduce score for excessive availability
            return max(100.0 - (excess_ratio - 1.5) * 10, 70.0)
    else:
        # Profile has less than needed
        # Linear penalty based on shortage
        coverage = profile_availability / user_availability
        return coverage * 100


def calculate_timezone_score(user_timezone: str, profile_timezone: str) -> float:
    """
    Calculate timezone compatibility score based on UTC offset distance.
    
    Args:
        user_timezone: User's timezone (e.g., "UTC+5:30")
        profile_timezone: Profile's timezone
    
    Returns:
        Compatibility score (0-100)
    """
    def parse_timezone(tz: str) -> float:
        """Parse timezone string to numeric offset."""
        tz = tz.replace("UTC", "").strip()
        if not tz or tz == "+0":
            return 0.0
        
        # Handle formats like "+5:30" or "-8"
        if ":" in tz:
            parts = tz.split(":")
            hours = float(parts[0])
            minutes = float(parts[1]) / 60
            return hours + (minutes if hours >= 0 else -minutes)
        else:
            return float(tz)
    
    try:
        user_offset = parse_timezone(user_timezone)
        profile_offset = parse_timezone(profile_timezone)
        
        # Calculate absolute difference in hours
        diff = abs(user_offset - profile_offset)
        
        # Score based on timezone distance
        # 0-2 hours: 100 (excellent)
        # 2-4 hours: 90 (very good)
        # 4-6 hours: 75 (good)
        # 6-8 hours: 60 (moderate)
        # 8-10 hours: 45 (challenging)
        # 10+ hours: 30 (difficult)
        if diff <= 2:
            return 100.0
        elif diff <= 4:
            return 90.0
        elif diff <= 6:
            return 75.0
        elif diff <= 8:
            return 60.0
        elif diff <= 10:
            return 45.0
        else:
            return 30.0
    except:
        return 50.0  # Neutral on parse error



def calculate_experience_score(
    user_preference: str,
    profile_experience: str
) -> float:
    """
    Calculate experience level compatibility score.
    
    Experience levels: junior, mid-level, senior, lead
    
    Args:
        user_preference: User's preferred experience level
        profile_experience: Profile's experience level
    
    Returns:
        Compatibility score (0-100)
    """
    if not user_preference:
        return 50.0  # Neutral if no preference
    
    experience_levels = ["junior", "mid-level", "senior", "lead"]
    
    try:
        user_idx = experience_levels.index(user_preference)
        profile_idx = experience_levels.index(profile_experience)
        
        # Exact match: 100
        if user_idx == profile_idx:
            return 100.0
        
        # Adjacent level: 80
        if abs(user_idx - profile_idx) == 1:
            return 80.0
        
        # Two levels apart: 50
        if abs(user_idx - profile_idx) == 2:
            return 50.0
        
        # Three levels apart: 30
        return 30.0
    except ValueError:
        return 50.0


def calculate_collaboration_score(
    user_style: str,
    profile_style: str
) -> float:
    """
    Calculate collaboration style compatibility score.
    
    Styles: collaborative, independent, flexible
    
    Args:
        user_style: User's preferred collaboration style
        profile_style: Profile's collaboration style
    
    Returns:
        Compatibility score (0-100)
    """
    if not user_style:
        return 50.0
    
    # Compatibility matrix
    compatibility = {
        ("collaborative", "collaborative"): 100,
        ("collaborative", "flexible"): 90,
        ("collaborative", "independent"): 60,
        ("independent", "independent"): 100,
        ("independent", "flexible"): 90,
        ("independent", "collaborative"): 60,
        ("flexible", "collaborative"): 90,
        ("flexible", "independent"): 90,
        ("flexible", "flexible"): 100,
    }
    
    return float(compatibility.get((user_style, profile_style), 50))


def calculate_communication_score(
    user_comm: str,
    profile_comm: str
) -> float:
    """
    Calculate communication preference compatibility score.
    
    Preferences: async, sync, hybrid
    
    Args:
        user_comm: User's communication preference
        profile_comm: Profile's communication preference
    
    Returns:
        Compatibility score (0-100)
    """
    if not user_comm:
        return 50.0
    
    # Compatibility matrix
    compatibility = {
        ("async", "async"): 100,
        ("async", "hybrid"): 90,
        ("async", "sync"): 50,
        ("sync", "sync"): 100,
        ("sync", "hybrid"): 90,
        ("sync", "async"): 50,
        ("hybrid", "async"): 90,
        ("hybrid", "sync"): 90,
        ("hybrid", "hybrid"): 100,
    }
    
    return float(compatibility.get((user_comm, profile_comm), 50))



def generate_match_reasons(
    skill_score: float,
    interest_score: float,
    availability_score: float,
    matched_skills: List[str],
    shared_interests: List[str],
    complementary_skills: List[str]
) -> List[str]:
    """
    Generate human-readable match reasons based on scores.
    
    Returns:
        List of positive match reasons
    """
    reasons = []
    
    if skill_score >= 80:
        if matched_skills:
            reasons.append(f"Strong match on {len(matched_skills)} needed skills")
        if complementary_skills:
            reasons.append(f"Brings {len(complementary_skills)} complementary skills")
    
    if interest_score >= 70:
        if shared_interests:
            reasons.append(f"Shares {len(shared_interests)} project interests")
    
    if availability_score >= 90:
        reasons.append("Excellent availability alignment")
    elif availability_score >= 70:
        reasons.append("Good availability compatibility")
    
    return reasons if reasons else ["Moderate overall compatibility"]


def generate_trade_offs(
    skill_score: float,
    interest_score: float,
    availability_score: float,
    timezone_score: float,
    experience_score: float,
    collaboration_score: float,
    communication_score: float
) -> List[str]:
    """
    Generate honest trade-off assessments.
    
    Returns:
        List of potential compatibility concerns
    """
    trade_offs = []
    
    if skill_score < 50:
        trade_offs.append("Limited coverage of needed skills")
    
    if interest_score < 40:
        trade_offs.append("Few shared project interests")
    
    if availability_score < 50:
        trade_offs.append("Availability may be lower than needed")
    
    if timezone_score < 50:
        trade_offs.append("Significant timezone difference")
    
    if experience_score < 50:
        trade_offs.append("Experience level difference may require adjustment")
    
    if collaboration_score < 60:
        trade_offs.append("Different collaboration style preferences")
    
    if communication_score < 60:
        trade_offs.append("Different communication preferences")
    
    return trade_offs



def find_matches(
    db: Session,
    user_skills: List[str],
    needed_skills: List[str],
    user_interests: List[str],
    preferred_experience: str,
    weekly_availability: int,
    user_timezone: str,
    preferred_team_size: str,
    collaboration_style: str,
    communication_preference: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Find and rank collaborator matches based on user preferences.
    
    This is the main matching engine function that:
    1. Retrieves all eligible profiles
    2. Calculates compatibility scores across all dimensions
    3. Generates explanations and trade-offs
    4. Ranks results deterministically
    
    Args:
        db: Database session
        user_skills: Skills the user already has
        needed_skills: Skills needed from collaborator
        user_interests: User's project interests
        preferred_experience: Preferred experience level
        weekly_availability: Desired weekly hours
        user_timezone: User's timezone
        preferred_team_size: Preferred team size
        collaboration_style: Preferred collaboration style
        communication_preference: Preferred communication style
        limit: Maximum number of results to return
    
    Returns:
        List of ranked match dictionaries with scores and explanations
    """
    # Get all profiles with their skills and interests
    profiles = db.query(CollaboratorProfile).all()
    
    matches = []
    
    for profile in profiles:
        # Get profile skills with proficiency
        profile_skills_result = db.execute(
            profile_skills.select().where(profile_skills.c.profile_id == profile.id)
        ).fetchall()
        
        profile_skills_dict = {
            row.skill_id: row.proficiency_level for row in profile_skills_result
        }
        
        # Convert skill IDs to names
        profile_skill_names = {}
        for skill in profile.skills:
            if skill.id in profile_skills_dict:
                profile_skill_names[skill.name] = profile_skills_dict[skill.id]
        
        profile_interest_names = [interest.name for interest in profile.interests]
        
        # Calculate individual dimension scores
        skill_score, matched_skills, complementary_skills = calculate_skill_score(
            user_skills, needed_skills, profile_skill_names, profile
        )
        
        interest_score, shared_interests = calculate_interest_score(
            user_interests, profile_interest_names
        )
        
        availability_score = calculate_availability_score(
            weekly_availability, profile.weekly_availability_hours
        )
        
        timezone_score = calculate_timezone_score(user_timezone, profile.timezone)
        
        experience_score = calculate_experience_score(
            preferred_experience, profile.experience_level
        )
        
        collaboration_score = calculate_collaboration_score(
            collaboration_style, profile.collaboration_style
        )
        
        communication_score = calculate_communication_score(
            communication_preference, profile.communication_preference
        )
        
        # Calculate weighted overall score
        overall_score = (
            skill_score * SCORING_WEIGHTS["skills"] +
            interest_score * SCORING_WEIGHTS["interests"] +
            availability_score * SCORING_WEIGHTS["availability"] +
            collaboration_score * SCORING_WEIGHTS["collaboration_style"] +
            communication_score * SCORING_WEIGHTS["communication"] +
            timezone_score * SCORING_WEIGHTS["timezone"] +
            experience_score * SCORING_WEIGHTS["experience"]
        )
        
        # Round to 1 decimal place
        overall_score = round(overall_score, 1)
        
        # Generate explanations
        match_reasons = generate_match_reasons(
            skill_score, interest_score, availability_score,
            matched_skills, shared_interests, complementary_skills
        )
        
        trade_offs = generate_trade_offs(
            skill_score, interest_score, availability_score,
            timezone_score, experience_score, collaboration_score,
            communication_score
        )
        
        # Build match result
        match = {
            "profile_id": profile.id,
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
            "overall_score": overall_score,
            "score_breakdown": {
                "skills": round(skill_score, 1),
                "interests": round(interest_score, 1),
                "availability": round(availability_score, 1),
                "collaboration_style": round(collaboration_score, 1),
                "communication": round(communication_score, 1),
                "timezone": round(timezone_score, 1),
                "experience": round(experience_score, 1)
            },
            "matched_skills": matched_skills,
            "complementary_skills": complementary_skills,
            "shared_interests": shared_interests,
            "match_reasons": match_reasons,
            "trade_offs": trade_offs
        }
        
        matches.append(match)
    
    # Sort matches deterministically
    # Primary: overall_score descending
    # Secondary: skill_score descending
    # Tertiary: profile_id ascending (stable tie-breaker)
    matches.sort(
        key=lambda x: (-x["overall_score"], -x["score_breakdown"]["skills"], x["profile_id"])
    )
    
    # Assign ranks
    for idx, match in enumerate(matches[:limit], start=1):
        match["rank"] = idx
    
    return matches[:limit]

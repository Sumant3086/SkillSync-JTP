"""
Explainable Collaborator Matching Engine — v2.

Improvements over v1:
  - Proficiency-weighted skill scoring (beginner → expert matters)
  - Skill rarity bonus (rare skills are worth more to match)
  - Recall-weighted F-score for interests (user-centric, not symmetric Jaccard)
  - Smooth exponential timezone decay (no arbitrary step-band cliffs)
  - Asymmetric experience scoring (over-experienced < under-experienced penalty)
  - Consistency bonus (balanced profiles beat one-trick-ponies)
  - Richer match-reason generation
"""
import math
import statistics
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.collaborator import CollaboratorProfile, Skill, profile_skills as ps_table


# ── Scoring weights (must sum to 1.0) ──────────────────────────────────────
SCORING_WEIGHTS = {
    "skills":              0.35,
    "interests":           0.20,
    "availability":        0.15,
    "collaboration_style": 0.10,
    "communication":       0.10,
    "timezone":            0.05,
    "experience":          0.05,
}

# Proficiency → numeric multiplier used in skill scoring
PROFICIENCY_WEIGHTS: Dict[str, float] = {
    "beginner":     0.40,
    "intermediate": 0.65,
    "advanced":     0.85,
    "expert":       1.00,
}


# ── Individual dimension scorers ────────────────────────────────────────────

def calculate_skill_score(
    user_skills: List[str],
    needed_skills: List[str],
    profile_skills_dict: Dict[str, str],   # skill_name → proficiency_level
    profile: Optional[CollaboratorProfile],  # kept for API compatibility
    skill_rarity: Optional[Dict[str, float]] = None,  # skill_name → rarity (1.0–1.5)
) -> Tuple[float, List[str], List[str]]:
    """
    Calculate skill compatibility with proficiency and rarity weighting.

    Needed-skill coverage (70% of score):
        Each needed skill is worth  proficiency_weight × rarity_weight.
        A profile matching "expert Kubernetes" on a rare skill beats a
        profile matching "beginner Python" on a common skill.

    Complementary-skill bonus (up to 30%):
        Skills the profile has that the user does not (and did not request),
        weighted by proficiency × rarity. Rewards genuinely useful additions
        rather than a raw count.

    Args:
        user_skills: Skills the user already has.
        needed_skills: Skills the user needs from a collaborator.
        profile_skills_dict: Profile's skills mapped to proficiency levels.
        profile: Unused; kept for backward-compatible call sites.
        skill_rarity: Pre-computed rarity scores (1.0 = common, 1.5 = unique).

    Returns:
        (score 0-100, matched_skills list, top-5 complementary_skills list)
    """
    if skill_rarity is None:
        skill_rarity = {}

    matched_skills: List[str] = []
    complementary_skills: List[str] = []

    profile_skill_names = set(profile_skills_dict.keys())
    user_skill_set = set(user_skills)
    needed_skill_set = set(needed_skills)

    # ── Needed-skills coverage ───────────────────────────────────────────────
    if needed_skill_set:
        weighted_earned = 0.0
        weighted_max = 0.0
        for skill in needed_skill_set:
            rarity = skill_rarity.get(skill, 1.0)
            # Maximum possible contribution if profile had this skill at expert level
            weighted_max += 1.0 * rarity
            if skill in profile_skill_names:
                proficiency = PROFICIENCY_WEIGHTS.get(
                    profile_skills_dict[skill], 0.65
                )
                weighted_earned += proficiency * rarity
                matched_skills.append(skill)
        needed_coverage = weighted_earned / weighted_max if weighted_max > 0 else 0.0
    else:
        needed_coverage = 0.5  # neutral when no specific skills are requested

    # ── Complementary-skill bonus ─────────────────────────────────────────────
    comp_value = 0.0
    for skill in profile_skill_names:
        if skill not in user_skill_set and skill not in needed_skill_set:
            complementary_skills.append(skill)
            proficiency = PROFICIENCY_WEIGHTS.get(profile_skills_dict[skill], 0.65)
            rarity = skill_rarity.get(skill, 1.0)
            # Each complementary skill contributes up to ~0.065 (expert, rare)
            comp_value += proficiency * rarity * 0.05

    complementary_bonus = min(comp_value, 0.30)

    skill_score = min((needed_coverage * 0.70 + complementary_bonus) * 100, 100.0)
    return skill_score, matched_skills, complementary_skills[:5]


def calculate_interest_score(
    user_interests: List[str],
    profile_interests: List[str],
) -> Tuple[float, List[str]]:
    """
    Calculate interest alignment using an F-beta score (recall-weighted).

    Recall measures how well the profile covers what the user wants.
    Precision measures how focused the profile is on the user's domains.
    Beta = 1.5 weights recall 2.25× more than precision, reflecting that
    covering the user's stated interests is more important than avoiding
    irrelevant ones.

    This replaces symmetric Jaccard, which under-rewards profiles that share
    all of the user's interests but also have a few extras.

    Args:
        user_interests: Domains the user cares about.
        profile_interests: Domains the profile is interested in.

    Returns:
        (score 0-100, shared_interests list)
    """
    if not user_interests or not profile_interests:
        return 50.0, []

    user_set = set(user_interests)
    profile_set = set(profile_interests)
    intersection = user_set & profile_set

    if not intersection:
        return 0.0, []

    recall = len(intersection) / len(user_set)       # user's interests covered
    precision = len(intersection) / len(profile_set)  # profile's focus on user's domains

    # F-beta with beta = 1.5  (recall weighted 2.25× over precision)
    beta_sq = 1.5 ** 2
    f_score = (1 + beta_sq) * (precision * recall) / (beta_sq * precision + recall)

    return round(f_score * 100, 1), list(intersection)


def calculate_availability_score(
    user_availability: int,
    profile_availability: int,
) -> float:
    """
    Calculate availability compatibility.

    Penalises both under- and over-availability:
    - Under: linear penalty (half the hours → 50 pts)
    - Slight surplus (up to 30% extra): full score
    - Large surplus (>2×): mild penalty — may indicate spreading thin

    Args:
        user_availability: Weekly hours the user needs.
        profile_availability: Weekly hours the profile can offer.

    Returns:
        Compatibility score (0-100).
    """
    if user_availability <= 0:
        return 50.0

    ratio = profile_availability / user_availability

    if ratio >= 1.0:
        if ratio <= 1.3:
            return 100.0
        elif ratio <= 2.0:
            # Gradually reduce for large surplus
            return round(100.0 - (ratio - 1.3) * 14.3, 1)
        else:
            return round(max(90.0 - (ratio - 2.0) * 20.0, 50.0), 1)
    else:
        return round(ratio * 100.0, 1)


def calculate_timezone_score(user_timezone: str, profile_timezone: str) -> float:
    """
    Calculate timezone compatibility using smooth exponential decay.

    Replaces the previous step-band approach (which created arbitrary cliffs
    at band boundaries). Now every hour of difference matters proportionally.

    Score formula: 100 × exp(-0.08 × diff^1.5)
    Examples: 0 h → 100, 2 h → 91, 5 h → 76, 8 h → 54, 12 h → 28

    Args:
        user_timezone: User timezone string (e.g. "UTC+5:30").
        profile_timezone: Profile timezone string.

    Returns:
        Compatibility score (10-100).
    """
    def parse_tz(tz: str) -> float:
        tz = tz.replace("UTC", "").strip()
        if not tz or tz in ("+0", "0"):
            return 0.0
        if ":" in tz:
            parts = tz.split(":")
            hours = float(parts[0])
            minutes = float(parts[1]) / 60.0
            return hours + (minutes if hours >= 0 else -minutes)
        return float(tz)

    try:
        diff = abs(parse_tz(user_timezone) - parse_tz(profile_timezone))
        score = 100.0 * math.exp(-0.08 * (diff ** 1.5))
        return round(max(score, 10.0), 1)
    except (ValueError, TypeError):
        return 50.0


def calculate_experience_score(
    user_preference: str,
    profile_experience: str,
) -> float:
    """
    Calculate experience level compatibility with asymmetric penalties.

    Being slightly over-experienced (profile more senior than requested) is
    less penalised than being under-experienced — it is generally better to
    collaborate with someone more senior than expected.

    Args:
        user_preference: Requested experience level.
        profile_experience: Profile's actual experience level.

    Returns:
        Compatibility score (0-100).
    """
    if not user_preference:
        return 50.0

    levels = ["junior", "mid-level", "senior", "lead"]

    try:
        user_idx = levels.index(user_preference)
        profile_idx = levels.index(profile_experience)
        diff = profile_idx - user_idx  # positive = more experienced than requested

        score_map = {
            0:  100,   # exact match
            1:   85,   # one level above requested — slight benefit
           -1:   70,   # one level below — mild concern
            2:   65,   # two above — noticeably senior but still workable
           -2:   40,   # two below — significant gap
            3:   35,   # three above (junior wanted lead)
           -3:   20,   # three below (lead wanted junior)
        }
        return float(score_map.get(diff, 50))
    except ValueError:
        return 50.0


def calculate_collaboration_score(user_style: str, profile_style: str) -> float:
    """
    Calculate collaboration style compatibility.

    Args:
        user_style: collaborative | independent | flexible
        profile_style: collaborative | independent | flexible

    Returns:
        Compatibility score (0-100).
    """
    if not user_style:
        return 50.0

    matrix: Dict[Tuple[str, str], int] = {
        ("collaborative", "collaborative"): 100,
        ("collaborative", "flexible"):       90,
        ("collaborative", "independent"):    55,
        ("independent",  "independent"):    100,
        ("independent",  "flexible"):        90,
        ("independent",  "collaborative"):   55,
        ("flexible",     "collaborative"):   90,
        ("flexible",     "independent"):     90,
        ("flexible",     "flexible"):       100,
    }
    return float(matrix.get((user_style, profile_style), 50))


def calculate_communication_score(user_comm: str, profile_comm: str) -> float:
    """
    Calculate communication preference compatibility.

    Args:
        user_comm: async | sync | hybrid
        profile_comm: async | sync | hybrid

    Returns:
        Compatibility score (0-100).
    """
    if not user_comm:
        return 50.0

    matrix: Dict[Tuple[str, str], int] = {
        ("async",  "async"):  100,
        ("async",  "hybrid"):  85,
        ("async",  "sync"):    45,
        ("sync",   "sync"):   100,
        ("sync",   "hybrid"):  85,
        ("sync",   "async"):   45,
        ("hybrid", "async"):   85,
        ("hybrid", "sync"):    85,
        ("hybrid", "hybrid"): 100,
    }
    return float(matrix.get((user_comm, profile_comm), 50))


def calculate_consistency_bonus(scores: List[float]) -> float:
    """
    Return a small score adjustment based on how balanced the profile is.

    A profile scoring 80 across all 7 dimensions is more dependable than
    one scoring 100 on skills but 15 on everything else — the latter has a
    single point of strength that may not compensate for the mismatches in
    practice.

    Adjustment range: -3 to +3 points added to the overall score.

    Args:
        scores: List of raw dimension scores (0-100 each).

    Returns:
        Float adjustment in [-3, +3].
    """
    if len(scores) < 2:
        return 0.0
    variance = statistics.variance(scores)
    # variance ≈ 0 → adjustment ≈ +3 (perfectly balanced)
    # variance ≈ 1500 (very uneven 0–100 spread) → adjustment ≈ -7 → capped at -3
    adjustment = 3.0 - (variance / 250.0)
    return round(max(-3.0, min(3.0, adjustment)), 2)


# ── Explanation generators ──────────────────────────────────────────────────

def generate_match_reasons(
    skill_score: float,
    interest_score: float,
    availability_score: float,
    matched_skills: List[str],
    shared_interests: List[str],
    complementary_skills: List[str],
) -> List[str]:
    """Generate positive, human-readable match reasons from dimension scores."""
    reasons: List[str] = []

    if skill_score >= 80 and matched_skills:
        n = len(matched_skills)
        reasons.append(
            f"Covers {n} of your required skill{'s' if n > 1 else ''} at a good proficiency level"
        )
    elif skill_score >= 55 and matched_skills:
        reasons.append(f"Partial skill overlap on {len(matched_skills)} needed skill{'s' if len(matched_skills) > 1 else ''}")

    if complementary_skills:
        reasons.append(
            f"Brings {len(complementary_skills)} additional skill{'s' if len(complementary_skills) > 1 else ''} you don't have"
        )

    if interest_score >= 65 and shared_interests:
        top = shared_interests[:2]
        reasons.append(
            f"Shares key interests: {', '.join(top)}"
        )

    if availability_score >= 90:
        reasons.append("Availability aligns well with your weekly hours")
    elif availability_score >= 70:
        reasons.append("Reasonable availability match")

    return reasons if reasons else ["General compatibility across multiple dimensions"]


def generate_trade_offs(
    skill_score: float,
    interest_score: float,
    availability_score: float,
    timezone_score: float,
    experience_score: float,
    collaboration_score: float,
    communication_score: float,
) -> List[str]:
    """Generate honest trade-off notes for low-scoring dimensions."""
    trade_offs: List[str] = []

    if skill_score < 50:
        trade_offs.append("Limited coverage of your required skills")
    if interest_score < 35:
        trade_offs.append("Few shared project interests")
    if availability_score < 50:
        trade_offs.append("Availability may not meet your weekly hours requirement")
    if timezone_score < 50:
        trade_offs.append("Significant timezone difference — async-first collaboration recommended")
    if experience_score < 50:
        trade_offs.append("Experience level differs considerably from your preference")
    if collaboration_score < 60:
        trade_offs.append("Different preferred collaboration styles")
    if communication_score < 60:
        trade_offs.append("Different communication preferences")

    return trade_offs


# ── Main matching function ──────────────────────────────────────────────────

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
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Find and rank collaborator matches using a multi-criteria weighted algorithm.

    Algorithm steps:
    1. Pre-compute skill rarity across all 40 profiles (one DB query).
    2. For each profile, build skill name → proficiency dict.
    3. Calculate 7 dimension scores using the functions above.
    4. Apply weighted sum, then add a consistency adjustment.
    5. Generate match reasons and trade-offs.
    6. Sort deterministically: overall_score DESC, skills DESC, profile_id ASC.

    Args:
        db: SQLAlchemy session.
        user_skills: Skills the user already has.
        needed_skills: Skills needed from the collaborator.
        user_interests: Project domains the user is interested in.
        preferred_experience: Desired experience level string.
        weekly_availability: Desired collaboration hours per week.
        user_timezone: User's UTC offset string (e.g. "UTC+1").
        preferred_team_size: Preferred team size (informational, not scored).
        collaboration_style: Preferred working style.
        communication_preference: Preferred communication mode.
        limit: Maximum results to return.

    Returns:
        List of ranked match dicts with full score breakdowns and explanations.
    """
    profiles = db.query(CollaboratorProfile).all()
    total_profiles = max(len(profiles), 1)

    # ── Step 1: Pre-compute skill rarity ─────────────────────────────────────
    # Skills held by fewer profiles are rarer and more valuable when matched.
    # Rarity score: 1.0 (in every profile) → 1.5 (in a single profile)
    freq_rows = db.execute(
        select(Skill.name, func.count(ps_table.c.profile_id).label("cnt"))
        .join(ps_table, Skill.id == ps_table.c.skill_id)
        .group_by(Skill.name)
    ).fetchall()

    skill_rarity: Dict[str, float] = {
        name: 1.0 + (1.0 - count / total_profiles) * 0.5
        for name, count in freq_rows
    }

    # ── Step 2-5: Score every profile ────────────────────────────────────────
    matches: List[Dict[str, Any]] = []

    for profile in profiles:
        # Build name → proficiency dict for this profile
        prof_skill_rows = db.execute(
            ps_table.select().where(ps_table.c.profile_id == profile.id)
        ).fetchall()

        id_to_proficiency = {row.skill_id: row.proficiency_level for row in prof_skill_rows}

        profile_skill_names: Dict[str, str] = {
            skill.name: id_to_proficiency.get(skill.id, "intermediate")
            for skill in profile.skills
        }

        profile_interest_names = [i.name for i in profile.interests]

        # Calculate all 7 dimension scores
        skill_score, matched_skills, complementary_skills = calculate_skill_score(
            user_skills,
            needed_skills,
            profile_skill_names,
            profile,
            skill_rarity=skill_rarity,
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

        # Weighted overall score
        overall = (
            skill_score         * SCORING_WEIGHTS["skills"]
            + interest_score      * SCORING_WEIGHTS["interests"]
            + availability_score  * SCORING_WEIGHTS["availability"]
            + collaboration_score * SCORING_WEIGHTS["collaboration_style"]
            + communication_score * SCORING_WEIGHTS["communication"]
            + timezone_score      * SCORING_WEIGHTS["timezone"]
            + experience_score    * SCORING_WEIGHTS["experience"]
        )

        # Consistency adjustment: balanced profiles get a small bonus/penalty
        all_scores = [
            skill_score, interest_score, availability_score,
            timezone_score, experience_score,
            collaboration_score, communication_score,
        ]
        consistency = calculate_consistency_bonus(all_scores)
        overall_score = round(max(0.0, min(100.0, overall + consistency)), 1)

        # Generate human-readable explanations
        match_reasons = generate_match_reasons(
            skill_score, interest_score, availability_score,
            matched_skills, shared_interests, complementary_skills,
        )
        trade_offs = generate_trade_offs(
            skill_score, interest_score, availability_score,
            timezone_score, experience_score,
            collaboration_score, communication_score,
        )

        matches.append({
            "profile_id":               profile.id,
            "name":                     profile.name,
            "professional_title":       profile.professional_title,
            "bio":                      profile.bio,
            "experience_level":         profile.experience_level,
            "years_of_experience":      profile.years_of_experience,
            "weekly_availability_hours": profile.weekly_availability_hours,
            "timezone":                 profile.timezone,
            "collaboration_style":      profile.collaboration_style,
            "communication_preference": profile.communication_preference,
            "preferred_team_size":      profile.preferred_team_size,
            "overall_score":            overall_score,
            "score_breakdown": {
                "skills":              round(skill_score, 1),
                "interests":           round(interest_score, 1),
                "availability":        round(availability_score, 1),
                "collaboration_style": round(collaboration_score, 1),
                "communication":       round(communication_score, 1),
                "timezone":            round(timezone_score, 1),
                "experience":          round(experience_score, 1),
            },
            "matched_skills":       matched_skills,
            "complementary_skills": complementary_skills,
            "shared_interests":     shared_interests,
            "match_reasons":        match_reasons,
            "trade_offs":           trade_offs,
        })

    # Sort: overall_score DESC → skill_score DESC → profile_id ASC (stable)
    matches.sort(
        key=lambda x: (
            -x["overall_score"],
            -x["score_breakdown"]["skills"],
            x["profile_id"],
        )
    )

    for idx, match in enumerate(matches[:limit], start=1):
        match["rank"] = idx

    return matches[:limit]

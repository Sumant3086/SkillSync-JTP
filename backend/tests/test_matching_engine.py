"""Unit tests for the SkillSync matching engine (v2)."""
import math
import pytest
from app.services.matching_engine import (
    calculate_skill_score,
    calculate_interest_score,
    calculate_availability_score,
    calculate_timezone_score,
    calculate_experience_score,
    calculate_collaboration_score,
    calculate_communication_score,
    calculate_team_size_score,
    calculate_consistency_bonus,
    SCORING_WEIGHTS,
    PROFICIENCY_WEIGHTS,
)


# ── Meta ─────────────────────────────────────────────────────────────────────

def test_scoring_weights_total_100():
    """All scoring weights must sum to exactly 100 %."""
    total = sum(SCORING_WEIGHTS.values())
    assert abs(total - 1.0) < 0.001


def test_proficiency_weights_ordered():
    """Expert must score higher than advanced > intermediate > beginner."""
    levels = ["beginner", "intermediate", "advanced", "expert"]
    weights = [PROFICIENCY_WEIGHTS[l] for l in levels]
    assert weights == sorted(weights), "Proficiency weights must be ascending"


# ── Skill scoring ─────────────────────────────────────────────────────────────

def test_skill_score_perfect_match():
    """Matching all needed skills at high proficiency scores well above 70."""
    profile_skills = {"React": "advanced", "Node.js": "expert"}
    score, matched, _ = calculate_skill_score(
        user_skills=["Python"],
        needed_skills=["React", "Node.js"],
        profile_skills_dict=profile_skills,
        profile=None,
    )
    assert score >= 70.0, f"Perfect needed match should score high, got {score}"
    assert "React" in matched and "Node.js" in matched
    assert len(matched) == 2


def test_skill_score_with_complementary():
    """Complementary skills add value but total score stays ≤ 100."""
    profile_skills = {
        "React": "advanced",
        "Docker": "intermediate",
        "AWS": "advanced",
        "PostgreSQL": "expert",
    }
    score, matched, complementary = calculate_skill_score(
        user_skills=["Python"],
        needed_skills=["React"],
        profile_skills_dict=profile_skills,
        profile=None,
    )
    assert score <= 100.0
    assert len(complementary) > 0


def test_skill_score_no_match():
    """Profile with none of the needed skills scores below 50."""
    profile_skills = {"Java": "expert", "Spring Boot": "advanced"}
    score, matched, _ = calculate_skill_score(
        user_skills=["Python"],
        needed_skills=["React", "Node.js"],
        profile_skills_dict=profile_skills,
        profile=None,
    )
    assert score < 50.0, f"No skill match should score low, got {score}"
    assert len(matched) == 0


def test_skill_score_uses_proficiency():
    """Expert-level proficiency on the same skill should score higher than beginner."""
    expert_profile = {"React": "expert"}
    beginner_profile = {"React": "beginner"}

    score_expert, _, _ = calculate_skill_score(
        user_skills=[], needed_skills=["React"],
        profile_skills_dict=expert_profile, profile=None,
    )
    score_beginner, _, _ = calculate_skill_score(
        user_skills=[], needed_skills=["React"],
        profile_skills_dict=beginner_profile, profile=None,
    )
    assert score_expert > score_beginner, (
        f"Expert ({score_expert}) should beat beginner ({score_beginner})"
    )


def test_skill_score_rarity_bonus():
    """A rare needed skill matched at equal proficiency should score higher."""
    profile = {"Kubernetes": "advanced"}

    # Kubernetes is rare (only 1 out of 10 profiles)
    rare_rarity = {"Kubernetes": 1.0 + (1.0 - 1 / 10) * 0.5}  # 1.45
    # Kubernetes is common (9 out of 10 profiles)
    common_rarity = {"Kubernetes": 1.0 + (1.0 - 9 / 10) * 0.5}  # 1.05

    score_rare, _, _ = calculate_skill_score(
        user_skills=[], needed_skills=["Kubernetes"],
        profile_skills_dict=profile, profile=None,
        skill_rarity=rare_rarity,
    )
    score_common, _, _ = calculate_skill_score(
        user_skills=[], needed_skills=["Kubernetes"],
        profile_skills_dict=profile, profile=None,
        skill_rarity=common_rarity,
    )
    assert score_rare > score_common, (
        f"Rare skill match ({score_rare}) should beat common ({score_common})"
    )


# ── Interest scoring ──────────────────────────────────────────────────────────

def test_interest_score_full_overlap():
    """Identical interest sets should score 100."""
    score, shared = calculate_interest_score(
        user_interests=["Web Development", "Mobile Apps"],
        profile_interests=["Web Development", "Mobile Apps"],
    )
    assert score == 100.0
    assert len(shared) == 2


def test_interest_score_partial_overlap():
    """Partial overlap scores between 0 and 100."""
    score, shared = calculate_interest_score(
        user_interests=["Web Development", "Mobile Apps", "AI & Machine Learning"],
        profile_interests=["Web Development", "E-commerce"],
    )
    assert 0 < score < 100
    assert "Web Development" in shared


def test_interest_score_no_overlap():
    """No shared interests scores 0."""
    score, shared = calculate_interest_score(
        user_interests=["Gaming", "Blockchain"],
        profile_interests=["Healthcare Tech", "FinTech"],
    )
    assert score == 0.0
    assert len(shared) == 0


def test_interest_score_recall_weighted():
    """Profile covering ALL user interests should score higher than partial overlap."""
    # Profile A covers both of the user's interests plus more (full recall)
    score_full, _ = calculate_interest_score(
        user_interests=["Web Development", "SaaS Products"],
        profile_interests=["Web Development", "SaaS Products", "Gaming"],
    )
    # Profile B covers only one of the user's interests (partial recall)
    score_partial, _ = calculate_interest_score(
        user_interests=["Web Development", "SaaS Products"],
        profile_interests=["Web Development", "Healthcare Tech"],
    )
    assert score_full > score_partial, (
        f"Full recall ({score_full}) should beat partial ({score_partial})"
    )


# ── Availability scoring ──────────────────────────────────────────────────────

def test_availability_score_perfect_match():
    assert calculate_availability_score(20, 20) == 100.0


def test_availability_score_slight_surplus():
    """A small surplus (≤ 30 %) should still score 100."""
    assert calculate_availability_score(20, 25) == 100.0


def test_availability_score_insufficient():
    """Half the needed availability should score 50."""
    assert calculate_availability_score(20, 10) == 50.0


# ── Timezone scoring ──────────────────────────────────────────────────────────

def test_timezone_score_same_zone():
    assert calculate_timezone_score("UTC+5:30", "UTC+5:30") == 100.0


def test_timezone_score_close_zones():
    """1-hour difference should score well above 90."""
    score = calculate_timezone_score("UTC+0", "UTC+1")
    assert score >= 90.0, f"1 h diff should score ≥ 90, got {score}"


def test_timezone_score_opposite_zones():
    """16-hour difference should score very low (≤ 20)."""
    score = calculate_timezone_score("UTC+8", "UTC-8")
    assert score <= 20.0, f"16 h diff should score ≤ 20, got {score}"


def test_timezone_smooth_decay():
    """Scores should decrease monotonically as timezone distance grows."""
    scores = [
        calculate_timezone_score("UTC+0", f"UTC+{h}")
        for h in [0, 2, 5, 8, 12]
    ]
    assert scores == sorted(scores, reverse=True), (
        f"Timezone scores should decrease with distance: {scores}"
    )


# ── Experience scoring ────────────────────────────────────────────────────────

def test_experience_score_exact_match():
    assert calculate_experience_score("senior", "senior") == 100.0


def test_experience_score_adjacent_level_above():
    """Profile one level MORE experienced than requested scores 85 (not punished much)."""
    score = calculate_experience_score("mid-level", "senior")
    assert score == 85.0, f"One level above should score 85, got {score}"


def test_experience_score_adjacent_level_below():
    """Profile one level LESS experienced than requested scores 70."""
    score = calculate_experience_score("senior", "mid-level")
    assert score == 70.0, f"One level below should score 70, got {score}"


def test_experience_score_asymmetric():
    """Over-experienced should be penalised LESS than under-experienced."""
    score_over = calculate_experience_score("junior", "mid-level")   # diff = +1
    score_under = calculate_experience_score("mid-level", "junior")  # diff = -1
    assert score_over > score_under, (
        f"Over-experienced ({score_over}) should outscore under-experienced ({score_under})"
    )


def test_experience_score_distant_level():
    """Three levels apart (junior → lead) returns 35 (positive diff, less penalised)."""
    score = calculate_experience_score("junior", "lead")
    assert score == 35.0, f"Three levels above should score 35, got {score}"


# ── Collaboration scoring ─────────────────────────────────────────────────────

def test_collaboration_score_perfect_match():
    assert calculate_collaboration_score("collaborative", "collaborative") == 100.0


def test_collaboration_score_flexible():
    assert calculate_collaboration_score("collaborative", "flexible") == 90.0


def test_collaboration_score_mismatch():
    """Collaborative vs independent is a mismatch — scores 55."""
    score = calculate_collaboration_score("collaborative", "independent")
    assert score == 55.0, f"Collab/Independent mismatch should score 55, got {score}"


# ── Communication scoring ─────────────────────────────────────────────────────

def test_communication_score_perfect_match():
    assert calculate_communication_score("async", "async") == 100.0


def test_communication_score_hybrid_compatible():
    """Hybrid is compatible with sync/async — scores 85."""
    score = calculate_communication_score("sync", "hybrid")
    assert score == 85.0, f"Sync/Hybrid should score 85, got {score}"


def test_communication_score_mismatch():
    """Async vs sync is the worst mismatch — scores 45."""
    score = calculate_communication_score("async", "sync")
    assert score == 45.0, f"Async/Sync mismatch should score 45, got {score}"


# ── Consistency bonus ─────────────────────────────────────────────────────────

def test_consistency_bonus_perfectly_balanced():
    """All-equal scores (zero variance) should yield the maximum +3 bonus."""
    scores = [75.0] * 7
    bonus = calculate_consistency_bonus(scores)
    assert bonus == 3.0, f"Zero variance should give +3, got {bonus}"


def test_consistency_bonus_highly_uneven():
    """Very uneven scores should produce a negative adjustment."""
    scores = [100.0, 0.0, 100.0, 0.0, 100.0, 0.0, 100.0]
    bonus = calculate_consistency_bonus(scores)
    assert bonus < 0, f"High variance should give negative adjustment, got {bonus}"


def test_consistency_bonus_range():
    """Consistency bonus must stay within [-3, +3]."""
    test_cases = [
        [100, 0, 100, 0, 100, 0, 100],   # extreme uneven
        [50] * 7,                          # perfectly balanced
        [80, 20, 90, 10, 70, 30, 60],     # mixed
    ]
    for scores in test_cases:
        bonus = calculate_consistency_bonus(scores)
        assert -3.0 <= bonus <= 3.0, f"Bonus {bonus} out of [-3, 3] for scores {scores}"


# ── Team size scoring ─────────────────────────────────────────────────────────

def test_team_size_score_exact_match():
    assert calculate_team_size_score("small (2-3)", "small (2-3)") == 100.0


def test_team_size_score_one_step():
    """Adjacent sizes score 65."""
    assert calculate_team_size_score("small (2-3)", "medium (4-6)") == 65.0
    assert calculate_team_size_score("medium (4-6)", "large (7+)") == 65.0


def test_team_size_score_two_steps():
    """Opposite ends score 30."""
    assert calculate_team_size_score("small (2-3)", "large (7+)") == 30.0


def test_team_size_score_no_preference():
    """Empty preference returns neutral 50."""
    assert calculate_team_size_score("", "medium (4-6)") == 50.0


def test_team_size_in_scoring_weights():
    """team_size must be a weighted dimension (closing the v1/v2 gap)."""
    assert "team_size" in SCORING_WEIGHTS
    assert SCORING_WEIGHTS["team_size"] > 0


# ── Cross-cutting ─────────────────────────────────────────────────────────────

def test_all_scores_in_valid_range():
    """Every scoring function must return a value in [0, 100]."""
    results = [
        calculate_availability_score(10, 5),
        calculate_timezone_score("UTC+0", "UTC+12"),
        calculate_experience_score("junior", "lead"),
        calculate_collaboration_score("collaborative", "independent"),
        calculate_communication_score("async", "sync"),
    ]
    for score in results:
        assert 0 <= score <= 100, f"Score {score} is outside [0, 100]"


def test_deterministic_scoring():
    """Same inputs must always produce the same outputs."""
    profile_skills = {"React": "advanced", "Node.js": "expert"}
    args = (["Python"], ["React"], profile_skills, None)

    score1, matched1, comp1 = calculate_skill_score(*args)
    score2, matched2, comp2 = calculate_skill_score(*args)

    assert score1 == score2
    assert matched1 == matched2

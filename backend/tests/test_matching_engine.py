"""Unit tests for the matching engine."""
import pytest
from app.services.matching_engine import (
    calculate_skill_score,
    calculate_interest_score,
    calculate_availability_score,
    calculate_timezone_score,
    calculate_experience_score,
    calculate_collaboration_score,
    calculate_communication_score,
    SCORING_WEIGHTS
)


def test_scoring_weights_total_100():
    """Verify that all scoring weights sum to exactly 100%."""
    total = sum(SCORING_WEIGHTS.values())
    assert abs(total - 1.0) < 0.001, "Scoring weights must sum to 100%"


def test_skill_score_perfect_match():
    """Test skill scoring with perfect needed skills match."""
    profile_skills = {"React": "advanced", "Node.js": "expert"}
    score, matched, complementary = calculate_skill_score(
        user_skills=["Python"],
        needed_skills=["React", "Node.js"],
        profile_skills_dict=profile_skills,
        profile=None
    )
    assert score >= 70.0, "Perfect needed match should score high"
    assert "React" in matched and "Node.js" in matched
    assert len(matched) == 2


def test_skill_score_with_complementary():
    """Test that complementary skills add value but don't dominate."""
    profile_skills = {
        "React": "advanced",
        "Docker": "intermediate",
        "AWS": "advanced",
        "PostgreSQL": "expert"
    }
    score, matched, complementary = calculate_skill_score(
        user_skills=["Python"],
        needed_skills=["React"],
        profile_skills_dict=profile_skills,
        profile=None
    )
    assert score <= 100.0, "Score must not exceed 100"
    assert len(complementary) > 0, "Should identify complementary skills"


def test_skill_score_no_match():
    """Test skill scoring when profile has no needed skills."""
    profile_skills = {"Java": "expert", "Spring Boot": "advanced"}
    score, matched, complementary = calculate_skill_score(
        user_skills=["Python"],
        needed_skills=["React", "Node.js"],
        profile_skills_dict=profile_skills,
        profile=None
    )
    assert score < 50.0, "No match should result in low score"
    assert len(matched) == 0



def test_interest_score_full_overlap():
    """Test interest scoring with complete overlap."""
    score, shared = calculate_interest_score(
        user_interests=["Web Development", "Mobile Apps"],
        profile_interests=["Web Development", "Mobile Apps"]
    )
    assert score == 100.0, "Complete overlap should score 100"
    assert len(shared) == 2


def test_interest_score_partial_overlap():
    """Test interest scoring with partial overlap."""
    score, shared = calculate_interest_score(
        user_interests=["Web Development", "Mobile Apps", "AI & Machine Learning"],
        profile_interests=["Web Development", "E-commerce"]
    )
    assert 0 < score < 100, "Partial overlap should score between 0 and 100"
    assert "Web Development" in shared


def test_interest_score_no_overlap():
    """Test interest scoring with no overlap."""
    score, shared = calculate_interest_score(
        user_interests=["Gaming", "Blockchain"],
        profile_interests=["Healthcare Tech", "FinTech"]
    )
    assert score == 0.0, "No overlap should score 0"
    assert len(shared) == 0


def test_availability_score_perfect_match():
    """Test availability scoring when profile meets needs perfectly."""
    score = calculate_availability_score(
        user_availability=20,
        profile_availability=20
    )
    assert score == 100.0, "Perfect match should score 100"


def test_availability_score_exceeds_needs():
    """Test availability scoring when profile exceeds needs reasonably."""
    score = calculate_availability_score(
        user_availability=20,
        profile_availability=25
    )
    assert score >= 90.0, "Reasonable excess should still score high"


def test_availability_score_insufficient():
    """Test availability scoring when profile has insufficient hours."""
    score = calculate_availability_score(
        user_availability=20,
        profile_availability=10
    )
    assert score == 50.0, "Half availability should score 50"


def test_timezone_score_same_zone():
    """Test timezone scoring for same timezone."""
    score = calculate_timezone_score("UTC+5:30", "UTC+5:30")
    assert score == 100.0, "Same timezone should score 100"


def test_timezone_score_close_zones():
    """Test timezone scoring for nearby timezones."""
    score = calculate_timezone_score("UTC+0", "UTC+1")
    assert score >= 90.0, "1 hour difference should score very high"


def test_timezone_score_opposite_zones():
    """Test timezone scoring for opposite timezones."""
    score = calculate_timezone_score("UTC+8", "UTC-8")
    assert score <= 50.0, "16 hour difference should score low"



def test_experience_score_exact_match():
    """Test experience scoring with exact match."""
    score = calculate_experience_score("senior", "senior")
    assert score == 100.0, "Exact match should score 100"


def test_experience_score_adjacent_level():
    """Test experience scoring with adjacent levels."""
    score = calculate_experience_score("mid-level", "senior")
    assert score == 80.0, "Adjacent level should score 80"


def test_experience_score_distant_level():
    """Test experience scoring with distant levels."""
    score = calculate_experience_score("junior", "lead")
    assert score == 30.0, "Three levels apart should score 30"


def test_collaboration_score_perfect_match():
    """Test collaboration style with perfect match."""
    score = calculate_collaboration_score("collaborative", "collaborative")
    assert score == 100.0, "Perfect match should score 100"


def test_collaboration_score_flexible():
    """Test collaboration style with flexible partner."""
    score = calculate_collaboration_score("collaborative", "flexible")
    assert score == 90.0, "Flexible should be compatible with all styles"


def test_collaboration_score_mismatch():
    """Test collaboration style with mismatch."""
    score = calculate_collaboration_score("collaborative", "independent")
    assert score == 60.0, "Collaborative-Independent should score lower"


def test_communication_score_perfect_match():
    """Test communication preference with perfect match."""
    score = calculate_communication_score("async", "async")
    assert score == 100.0, "Perfect match should score 100"


def test_communication_score_hybrid():
    """Test communication preference with hybrid."""
    score = calculate_communication_score("sync", "hybrid")
    assert score == 90.0, "Hybrid should be compatible"


def test_communication_score_mismatch():
    """Test communication preference with mismatch."""
    score = calculate_communication_score("async", "sync")
    assert score == 50.0, "Async-Sync mismatch should score 50"


def test_score_boundaries():
    """Test that all scoring functions return values between 0 and 100."""
    # This is a meta-test to ensure score boundaries
    test_cases = [
        calculate_availability_score(10, 5),
        calculate_timezone_score("UTC+0", "UTC+12"),
        calculate_experience_score("junior", "lead"),
        calculate_collaboration_score("collaborative", "independent"),
        calculate_communication_score("async", "sync")
    ]
    
    for score in test_cases:
        assert 0 <= score <= 100, f"Score {score} is outside valid range [0, 100]"


def test_deterministic_scoring():
    """Test that scoring is deterministic (same inputs produce same outputs)."""
    # Run the same calculation twice
    profile_skills = {"React": "advanced", "Node.js": "expert"}
    
    score1, matched1, comp1 = calculate_skill_score(
        ["Python"], ["React"], profile_skills, None
    )
    score2, matched2, comp2 = calculate_skill_score(
        ["Python"], ["React"], profile_skills, None
    )
    
    assert score1 == score2, "Scoring must be deterministic"
    assert matched1 == matched2, "Matched skills must be deterministic"

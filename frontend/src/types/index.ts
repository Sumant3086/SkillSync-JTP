// Type definitions for SkillSync

export interface MatchPreferences {
  user_skills: string[];
  needed_skills: string[];
  project_interests: string[];
  preferred_experience: string;
  weekly_availability: number;
  timezone: string;
  preferred_team_size: string;
  collaboration_style: string;
  communication_preference: string;
}

export interface ScoreBreakdown {
  skills: number;
  interests: number;
  availability: number;
  collaboration_style: number;
  communication: number;
  timezone: number;
  experience: number;
  team_size: number;
}

export interface MatchResult {
  rank: number;
  profile_id: number;
  name: string;
  professional_title: string;
  bio: string;
  experience_level: string;
  years_of_experience: number;
  weekly_availability_hours: number;
  timezone: string;
  collaboration_style: string;
  communication_preference: string;
  preferred_team_size: string;
  overall_score: number;
  score_breakdown: ScoreBreakdown;
  matched_skills: string[];
  complementary_skills: string[];
  shared_interests: string[];
  match_reasons: string[];
  trade_offs: string[];
}

export interface MatchResponse {
  total_profiles_evaluated: number;
  matches_returned: number;
  scoring_weights: Record<string, number>;
  matches: MatchResult[];
}

export interface Options {
  skills: string[];
  skills_by_category: Record<string, string[]>;
  project_interests: string[];
  experience_levels: string[];
  collaboration_styles: string[];
  communication_preferences: string[];
  team_sizes: string[];
  timezones: string[];
}

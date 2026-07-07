import { useState } from 'react';
import { MatchResponse, MatchResult } from '../types';

interface ResultsProps {
  results: MatchResponse;
  onNewSearch: () => void;
}

function Results({ results, onNewSearch }: ResultsProps) {
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set());

  const toggleExpand = (profileId: number) => {
    const newExpanded = new Set(expandedIds);
    if (newExpanded.has(profileId)) {
      newExpanded.delete(profileId);
    } else {
      newExpanded.add(profileId);
    }
    setExpandedIds(newExpanded);
  };

  return (
    <div className="results">
      <div className="results-header">
        <h1>Your Matches</h1>
        <p className="results-summary">
          Evaluated {results.total_profiles_evaluated} profiles and found{' '}
          {results.matches_returned} matches based on your preferences.
        </p>
        <div className="results-actions">
          <button className="btn btn-secondary" onClick={onNewSearch}>
            Adjust Preferences
          </button>
        </div>
      </div>

      {results.matches.map(match => (
        <MatchCard
          key={match.profile_id}
          match={match}
          expanded={expandedIds.has(match.profile_id)}
          onToggle={() => toggleExpand(match.profile_id)}
        />
      ))}
    </div>
  );
}

interface MatchCardProps {
  match: MatchResult;
  expanded: boolean;
  onToggle: () => void;
}

function MatchCard({ match, expanded, onToggle }: MatchCardProps) {
  return (
    <div className="match-card">
      <div className="match-header">
        <div className="match-rank">#{match.rank}</div>
        <div className="match-score">
          <div className="score-value">{match.overall_score}%</div>
          <div className="score-label">Compatibility</div>
        </div>
      </div>

      <div className="match-info">
        <h3>{match.name}</h3>
        <p className="match-title">{match.professional_title}</p>
        <p className="match-bio">{match.bio}</p>

        <div className="match-details">
          <div className="detail-item">
            <span className="detail-label">Experience</span>
            <span className="detail-value">
              {match.experience_level} ({match.years_of_experience} years)
            </span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Availability</span>
            <span className="detail-value">{match.weekly_availability_hours} hrs/week</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Timezone</span>
            <span className="detail-value">{match.timezone}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Team Size</span>
            <span className="detail-value">{match.preferred_team_size}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Collaboration</span>
            <span className="detail-value">{match.collaboration_style}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Communication</span>
            <span className="detail-value">{match.communication_preference}</span>
          </div>
        </div>

        <div className="match-highlights">
          {match.matched_skills.length > 0 && (
            <div className="highlight-section">
              <div className="highlight-title">✓ Matched Skills</div>
              <div className="skill-tags">
                {match.matched_skills.map(skill => (
                  <span key={skill} className="tag">{skill}</span>
                ))}
              </div>
            </div>
          )}

          {match.complementary_skills.length > 0 && (
            <div className="highlight-section">
              <div className="highlight-title">+ Complementary Skills</div>
              <div className="skill-tags">
                {match.complementary_skills.map(skill => (
                  <span key={skill} className="tag">{skill}</span>
                ))}
              </div>
            </div>
          )}

          {match.shared_interests.length > 0 && (
            <div className="highlight-section">
              <div className="highlight-title">🎯 Shared Interests</div>
              <div className="interest-tags">
                {match.shared_interests.map(interest => (
                  <span key={interest} className="tag">{interest}</span>
                ))}
              </div>
            </div>
          )}

          {match.match_reasons.length > 0 && (
            <div className="highlight-section">
              <div className="highlight-title">Why This Match</div>
              <ul className="reason-list">
                {match.match_reasons.map((reason, idx) => (
                  <li key={idx}>{reason}</li>
                ))}
              </ul>
            </div>
          )}

          {match.trade_offs.length > 0 && (
            <div className="highlight-section">
              <div className="highlight-title">Considerations</div>
              <ul className="tradeoff-list">
                {match.trade_offs.map((tradeoff, idx) => (
                  <li key={idx}>{tradeoff}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <button className="expand-btn" onClick={onToggle}>
          {expanded ? '− Hide' : '+ Show'} Score Breakdown
        </button>

        {expanded && (
          <div className="score-breakdown">
            <h4 style={{ marginBottom: '0.75rem' }}>Detailed Score Breakdown</h4>
            <div className="breakdown-item">
              <span className="breakdown-label">Skills</span>
              <span className="breakdown-score">{match.score_breakdown.skills}%</span>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">Interests</span>
              <span className="breakdown-score">{match.score_breakdown.interests}%</span>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">Availability</span>
              <span className="breakdown-score">{match.score_breakdown.availability}%</span>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">Collaboration Style</span>
              <span className="breakdown-score">{match.score_breakdown.collaboration_style}%</span>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">Communication</span>
              <span className="breakdown-score">{match.score_breakdown.communication}%</span>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">Timezone</span>
              <span className="breakdown-score">{match.score_breakdown.timezone}%</span>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">Experience</span>
              <span className="breakdown-score">{match.score_breakdown.experience}%</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Results;

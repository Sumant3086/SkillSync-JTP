import { useState } from 'react';
import { MatchResponse, MatchResult } from '../types';

interface ResultsProps {
  results: MatchResponse;
  onNewSearch: () => void;
  onBackToHome: () => void;
}

function Results({ results, onNewSearch, onBackToHome }: ResultsProps) {
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
        <div className="results-header-top">
          <div>
            <h1>Your Matches</h1>
            <p className="results-summary">
              Evaluated <strong>{results.total_profiles_evaluated}</strong> profiles and found{' '}
              <strong>{results.matches_returned}</strong> best matches for your preferences.
            </p>
          </div>
        </div>
        <div className="results-actions">
          <button className="btn btn-secondary" onClick={onBackToHome}>
            ← Home
          </button>
          <button className="btn btn-primary" onClick={onNewSearch}>
            Adjust Preferences
          </button>
        </div>
      </div>

      {results.matches.length === 0 ? (
        <div className="no-results">
          <p>No matches found. Try broadening your preferences.</p>
        </div>
      ) : (
        results.matches.map(match => (
          <MatchCard
            key={match.profile_id}
            match={match}
            expanded={expandedIds.has(match.profile_id)}
            onToggle={() => toggleExpand(match.profile_id)}
          />
        ))
      )}
    </div>
  );
}

interface MatchCardProps {
  match: MatchResult;
  expanded: boolean;
  onToggle: () => void;
}

function getScoreColor(score: number): string {
  if (score >= 70) return 'score-high';
  if (score >= 45) return 'score-medium';
  return 'score-low';
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="breakdown-item">
      <div className="breakdown-meta">
        <span className="breakdown-label">{label}</span>
        <span className={`breakdown-score ${getScoreColor(value)}`}>{value}%</span>
      </div>
      <div className="breakdown-bar-bg">
        <div
          className={`breakdown-bar-fill ${getScoreColor(value)}`}
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
    </div>
  );
}

function MatchCard({ match, expanded, onToggle }: MatchCardProps) {
  return (
    <div className="match-card">
      <div className="match-header">
        <div className="match-rank-block">
          <div className="match-avatar">{getInitials(match.name)}</div>
          <div className="match-rank">#{match.rank}</div>
        </div>
        <div className="match-score-block">
          <div className={`score-value ${getScoreColor(match.overall_score)}`}>
            {match.overall_score}%
          </div>
          <div className="score-label">Match</div>
          <div className="score-bar-mini">
            <div
              className={`score-bar-fill ${getScoreColor(match.overall_score)}`}
              style={{ width: `${match.overall_score}%` }}
            />
          </div>
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
              {match.experience_level} · {match.years_of_experience} yrs
            </span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Availability</span>
            <span className="detail-value">{match.weekly_availability_hours} hrs / week</span>
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
              <div className="highlight-title highlight-title--success">✓ Matched Skills</div>
              <div className="skill-tags">
                {match.matched_skills.map(skill => (
                  <span key={skill} className="tag tag--success">{skill}</span>
                ))}
              </div>
            </div>
          )}

          {match.complementary_skills.length > 0 && (
            <div className="highlight-section">
              <div className="highlight-title highlight-title--info">+ Complementary Skills</div>
              <div className="skill-tags">
                {match.complementary_skills.map(skill => (
                  <span key={skill} className="tag tag--info">{skill}</span>
                ))}
              </div>
            </div>
          )}

          {match.shared_interests.length > 0 && (
            <div className="highlight-section">
              <div className="highlight-title highlight-title--primary">Shared Interests</div>
              <div className="interest-tags">
                {match.shared_interests.map(interest => (
                  <span key={interest} className="tag tag--primary">{interest}</span>
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
            <h4>Detailed Score Breakdown</h4>
            <ScoreBar label="Skills Match" value={match.score_breakdown.skills} />
            <ScoreBar label="Shared Interests" value={match.score_breakdown.interests} />
            <ScoreBar label="Availability" value={match.score_breakdown.availability} />
            <ScoreBar label="Collaboration Style" value={match.score_breakdown.collaboration_style} />
            <ScoreBar label="Communication" value={match.score_breakdown.communication} />
            <ScoreBar label="Timezone" value={match.score_breakdown.timezone} />
            <ScoreBar label="Experience Level" value={match.score_breakdown.experience} />
          </div>
        )}
      </div>
    </div>
  );
}

export default Results;

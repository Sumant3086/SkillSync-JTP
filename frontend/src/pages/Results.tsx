import { useState } from 'react';
import { MatchResponse, MatchResult, ScoreBreakdown } from '../types';

interface ResultsProps {
  results: MatchResponse;
  onNewSearch: () => void;
  onBackToHome: () => void;
}

type SortKey = 'overall' | 'skills' | 'availability' | 'timezone' | 'interests';

const SORT_LABELS: Record<SortKey, string> = {
  overall:      'Overall Match',
  skills:       'Best Skills',
  availability: 'Best Availability',
  timezone:     'Closest Timezone',
  interests:    'Most Shared Interests',
};

function Results({ results, onNewSearch, onBackToHome }: ResultsProps) {
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set());
  const [sortBy, setSortBy]       = useState<SortKey>('overall');
  const [minScore, setMinScore]   = useState<number>(0);

  const toggleExpand = (profileId: number) => {
    const s = new Set(expandedIds);
    s.has(profileId) ? s.delete(profileId) : s.add(profileId);
    setExpandedIds(s);
  };

  const displayed = [...results.matches]
    .filter(m => m.overall_score >= minScore)
    .sort((a, b) => {
      if (sortBy === 'overall')      return b.overall_score - a.overall_score;
      if (sortBy === 'skills')       return b.score_breakdown.skills - a.score_breakdown.skills;
      if (sortBy === 'availability') return b.score_breakdown.availability - a.score_breakdown.availability;
      if (sortBy === 'timezone')     return b.score_breakdown.timezone - a.score_breakdown.timezone;
      if (sortBy === 'interests')    return b.score_breakdown.interests - a.score_breakdown.interests;
      return 0;
    });

  return (
    <div className="results">
      <div className="results-header">
        <div className="results-header-top">
          <div>
            <h1>Your Matches</h1>
            <p className="results-summary">
              Evaluated <strong>{results.total_profiles_evaluated}</strong> profiles —
              showing <strong>{displayed.length}</strong> of {results.matches_returned} matches.
            </p>
          </div>
          <div className="results-actions">
            <button className="btn btn-secondary" onClick={onBackToHome}>← Home</button>
            <button className="btn btn-primary" onClick={onNewSearch}>Adjust Preferences</button>
          </div>
        </div>

        {/* Sort + Filter controls */}
        <div className="results-controls">
          <div className="control-group">
            <label className="control-label">Sort by</label>
            <div className="sort-pills">
              {(Object.keys(SORT_LABELS) as SortKey[]).map(key => (
                <button
                  key={key}
                  className={`sort-pill ${sortBy === key ? 'sort-pill--active' : ''}`}
                  onClick={() => setSortBy(key)}
                >
                  {SORT_LABELS[key]}
                </button>
              ))}
            </div>
          </div>

          <div className="control-group">
            <label className="control-label">Min score: <strong>{minScore}%</strong></label>
            <input
              type="range"
              min={0}
              max={80}
              step={5}
              value={minScore}
              onChange={e => setMinScore(Number(e.target.value))}
              className="form-range filter-range"
            />
          </div>
        </div>
      </div>

      {displayed.length === 0 ? (
        <div className="no-results">
          <p>No matches above {minScore}%. Try lowering the minimum score filter.</p>
        </div>
      ) : (
        displayed.map((match, idx) => (
          <MatchCard
            key={match.profile_id}
            match={match}
            rank={idx + 1}
            expanded={expandedIds.has(match.profile_id)}
            onToggle={() => toggleExpand(match.profile_id)}
          />
        ))
      )}
    </div>
  );
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function getScoreColor(score: number): string {
  if (score >= 70) return 'score-high';
  if (score >= 45) return 'score-medium';
  return 'score-low';
}

function getInitials(name: string): string {
  return name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
}

// ── Radar Chart ───────────────────────────────────────────────────────────────

const RADAR_DIMS: { key: keyof ScoreBreakdown; label: string; weight: number }[] = [
  { key: 'skills',              label: 'Skills',        weight: 33 },
  { key: 'interests',           label: 'Interests',     weight: 18 },
  { key: 'availability',        label: 'Availability',  weight: 14 },
  { key: 'collaboration_style', label: 'Collab',        weight: 9  },
  { key: 'communication',       label: 'Comms',         weight: 9  },
  { key: 'timezone',            label: 'Timezone',      weight: 5  },
  { key: 'experience',          label: 'Experience',    weight: 5  },
  { key: 'team_size',           label: 'Team Size',     weight: 7  },
];

function RadarChart({ breakdown }: { breakdown: ScoreBreakdown }) {
  const N   = RADAR_DIMS.length;
  const CX  = 130;
  const CY  = 130;
  const R   = 85;
  const PAD = 28; // label padding from outer ring

  const angle = (i: number) => -Math.PI / 2 + (2 * Math.PI * i) / N;

  const point = (i: number, pct: number) => ({
    x: CX + R * (pct / 100) * Math.cos(angle(i)),
    y: CY + R * (pct / 100) * Math.sin(angle(i)),
  });

  const outerPt = (i: number) => ({
    x: CX + (R + PAD) * Math.cos(angle(i)),
    y: CY + (R + PAD) * Math.sin(angle(i)),
  });

  const gridLevels = [25, 50, 75, 100];

  const scores = RADAR_DIMS.map(d => breakdown[d.key] ?? 0);
  const dataPoints = scores.map((s, i) => point(i, s));
  const polygon = dataPoints.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');

  return (
    <svg
      width="260"
      height="260"
      viewBox="0 0 260 260"
      className="radar-svg"
      aria-label="Compatibility radar chart"
    >
      {/* Grid rings */}
      {gridLevels.map(level => {
        const pts = RADAR_DIMS.map((_, i) => point(i, level));
        return (
          <polygon
            key={level}
            points={pts.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="1"
          />
        );
      })}

      {/* Axis spokes */}
      {RADAR_DIMS.map((_, i) => {
        const outer = point(i, 100);
        return (
          <line
            key={i}
            x1={CX} y1={CY}
            x2={outer.x.toFixed(1)} y2={outer.y.toFixed(1)}
            stroke="#e5e7eb"
            strokeWidth="1"
          />
        );
      })}

      {/* Score polygon */}
      <polygon
        points={polygon}
        fill="rgba(79,70,229,0.18)"
        stroke="#4f46e5"
        strokeWidth="2"
        strokeLinejoin="round"
      />

      {/* Score dots */}
      {dataPoints.map((p, i) => (
        <circle key={i} cx={p.x.toFixed(1)} cy={p.y.toFixed(1)} r="3.5" fill="#4f46e5" />
      ))}

      {/* Axis labels */}
      {RADAR_DIMS.map((d, i) => {
        const lp = outerPt(i);
        const a = (angle(i) * 180) / Math.PI;
        const anchor =
          Math.abs(a) < 10 || Math.abs(a) > 170 ? 'middle'
          : a < 0 || a > 180 ? 'end'
          : 'start';
        return (
          <text
            key={i}
            x={lp.x.toFixed(1)}
            y={lp.y.toFixed(1)}
            textAnchor={anchor}
            dominantBaseline="middle"
            fontSize="9.5"
            fontWeight="600"
            fill="#6b7280"
          >
            {d.label}
          </text>
        );
      })}

      {/* Grid level annotations */}
      <text x={CX + 3} y={CY - R * 0.25 - 2} fontSize="7.5" fill="#9ca3af">25</text>
      <text x={CX + 3} y={CY - R * 0.50 - 2} fontSize="7.5" fill="#9ca3af">50</text>
      <text x={CX + 3} y={CY - R * 0.75 - 2} fontSize="7.5" fill="#9ca3af">75</text>
    </svg>
  );
}

// ── Score bar ─────────────────────────────────────────────────────────────────

function ScoreBar({
  label,
  value,
  weight,
}: {
  label: string;
  value: number;
  weight: number;
}) {
  return (
    <div className="breakdown-item">
      <div className="breakdown-meta">
        <span className="breakdown-label">
          {label}
          <span className="breakdown-weight">{weight}%</span>
        </span>
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

// ── Match card ────────────────────────────────────────────────────────────────

interface MatchCardProps {
  match: MatchResult;
  rank: number;
  expanded: boolean;
  onToggle: () => void;
}

function MatchCard({ match, rank, expanded, onToggle }: MatchCardProps) {
  return (
    <div className="match-card">
      <div className="match-header">
        <div className="match-rank-block">
          <div className="match-avatar">{getInitials(match.name)}</div>
          <div className="match-rank">#{rank}</div>
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
                {match.matched_skills.map(s => (
                  <span key={s} className="tag tag--success">{s}</span>
                ))}
              </div>
            </div>
          )}

          {match.complementary_skills.length > 0 && (
            <div className="highlight-section">
              <div className="highlight-title highlight-title--info">+ Complementary Skills</div>
              <div className="skill-tags">
                {match.complementary_skills.map(s => (
                  <span key={s} className="tag tag--info">{s}</span>
                ))}
              </div>
            </div>
          )}

          {match.shared_interests.length > 0 && (
            <div className="highlight-section">
              <div className="highlight-title highlight-title--primary">Shared Interests</div>
              <div className="interest-tags">
                {match.shared_interests.map(i => (
                  <span key={i} className="tag tag--primary">{i}</span>
                ))}
              </div>
            </div>
          )}

          {match.match_reasons.length > 0 && (
            <div className="highlight-section">
              <div className="highlight-title">Why This Match</div>
              <ul className="reason-list">
                {match.match_reasons.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          )}

          {match.trade_offs.length > 0 && (
            <div className="highlight-section">
              <div className="highlight-title">Considerations</div>
              <ul className="tradeoff-list">
                {match.trade_offs.map((t, i) => <li key={i}>{t}</li>)}
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
            <div className="breakdown-layout">
              {/* Radar chart */}
              <div className="radar-wrap">
                <RadarChart breakdown={match.score_breakdown} />
              </div>
              {/* Dimension bars */}
              <div className="breakdown-bars">
                {RADAR_DIMS.map(d => (
                  <ScoreBar
                    key={d.key}
                    label={d.label === 'Collab' ? 'Collaboration' : d.label === 'Comms' ? 'Communication' : d.label}
                    value={match.score_breakdown[d.key] ?? 0}
                    weight={d.weight}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Results;

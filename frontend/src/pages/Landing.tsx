interface LandingProps {
  onStart: () => void;
}

const FEATURES = [
  {
    icon: '🎯',
    title: 'Multi-Dimensional Matching',
    description:
      'Evaluates 7 compatibility dimensions: skills, interests, availability, collaboration style, communication, timezone, and experience level.',
  },
  {
    icon: '🔍',
    title: 'Explainable Results',
    description:
      'Every match comes with a detailed score breakdown and clear reasons — no black-box recommendations.',
  },
  {
    icon: '⚡',
    title: 'Instant Results',
    description:
      'Deterministic weighted algorithm evaluates all 40 profiles in milliseconds and returns the top 10 ranked matches.',
  },
  {
    icon: '⚖️',
    title: 'Honest Trade-offs',
    description:
      "We highlight potential compatibility concerns alongside strengths, so you can make an informed decision.",
  },
];

function Landing({ onStart }: LandingProps) {
  return (
    <div className="landing">
      <div className="hero">
        <div className="hero-badge">JTP 2026 · Matching Service</div>
        <h1 className="hero-title">Find the Right Collaborator</h1>
        <p className="hero-subtitle">
          Most platforms match by job title. SkillSync goes deeper — evaluating complementary
          abilities, shared interests, working styles, and timezone fit to surface truly
          compatible project partners.
        </p>
        <button className="btn btn-primary btn-lg" onClick={onStart}>
          Start Matching →
        </button>
      </div>

      <div className="features-grid">
        {FEATURES.map(f => (
          <div key={f.title} className="feature-card">
            <div className="feature-icon">{f.icon}</div>
            <h3 className="feature-title">{f.title}</h3>
            <p className="feature-desc">{f.description}</p>
          </div>
        ))}
      </div>

      <div className="how-it-works">
        <h2>How It Works</h2>
        <ol>
          <li>Select the project domains you are working on</li>
          <li>Tell us which skills you already have</li>
          <li>Describe what you need from an ideal collaborator</li>
          <li>Set your working preferences and availability</li>
          <li>Review and submit — get ranked matches with scores and explanations</li>
        </ol>
      </div>

      <div className="algo-box">
        <h3>The Algorithm</h3>
        <p>
          SkillSync uses a <strong>deterministic weighted scoring model</strong>. Each profile
          is evaluated across 7 dimensions and receives a weighted overall score (0–100%).
          Results are ranked by score, then by skill coverage as a tiebreaker.
        </p>
        <div className="weight-list">
          <span className="weight-item">Skills 35%</span>
          <span className="weight-item">Interests 20%</span>
          <span className="weight-item">Availability 15%</span>
          <span className="weight-item">Collaboration 10%</span>
          <span className="weight-item">Communication 10%</span>
          <span className="weight-item">Timezone 5%</span>
          <span className="weight-item">Experience 5%</span>
        </div>
      </div>
    </div>
  );
}

export default Landing;

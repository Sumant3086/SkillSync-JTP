interface LandingProps {
  onStart: () => void;
}

function Landing({ onStart }: LandingProps) {
  return (
    <div className="landing">
      <h1 className="hero-title">SkillSync</h1>
      <p className="hero-subtitle">Find the right collaborator, not just another profile</p>
      <p className="hero-description">
        Most platforms match people based on job titles and a handful of skills.
        SkillSync goes deeper—evaluating complementary abilities, shared interests,
        working styles, availability, and more to help you find truly compatible
        collaborators for your projects.
      </p>

      <button className="btn btn-primary" onClick={onStart}>
        Find My Matches
      </button>

      <div className="how-it-works">
        <h2>How It Works</h2>
        <ol>
          <li>Tell us about your project and the skills you bring</li>
          <li>Describe what you need from an ideal collaborator</li>
          <li>Share your working preferences and availability</li>
          <li>Review your preferences and submit</li>
          <li>Get ranked matches with clear, explainable reasons</li>
        </ol>
      </div>
    </div>
  );
}

export default Landing;

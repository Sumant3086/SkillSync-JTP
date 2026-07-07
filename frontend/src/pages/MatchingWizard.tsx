import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { MatchPreferences, Options, MatchResponse } from '../types';
import MultiSelect from '../components/MultiSelect';

interface MatchingWizardProps {
  onComplete: (results: MatchResponse) => void;
  onBack: () => void;
}

const STEPS = [
  { id: 1, title: 'Your Project', description: 'What domains are you working in?' },
  { id: 2, title: 'Your Skills', description: 'What skills do you already bring?' },
  { id: 3, title: 'Ideal Collaborator', description: 'What do you need from a partner?' },
  { id: 4, title: 'Working Style', description: 'How do you like to collaborate?' },
  { id: 5, title: 'Review & Match', description: 'Confirm your preferences and find matches' },
];

const SKILL_CATEGORIES: Record<string, string> = {
  frontend: 'Frontend',
  backend: 'Backend',
  database: 'Database',
  devops: 'DevOps',
  data: 'Data & AI',
  design: 'Design',
  mobile: 'Mobile',
  tools: 'Tools & Practices',
};

function MatchingWizard({ onComplete, onBack }: MatchingWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [options, setOptions] = useState<Options | null>(null);
  const [skillCategory, setSkillCategory] = useState<string>('all');

  const [preferences, setPreferences] = useState<MatchPreferences>({
    user_skills: [],
    needed_skills: [],
    project_interests: [],
    preferred_experience: '',
    weekly_availability: 20,
    timezone: 'UTC+0',
    preferred_team_size: '',
    collaboration_style: '',
    communication_preference: '',
  });

  useEffect(() => {
    api.getOptions()
      .then(data => setOptions(data))
      .catch(() => setError('Failed to load options. Please refresh the page.'));
  }, []);

  const handleNext = () => {
    if (currentStep < STEPS.length) setCurrentStep(currentStep + 1);
  };

  const handleBack = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
    else onBack();
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const results = await api.findMatches(preferences);
      onComplete(results);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to find matches. Please try again.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  if (!options) {
    return (
      <div className="loading">
        <div className="spinner" />
        <p className="loading-text">Loading options…</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner" />
        <p className="loading-text">Finding your ideal collaborators…</p>
        <p className="loading-sub">Evaluating {40} profiles across 7 dimensions</p>
      </div>
    );
  }

  const filteredSkills =
    skillCategory === 'all'
      ? options.skills
      : (options.skills_by_category[skillCategory] ?? []);

  const availableCategories = Object.keys(options.skills_by_category);

  return (
    <div className="form-wizard">
      {/* Progress Bar */}
      <div className="progress-bar">
        {STEPS.map(step => (
          <div key={step.id} className="progress-step">
            <div
              className={`step-circle ${
                currentStep === step.id
                  ? 'active'
                  : currentStep > step.id
                  ? 'completed'
                  : ''
              }`}
            >
              {currentStep > step.id ? '✓' : step.id}
            </div>
            <span className={`step-label ${currentStep === step.id ? 'active' : ''}`}>
              {step.title}
            </span>
          </div>
        ))}
      </div>

      {/* Form Card */}
      <div className="form-card">
        <h2 className="form-title">{STEPS[currentStep - 1].title}</h2>
        <p className="form-description">{STEPS[currentStep - 1].description}</p>

        {error && <div className="form-error-box">{error}</div>}

        {/* Step 1: Project Interests */}
        {currentStep === 1 && (
          <MultiSelect
            label="Project Domains"
            hint="Select all domains relevant to your project"
            options={options.project_interests}
            selected={preferences.project_interests}
            onChange={interests =>
              setPreferences({ ...preferences, project_interests: interests })
            }
          />
        )}

        {/* Step 2: User Skills */}
        {currentStep === 2 && (
          <>
            <div className="category-filter">
              <button
                className={`cat-btn ${skillCategory === 'all' ? 'cat-btn--active' : ''}`}
                onClick={() => setSkillCategory('all')}
              >
                All
              </button>
              {availableCategories.map(cat => (
                <button
                  key={cat}
                  className={`cat-btn ${skillCategory === cat ? 'cat-btn--active' : ''}`}
                  onClick={() => setSkillCategory(cat)}
                >
                  {SKILL_CATEGORIES[cat] ?? cat}
                </button>
              ))}
            </div>
            <MultiSelect
              label="Your Skills"
              hint="Select the skills you already have"
              options={filteredSkills}
              selected={preferences.user_skills}
              onChange={skills => setPreferences({ ...preferences, user_skills: skills })}
            />
          </>
        )}

        {/* Step 3: Needed Skills & Experience */}
        {currentStep === 3 && (
          <>
            <div className="category-filter">
              <button
                className={`cat-btn ${skillCategory === 'all' ? 'cat-btn--active' : ''}`}
                onClick={() => setSkillCategory('all')}
              >
                All
              </button>
              {availableCategories.map(cat => (
                <button
                  key={cat}
                  className={`cat-btn ${skillCategory === cat ? 'cat-btn--active' : ''}`}
                  onClick={() => setSkillCategory(cat)}
                >
                  {SKILL_CATEGORIES[cat] ?? cat}
                </button>
              ))}
            </div>
            <MultiSelect
              label="Skills You Need"
              hint="Select skills you want your collaborator to bring"
              options={filteredSkills}
              selected={preferences.needed_skills}
              onChange={skills => setPreferences({ ...preferences, needed_skills: skills })}
            />

            <div className="form-group">
              <label className="form-label">Preferred Experience Level</label>
              <span className="form-hint">What seniority are you looking for?</span>
              <select
                className="form-select"
                value={preferences.preferred_experience}
                onChange={e =>
                  setPreferences({ ...preferences, preferred_experience: e.target.value })
                }
              >
                <option value="">Any level</option>
                {options.experience_levels.map(level => (
                  <option key={level} value={level}>
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </>
        )}

        {/* Step 4: Working Preferences */}
        {currentStep === 4 && (
          <>
            <div className="form-group">
              <label className="form-label">
                Weekly Availability: <strong>{preferences.weekly_availability} hours</strong>
              </label>
              <span className="form-hint">How many hours per week can you commit?</span>
              <input
                type="range"
                className="form-range"
                min="1"
                max="60"
                value={preferences.weekly_availability}
                onChange={e =>
                  setPreferences({
                    ...preferences,
                    weekly_availability: parseInt(e.target.value) || 20,
                  })
                }
              />
              <div className="range-labels">
                <span>1 hr</span>
                <span>60 hrs</span>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Your Timezone</label>
              <select
                className="form-select"
                value={preferences.timezone}
                onChange={e => setPreferences({ ...preferences, timezone: e.target.value })}
              >
                {options.timezones.map(tz => (
                  <option key={tz} value={tz}>
                    {tz}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Preferred Team Size</label>
              <select
                className="form-select"
                value={preferences.preferred_team_size}
                onChange={e =>
                  setPreferences({ ...preferences, preferred_team_size: e.target.value })
                }
              >
                <option value="">No preference</option>
                {options.team_sizes.map(size => (
                  <option key={size} value={size}>
                    {size}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Collaboration Style</label>
              <select
                className="form-select"
                value={preferences.collaboration_style}
                onChange={e =>
                  setPreferences({ ...preferences, collaboration_style: e.target.value })
                }
              >
                <option value="">No preference</option>
                {options.collaboration_styles.map(style => (
                  <option key={style} value={style}>
                    {style.charAt(0).toUpperCase() + style.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Communication Preference</label>
              <select
                className="form-select"
                value={preferences.communication_preference}
                onChange={e =>
                  setPreferences({ ...preferences, communication_preference: e.target.value })
                }
              >
                <option value="">No preference</option>
                {options.communication_preferences.map(pref => (
                  <option key={pref} value={pref}>
                    {pref.charAt(0).toUpperCase() + pref.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </>
        )}

        {/* Step 5: Review */}
        {currentStep === 5 && (
          <div className="review-summary">
            <div className="review-row">
              <span className="review-key">Project Domains</span>
              <span className="review-val">
                {preferences.project_interests.length > 0
                  ? preferences.project_interests.join(', ')
                  : 'None selected'}
              </span>
            </div>
            <div className="review-row">
              <span className="review-key">Your Skills</span>
              <span className="review-val">
                {preferences.user_skills.length > 0
                  ? preferences.user_skills.join(', ')
                  : 'None selected'}
              </span>
            </div>
            <div className="review-row">
              <span className="review-key">Skills Needed</span>
              <span className="review-val">
                {preferences.needed_skills.length > 0
                  ? preferences.needed_skills.join(', ')
                  : 'None selected'}
              </span>
            </div>
            <div className="review-row">
              <span className="review-key">Experience Preference</span>
              <span className="review-val">{preferences.preferred_experience || 'Any'}</span>
            </div>
            <div className="review-row">
              <span className="review-key">Weekly Availability</span>
              <span className="review-val">{preferences.weekly_availability} hours</span>
            </div>
            <div className="review-row">
              <span className="review-key">Timezone</span>
              <span className="review-val">{preferences.timezone}</span>
            </div>
            <div className="review-row">
              <span className="review-key">Team Size</span>
              <span className="review-val">{preferences.preferred_team_size || 'No preference'}</span>
            </div>
            <div className="review-row">
              <span className="review-key">Collaboration Style</span>
              <span className="review-val">
                {preferences.collaboration_style || 'No preference'}
              </span>
            </div>
            <div className="review-row">
              <span className="review-key">Communication</span>
              <span className="review-val">
                {preferences.communication_preference || 'No preference'}
              </span>
            </div>
            <p className="review-note">
              The algorithm will evaluate all 40 profiles across 7 weighted dimensions and
              return the top 10 ranked matches with full explanations.
            </p>
          </div>
        )}

        {/* Form Actions */}
        <div className="form-actions">
          <button className="btn btn-secondary" onClick={handleBack}>
            {currentStep === 1 ? '← Home' : '← Back'}
          </button>

          {currentStep < STEPS.length ? (
            <button className="btn btn-primary" onClick={handleNext}>
              Next →
            </button>
          ) : (
            <button className="btn btn-primary" onClick={handleSubmit}>
              Find My Matches
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default MatchingWizard;

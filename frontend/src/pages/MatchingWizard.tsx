import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { MatchPreferences, Options, MatchResponse } from '../types';
import MultiSelect from '../components/MultiSelect';

interface MatchingWizardProps {
  onComplete: (results: MatchResponse) => void;
}

const STEPS = [
  { id: 1, title: 'Your Project', description: 'What are you working on?' },
  { id: 2, title: 'Your Skills', description: 'What skills do you bring?' },
  { id: 3, title: 'Ideal Collaborator', description: 'What do you need?' },
  { id: 4, title: 'Working Preferences', description: 'How do you like to work?' },
  { id: 5, title: 'Review & Match', description: 'Confirm your preferences' },
];

function MatchingWizard({ onComplete }: MatchingWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [options, setOptions] = useState<Options | null>(null);
  
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
    loadOptions();
  }, []);

  const loadOptions = async () => {
    try {
      const data = await api.getOptions();
      setOptions(data);
    } catch (err) {
      setError('Failed to load options. Please refresh the page.');
    }
  };

  const handleNext = () => {
    if (currentStep < STEPS.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };


  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const results = await api.findMatches(preferences);
      onComplete(results);
    } catch (err: any) {
      setError(err.message || 'Failed to find matches. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!options) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p className="loading-text">Loading...</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p className="loading-text">Finding your ideal collaborators...</p>
      </div>
    );
  }

  return (
    <div className="form-wizard">
      {/* Progress Bar */}
      <div className="progress-bar">
        {STEPS.map(step => (
          <div key={step.id} className="progress-step">
            <div
              className={`step-circle ${
                currentStep === step.id ? 'active' : currentStep > step.id ? 'completed' : ''
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

        {error && (
          <div className="form-error" style={{ marginBottom: '1rem', padding: '0.75rem', background: '#fee', borderRadius: '0.5rem' }}>
            {error}
          </div>
        )}

        {/* Step 1: Project Interests */}
        {currentStep === 1 && (
          <MultiSelect
            label="Project Interests"
            hint="Select the domains you're interested in working on"
            options={options.project_interests}
            selected={preferences.project_interests}
            onChange={interests => setPreferences({ ...preferences, project_interests: interests })}
          />
        )}

        {/* Step 2: User Skills */}
        {currentStep === 2 && (
          <MultiSelect
            label="Your Skills"
            hint="Select the skills you already have"
            options={options.skills}
            selected={preferences.user_skills}
            onChange={skills => setPreferences({ ...preferences, user_skills: skills })}
          />
        )}

        {/* Step 3: Needed Skills & Experience */}
        {currentStep === 3 && (
          <>
            <MultiSelect
              label="Skills You Need"
              hint="Select skills you're looking for in a collaborator"
              options={options.skills}
              selected={preferences.needed_skills}
              onChange={skills => setPreferences({ ...preferences, needed_skills: skills })}
            />

            <div className="form-group">
              <label className="form-label">Preferred Experience Level</label>
              <span className="form-hint">What experience level are you looking for?</span>
              <select
                className="form-select"
                value={preferences.preferred_experience}
                onChange={e => setPreferences({ ...preferences, preferred_experience: e.target.value })}
              >
                <option value="">Any level</option>
                {options.experience_levels.map(level => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
            </div>
          </>
        )}


        {/* Step 4: Working Preferences */}
        {currentStep === 4 && (
          <>
            <div className="form-group">
              <label className="form-label">Weekly Availability (hours)</label>
              <span className="form-hint">How many hours per week can you commit?</span>
              <input
                type="number"
                className="form-input"
                min="1"
                max="60"
                value={preferences.weekly_availability}
                onChange={e => setPreferences({ ...preferences, weekly_availability: parseInt(e.target.value) || 20 })}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Your Timezone</label>
              <select
                className="form-select"
                value={preferences.timezone}
                onChange={e => setPreferences({ ...preferences, timezone: e.target.value })}
              >
                {options.timezones.map(tz => (
                  <option key={tz} value={tz}>{tz}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Preferred Team Size</label>
              <select
                className="form-select"
                value={preferences.preferred_team_size}
                onChange={e => setPreferences({ ...preferences, preferred_team_size: e.target.value })}
              >
                <option value="">No preference</option>
                {options.team_sizes.map(size => (
                  <option key={size} value={size}>{size}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Collaboration Style</label>
              <select
                className="form-select"
                value={preferences.collaboration_style}
                onChange={e => setPreferences({ ...preferences, collaboration_style: e.target.value })}
              >
                <option value="">No preference</option>
                {options.collaboration_styles.map(style => (
                  <option key={style} value={style}>{style}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Communication Preference</label>
              <select
                className="form-select"
                value={preferences.communication_preference}
                onChange={e => setPreferences({ ...preferences, communication_preference: e.target.value })}
              >
                <option value="">No preference</option>
                {options.communication_preferences.map(pref => (
                  <option key={pref} value={pref}>{pref}</option>
                ))}
              </select>
            </div>
          </>
        )}


        {/* Step 5: Review */}
        {currentStep === 5 && (
          <div style={{ fontSize: '0.95rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>Review Your Preferences</h3>
            
            <div style={{ marginBottom: '1rem' }}>
              <strong>Project Interests:</strong>{' '}
              {preferences.project_interests.length > 0 ? preferences.project_interests.join(', ') : 'None selected'}
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <strong>Your Skills:</strong>{' '}
              {preferences.user_skills.length > 0 ? preferences.user_skills.join(', ') : 'None selected'}
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <strong>Skills Needed:</strong>{' '}
              {preferences.needed_skills.length > 0 ? preferences.needed_skills.join(', ') : 'None selected'}
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <strong>Experience Preference:</strong> {preferences.preferred_experience || 'Any'}
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <strong>Weekly Availability:</strong> {preferences.weekly_availability} hours
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <strong>Timezone:</strong> {preferences.timezone}
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <strong>Team Size:</strong> {preferences.preferred_team_size || 'No preference'}
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <strong>Collaboration Style:</strong> {preferences.collaboration_style || 'No preference'}
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <strong>Communication:</strong> {preferences.communication_preference || 'No preference'}
            </div>
          </div>
        )}

        {/* Form Actions */}
        <div className="form-actions">
          <button
            className="btn btn-secondary"
            onClick={handleBack}
            disabled={currentStep === 1}
          >
            Back
          </button>

          {currentStep < STEPS.length ? (
            <button className="btn btn-primary" onClick={handleNext}>
              Next
            </button>
          ) : (
            <button className="btn btn-primary" onClick={handleSubmit}>
              Find Matches
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default MatchingWizard;

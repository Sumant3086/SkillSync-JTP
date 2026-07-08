import { useState, useEffect } from 'react';
import Landing from './pages/Landing';
import MatchingWizard from './pages/MatchingWizard';
import Results from './pages/Results';
import { MatchResponse, Options } from './types';
import { api } from './services/api';
import './styles/App.css';

type View = 'landing' | 'wizard' | 'results';

function App() {
  const [view, setView] = useState<View>('landing');
  const [matchResults, setMatchResults] = useState<MatchResponse | null>(null);
  const [options, setOptions] = useState<Options | null>(null);
  const [optionsError, setOptionsError] = useState<string | null>(null);

  // Pre-fetch options on mount so the backend wakes up while the user reads
  // the landing page — eliminates the cold-start wait on the wizard screen.
  useEffect(() => {
    api.getOptions()
      .then(setOptions)
      .catch(() => setOptionsError('Failed to load options. Please refresh the page.'));
  }, []);

  const handleStartMatching = () => setView('wizard');

  const handleMatchComplete = (results: MatchResponse) => {
    setMatchResults(results);
    setView('results');
  };

  const handleNewSearch = () => {
    setMatchResults(null);
    setView('wizard');
  };

  const handleBackToHome = () => {
    setMatchResults(null);
    setView('landing');
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-container">
          <button className="logo-btn" onClick={handleBackToHome}>
            SkillSync
          </button>
          <span className="tagline">Explainable Collaborator Matching</span>
        </div>
      </header>

      <main className="container">
        {view === 'landing' && <Landing onStart={handleStartMatching} />}
        {view === 'wizard' && (
          <MatchingWizard
            options={options}
            optionsError={optionsError}
            onComplete={handleMatchComplete}
            onBack={handleBackToHome}
          />
        )}
        {view === 'results' && matchResults && (
          <Results
            results={matchResults}
            onNewSearch={handleNewSearch}
            onBackToHome={handleBackToHome}
          />
        )}
      </main>

      <footer className="footer">
        <div className="footer-content">
          <p>SkillSync — Explainable Collaborator Matching Platform</p>
          <p>JTP 2026 Project Round &nbsp;·&nbsp; Weighted multi-criteria algorithm &nbsp;·&nbsp; 40 synthetic profiles</p>
        </div>
      </footer>
    </div>
  );
}

export default App;

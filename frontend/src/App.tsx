import { useState } from 'react';
import Landing from './pages/Landing';
import MatchingWizard from './pages/MatchingWizard';
import Results from './pages/Results';
import { MatchResponse } from './types';
import './styles/App.css';

type View = 'landing' | 'wizard' | 'results';

function App() {
  const [view, setView] = useState<View>('landing');
  const [matchResults, setMatchResults] = useState<MatchResponse | null>(null);

  const handleStartMatching = () => {
    setView('wizard');
  };

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
          <a href="#" className="logo" onClick={handleBackToHome}>
            SkillSync
          </a>
          <span className="tagline">Find the right collaborator</span>
        </div>
      </header>

      <main className="container">
        {view === 'landing' && <Landing onStart={handleStartMatching} />}
        {view === 'wizard' && <MatchingWizard onComplete={handleMatchComplete} />}
        {view === 'results' && matchResults && (
          <Results results={matchResults} onNewSearch={handleNewSearch} />
        )}
      </main>

      <footer className="footer">
        <div className="footer-content">
          <p>SkillSync - Explainable Collaborator Matching Platform</p>
          <p>Developed for the JTP 2026 Project Round</p>
        </div>
      </footer>
    </div>
  );
}

export default App;

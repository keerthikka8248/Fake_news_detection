import React from 'react';
import DetectionForm from './components/DetectionForm';
import './App.css';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>🕵‍♂ Fake News Detector</h1>
        <p>Analyze content, URLs, or uploaded files to detect misinformation.</p>
      </header>

      <main className="app-main">
        <DetectionForm />
      </main>

      <footer className="app-footer">
        <p>© 2025 Fake News Detection Tool. Built with ❤ using React.</p>
      </footer>
    </div>
  );
}

export default App;
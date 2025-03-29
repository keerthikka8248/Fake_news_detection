import React, { useState } from 'react';
import './DetectionForm.css';

const DetectionForm = () => {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const detectNews = async () => {
    if (!text.trim() || text.split(' ').length < 5) {
      setError('Please enter at least 5 words');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || errorData.message || 'API request failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="detection-container">
      <h1>Fake News Detector</h1>
      
      <div className="input-section">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste news article or text content here (minimum 5 words)..."
          rows={8}
        />
        <button 
          onClick={detectNews}
          disabled={loading || text.split(' ').length < 5}
        >
          {loading ? 'Analyzing...' : 'Detect'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className={`result ${result.prediction.toLowerCase()}`}>
          <h2>
            {result.prediction === 'Fake' ? '⚠ Fake News' : '✅ Real News'} 
            <span>({Math.round(result.confidence * 100)}% confidence)</span>
          </h2>
          
          <div className="model-results">
            <h3>Model Details:</h3>
            <div className="model">
              <strong>Logistic Regression:</strong>
              <span>{result.models.logistic.prediction} ({Math.round(result.models.logistic.confidence * 100)}%)</span>
            </div>
            <div className="model">
              <strong>Random Forest:</strong>
              <span>{result.models.random_forest.prediction} ({Math.round(result.models.random_forest.confidence * 100)}%)</span>
            </div>
          </div>

          {result.processed_text && (
            <div className="processed-text">
              <h3>Processed Text Preview:</h3>
              <p>{result.processed_text}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DetectionForm;
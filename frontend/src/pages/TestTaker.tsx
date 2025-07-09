import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { TestEngine } from '../lib/test-engine';
import { getTestByKey } from '../lib/test-library';
import { TestTemplate, TestQuestion, type TestResults } from '../types/tests';

interface TestTakerState {
  engine: TestEngine | null;
  currentQuestion: TestQuestion | null;
  isLoading: boolean;
  error: string | null;
  showResults: boolean;
  results: TestResults | null;
  startTime: number;
}

export default function TestTaker() {
  const { testKey } = useParams<{ testKey: string }>();
  const navigate = useNavigate();
  const responseTimeRef = useRef<number>(0);
  
  const [state, setState] = useState<TestTakerState>({
    engine: null,
    currentQuestion: null,
    isLoading: true,
    error: null,
    showResults: false,
    results: null,
    startTime: 0
  });

  // Initialize test engine
  useEffect(() => {
    if (!testKey) {
      setState(prev => ({ ...prev, error: 'No test specified', isLoading: false }));
      return;
    }

    const template = getTestByKey(testKey);
    if (!template) {
      setState(prev => ({ ...prev, error: 'Test not found', isLoading: false }));
      return;
    }

    const engine = new TestEngine(template);
    const currentQuestion = engine.getCurrentQuestion();
    
    setState(prev => ({
      ...prev,
      engine,
      currentQuestion,
      isLoading: false,
      startTime: Date.now()
    }));

    responseTimeRef.current = Date.now();
  }, [testKey]);

  const handleResponse = useCallback((response: number | string) => {
    if (!state.engine) return;

    const responseTime = Date.now() - responseTimeRef.current;
    
    try {
      const success = state.engine.answerQuestion(response, responseTime);
      if (!success) {
        setState(prev => ({ ...prev, error: 'Failed to record response' }));
        return;
      }

      // Check if test is complete
      if (state.engine.isComplete()) {
        const results = state.engine.calculateResults();
        setState(prev => ({
          ...prev,
          showResults: true,
          results,
          currentQuestion: null
        }));
      } else {
        // Move to next question
        const nextQuestion = state.engine.getCurrentQuestion();
        setState(prev => ({
          ...prev,
          currentQuestion: nextQuestion
        }));
        responseTimeRef.current = Date.now();
      }
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'An error occurred' 
      }));
    }
  }, [state.engine]);

  const handleSkip = useCallback(() => {
    if (!state.engine) return;

    const success = state.engine.skipQuestion();
    if (!success) {
      setState(prev => ({ ...prev, error: 'Cannot skip required question' }));
      return;
    }

    const nextQuestion = state.engine.getCurrentQuestion();
    setState(prev => ({
      ...prev,
      currentQuestion: nextQuestion
    }));
    responseTimeRef.current = Date.now();
  }, [state.engine]);

  const handlePrevious = useCallback(() => {
    if (!state.engine) return;

    const success = state.engine.previousQuestion();
    if (!success) return;

    const prevQuestion = state.engine.getCurrentQuestion();
    setState(prev => ({
      ...prev,
      currentQuestion: prevQuestion,
      showResults: false,
      results: null
    }));
    responseTimeRef.current = Date.now();
  }, [state.engine]);

  const handleRestart = useCallback(() => {
    if (!testKey) return;
    
    const template = getTestByKey(testKey);
    if (!template) return;

    const engine = new TestEngine(template);
    const currentQuestion = engine.getCurrentQuestion();
    
    setState({
      engine,
      currentQuestion,
      isLoading: false,
      error: null,
      showResults: false,
      results: null,
      startTime: Date.now()
    });

    responseTimeRef.current = Date.now();
  }, [testKey]);

  const getProgress = useCallback(() => {
    return state.engine?.getProgress() || 0;
  }, [state.engine]);

  const getQuestionNumber = useCallback(() => {
    if (!state.engine) return { current: 0, total: 0 };
    const visibleQuestions = state.engine.getVisibleQuestions();
    const current = Math.max(0, state.engine.getSession().current_question);
    return { current, total: visibleQuestions.length };
  }, [state.engine]);

  if (state.isLoading) {
    return (
      <div className="test-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading assessment...</p>
        </div>
      </div>
    );
  }

  if (state.error) {
    return (
      <div className="test-container">
        <div className="error-message">
          <h2>Error</h2>
          <p>{state.error}</p>
          <button onClick={() => navigate('/')} className="btn-primary">
            Return Home
          </button>
        </div>
      </div>
    );
  }

  if (state.showResults && state.results) {
    return <TestResults results={state.results} onRestart={handleRestart} onHome={() => navigate('/')} />;
  }

  if (!state.currentQuestion) {
    return (
      <div className="test-container">
        <div className="test-complete">
          <h2>Assessment Complete</h2>
          <p>Processing your results...</p>
        </div>
      </div>
    );
  }

  const progress = getProgress();
  const questionNumbers = getQuestionNumber();
  const metadata = state.engine?.getMetadata();

  return (
    <div className="test-container">
      <style>{testTakerStyles}</style>
      
      {/* Header */}
      <div className="test-header">
        <div className="test-info">
          <h1>{metadata?.name}</h1>
          <p className="test-description">{metadata?.description}</p>
        </div>
        
        <div className="progress-section">
          <div className="progress-info">
            <span>Question {questionNumbers.current + 1} of {questionNumbers.total}</span>
            <span>{progress}% Complete</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Question */}
      <div className="question-container">
        <QuestionComponent
          question={state.currentQuestion}
          onResponse={handleResponse}
          onSkip={state.currentQuestion.required ? undefined : handleSkip}
        />
      </div>

      {/* Navigation */}
      <div className="navigation-container">
        <button 
          onClick={handlePrevious}
          className="btn-secondary"
          disabled={questionNumbers.current === 0}
        >
          Previous
        </button>
        
        <div className="nav-info">
          <span>
            {metadata?.branching_enabled && 
              "Questions may vary based on your responses"
            }
          </span>
        </div>

        <button 
          onClick={() => navigate('/')}
          className="btn-outline"
        >
          Exit Assessment
        </button>
      </div>
    </div>
  );
}

interface QuestionComponentProps {
  question: TestQuestion;
  onResponse: (response: number | string) => void;
  onSkip?: () => void;
}

function QuestionComponent({ question, onResponse, onSkip }: QuestionComponentProps) {
  const [selectedValue, setSelectedValue] = useState<number | string | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    setSelectedValue(null);
    setIsAnimating(true);
    const timer = setTimeout(() => setIsAnimating(false), 300);
    return () => clearTimeout(timer);
  }, [question.id]);

  const handleSubmit = () => {
    if (selectedValue !== null) {
      onResponse(selectedValue);
    }
  };

  const renderQuestionInput = () => {
    switch (question.question_type) {
      case 'likert':
        return (
          <div className="likert-scale">
            {question.options?.map((option, index) => (
              <label key={index} className="likert-option">
                <input
                  type="radio"
                  name={`question-${question.id}`}
                  value={index}
                  checked={selectedValue === index}
                  onChange={(e) => setSelectedValue(parseInt(e.target.value))}
                />
                <span className="likert-label">{option}</span>
              </label>
            ))}
          </div>
        );

      case 'scale':
        return (
          <div className="scale-container">
            <div className="scale-labels">
              <span>{question.min_value}</span>
              <span>{question.max_value}</span>
            </div>
            <input
              type="range"
              min={question.min_value}
              max={question.max_value}
              value={selectedValue as number || question.min_value}
              onChange={(e) => setSelectedValue(parseInt(e.target.value))}
              className="scale-slider"
            />
            <div className="scale-value">
              Selected: {selectedValue || question.min_value}
            </div>
          </div>
        );

      case 'choice':
        return (
          <div className="choice-options">
            {question.options?.map((option, index) => (
              <button
                key={index}
                className={`choice-button ${selectedValue === index ? 'selected' : ''}`}
                onClick={() => setSelectedValue(index)}
              >
                {option}
              </button>
            ))}
          </div>
        );

      case 'boolean':
        return (
          <div className="boolean-options">
            <button
              className={`boolean-button ${selectedValue === 1 ? 'selected' : ''}`}
              onClick={() => setSelectedValue(1)}
            >
              Yes
            </button>
            <button
              className={`boolean-button ${selectedValue === 0 ? 'selected' : ''}`}
              onClick={() => setSelectedValue(0)}
            >
              No
            </button>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className={`question-card ${isAnimating ? 'animating' : ''}`}>
      <div className="question-header">
        <h2 className="question-text">{question.text}</h2>
        {!question.required && (
          <span className="optional-badge">Optional</span>
        )}
      </div>

      <div className="question-input">
        {renderQuestionInput()}
      </div>

      <div className="question-actions">
        {onSkip && (
          <button onClick={onSkip} className="btn-outline">
            Skip
          </button>
        )}
        
        <button 
          onClick={handleSubmit}
          disabled={selectedValue === null}
          className="btn-primary"
        >
          {question.required ? 'Continue' : 'Next'}
        </button>
      </div>
    </div>
  );
}

interface TestResultsProps {
  results: TestResults;
  onRestart: () => void;
  onHome: () => void;
}

function TestResults({ results, onRestart, onHome }: TestResultsProps) {
  return (
    <div className="results-container">
      <style>{resultsStyles}</style>
      
      <div className="results-header">
        <h1>Assessment Results</h1>
        <div className="score-display">
          <div className="main-score">
            <span className="score-value">{Math.round(results.normalized_score)}</span>
            <span className="score-unit">%</span>
          </div>
          <div className="score-interpretation">
            <h3>{results.interpretation}</h3>
            <p>{results.detailed_feedback}</p>
          </div>
        </div>
      </div>

      {results.dimension_scores && (
        <div className="dimension-scores">
          <h3>Detailed Breakdown</h3>
          <div className="dimensions-grid">
            {Object.entries(results.dimension_scores).map(([dimension, score]) => (
              <div key={dimension} className="dimension-item">
                <div className="dimension-name">{dimension}</div>
                <div className="dimension-bar">
                  <div 
                    className="dimension-fill" 
                    style={{ width: `${(score / 5) * 100}%` }}
                  ></div>
                </div>
                <div className="dimension-score">{score.toFixed(1)}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="recommendations-section">
        <h3>Recommendations</h3>
        <ul className="recommendations-list">
          {results.recommendations.map((rec, index) => (
            <li key={index}>{rec}</li>
          ))}
        </ul>
      </div>

      {results.risk_level !== 'low' && (
        <div className={`risk-alert risk-${results.risk_level}`}>
          <h4>Important Notice</h4>
          <p>
            Your responses indicate {results.risk_level} risk levels. 
            {results.follow_up_suggested && " We recommend speaking with a mental health professional."}
          </p>
        </div>
      )}

      <div className="results-actions">
        <button onClick={onRestart} className="btn-secondary">
          Retake Assessment
        </button>
        <button onClick={onHome} className="btn-primary">
          Return to Dashboard
        </button>
      </div>
    </div>
  );
}

const testTakerStyles = `
  .test-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  .test-header {
    background: white;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }

  .test-info h1 {
    margin: 0 0 8px 0;
    color: #1a1a1a;
    font-size: 24px;
    font-weight: 600;
  }

  .test-description {
    color: #666;
    margin: 0 0 20px 0;
    line-height: 1.5;
  }

  .progress-section {
    border-top: 1px solid #eee;
    padding-top: 20px;
  }

  .progress-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 14px;
    color: #666;
  }

  .progress-bar {
    height: 8px;
    background: #f0f0f0;
    border-radius: 4px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #4CAF50, #45a049);
    transition: width 0.3s ease;
  }

  .question-container {
    margin-bottom: 24px;
  }

  .question-card {
    background: white;
    border-radius: 12px;
    padding: 32px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
  }

  .question-card.animating {
    opacity: 0.7;
    transform: translateX(10px);
  }

  .question-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
  }

  .question-text {
    font-size: 20px;
    font-weight: 500;
    line-height: 1.4;
    margin: 0;
    color: #1a1a1a;
    flex: 1;
  }

  .optional-badge {
    background: #e3f2fd;
    color: #1976d2;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    margin-left: 16px;
  }

  .question-input {
    margin-bottom: 32px;
  }

  .likert-scale {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .likert-option {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .likert-option:hover {
    border-color: #4CAF50;
    background: #f8fff8;
  }

  .likert-option input[type="radio"] {
    margin-right: 12px;
    accent-color: #4CAF50;
  }

  .likert-option input[type="radio"]:checked + .likert-label {
    font-weight: 500;
    color: #4CAF50;
  }

  .choice-options {
    display: grid;
    gap: 12px;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }

  .choice-button {
    padding: 16px 20px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 16px;
  }

  .choice-button:hover {
    border-color: #4CAF50;
    background: #f8fff8;
  }

  .choice-button.selected {
    border-color: #4CAF50;
    background: #4CAF50;
    color: white;
  }

  .boolean-options {
    display: flex;
    gap: 16px;
    justify-content: center;
  }

  .boolean-button {
    padding: 16px 32px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 18px;
    font-weight: 500;
    min-width: 120px;
  }

  .boolean-button:hover {
    border-color: #4CAF50;
    background: #f8fff8;
  }

  .boolean-button.selected {
    border-color: #4CAF50;
    background: #4CAF50;
    color: white;
  }

  .scale-container {
    text-align: center;
  }

  .scale-labels {
    display: flex;
    justify-content: space-between;
    margin-bottom: 16px;
    font-weight: 500;
    color: #666;
  }

  .scale-slider {
    width: 100%;
    height: 8px;
    border-radius: 4px;
    background: #e0e0e0;
    outline: none;
    margin-bottom: 16px;
    accent-color: #4CAF50;
  }

  .scale-value {
    font-size: 18px;
    font-weight: 500;
    color: #4CAF50;
  }

  .question-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .navigation-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: white;
    border-radius: 12px;
    padding: 20px 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }

  .nav-info {
    font-size: 14px;
    color: #666;
    font-style: italic;
  }

  .btn-primary {
    background: #4CAF50;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s ease;
  }

  .btn-primary:hover:not(:disabled) {
    background: #45a049;
  }

  .btn-primary:disabled {
    background: #ccc;
    cursor: not-allowed;
  }

  .btn-secondary {
    background: #f5f5f5;
    color: #333;
    border: 2px solid #e0e0e0;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-secondary:hover:not(:disabled) {
    background: #e0e0e0;
    border-color: #ccc;
  }

  .btn-secondary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-outline {
    background: transparent;
    color: #666;
    border: 2px solid #e0e0e0;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-outline:hover {
    border-color: #ccc;
    color: #333;
  }

  .loading-spinner {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f0f0f0;
    border-top: 4px solid #4CAF50;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .error-message {
    text-align: center;
    padding: 40px 20px;
  }

  .error-message h2 {
    color: #d32f2f;
    margin-bottom: 16px;
  }

  .test-complete {
    text-align: center;
    padding: 60px 20px;
  }
`;

const resultsStyles = `
  .results-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }

  .results-header {
    background: white;
    border-radius: 12px;
    padding: 32px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    text-align: center;
  }

  .results-header h1 {
    margin: 0 0 24px 0;
    color: #1a1a1a;
    font-size: 28px;
    font-weight: 600;
  }

  .score-display {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 32px;
    flex-wrap: wrap;
  }

  .main-score {
    display: flex;
    align-items: baseline;
    gap: 4px;
  }

  .score-value {
    font-size: 64px;
    font-weight: 700;
    color: #4CAF50;
    line-height: 1;
  }

  .score-unit {
    font-size: 24px;
    color: #666;
    font-weight: 500;
  }

  .score-interpretation h3 {
    margin: 0 0 8px 0;
    color: #1a1a1a;
    font-size: 20px;
  }

  .score-interpretation p {
    margin: 0;
    color: #666;
    font-size: 16px;
    line-height: 1.5;
  }

  .dimension-scores {
    background: white;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }

  .dimension-scores h3 {
    margin: 0 0 20px 0;
    color: #1a1a1a;
    font-size: 18px;
    font-weight: 600;
  }

  .dimensions-grid {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .dimension-item {
    display: grid;
    grid-template-columns: 1fr 2fr auto;
    gap: 16px;
    align-items: center;
  }

  .dimension-name {
    font-weight: 500;
    color: #333;
  }

  .dimension-bar {
    height: 8px;
    background: #f0f0f0;
    border-radius: 4px;
    overflow: hidden;
  }

  .dimension-fill {
    height: 100%;
    background: linear-gradient(90deg, #4CAF50, #45a049);
    transition: width 0.5s ease;
  }

  .dimension-score {
    font-weight: 600;
    color: #4CAF50;
    min-width: 40px;
    text-align: right;
  }

  .recommendations-section {
    background: white;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }

  .recommendations-section h3 {
    margin: 0 0 16px 0;
    color: #1a1a1a;
    font-size: 18px;
    font-weight: 600;
  }

  .recommendations-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .recommendations-list li {
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;
    position: relative;
    padding-left: 24px;
  }

  .recommendations-list li:before {
    content: "✓";
    position: absolute;
    left: 0;
    color: #4CAF50;
    font-weight: bold;
  }

  .recommendations-list li:last-child {
    border-bottom: none;
  }

  .risk-alert {
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
    border-left: 4px solid;
  }

  .risk-moderate {
    background: #fff3cd;
    border-color: #ffc107;
    color: #856404;
  }

  .risk-high {
    background: #f8d7da;
    border-color: #dc3545;
    color: #721c24;
  }

  .risk-alert h4 {
    margin: 0 0 8px 0;
    font-size: 16px;
    font-weight: 600;
  }

  .risk-alert p {
    margin: 0;
    line-height: 1.5;
  }

  .results-actions {
    display: flex;
    gap: 16px;
    justify-content: center;
  }
`;
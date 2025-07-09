import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { getAllTests, getTestsByCategory } from '../lib/test-library';
import { TestTemplate } from '../types/tests';

type CategoryFilter = 'all' | 'wellbeing' | 'personality' | 'cognitive' | 'stress' | 'engagement';

export default function TestLibrary() {
  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const getFilteredTests = (): TestTemplate[] => {
    let tests = categoryFilter === 'all' ? getAllTests() : getTestsByCategory(categoryFilter);
    
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      tests = tests.filter(test => 
        test.name.toLowerCase().includes(query) ||
        test.description?.toLowerCase().includes(query) ||
        test.key.toLowerCase().includes(query)
      );
    }
    
    return tests;
  };

  const getCategoryIcon = (category: TestTemplate['category']): string => {
    const icons = {
      wellbeing: '🧠',
      personality: '🎭',
      cognitive: '🧩',
      stress: '⚡',
      engagement: '💼'
    };
    return icons[category] || '📋';
  };

  const getCategoryColor = (category: TestTemplate['category']): string => {
    const colors = {
      wellbeing: '#4CAF50',
      personality: '#9C27B0',
      cognitive: '#2196F3',
      stress: '#FF9800',
      engagement: '#607D8B'
    };
    return colors[category] || '#666';
  };

  const getDifficultyLevel = (duration: number): { level: string; color: string } => {
    if (duration <= 3) return { level: 'Quick', color: '#4CAF50' };
    if (duration <= 8) return { level: 'Medium', color: '#FF9800' };
    return { level: 'Comprehensive', color: '#f44336' };
  };

  const filteredTests = getFilteredTests();
  const categories: { key: CategoryFilter; label: string; count: number }[] = [
    { key: 'all', label: 'All Assessments', count: getAllTests().length },
    { key: 'wellbeing', label: 'Wellbeing', count: getTestsByCategory('wellbeing').length },
    { key: 'personality', label: 'Personality', count: getTestsByCategory('personality').length },
    { key: 'cognitive', label: 'Cognitive', count: getTestsByCategory('cognitive').length },
    { key: 'stress', label: 'Stress & Burnout', count: getTestsByCategory('stress').length },
    { key: 'engagement', label: 'Workplace', count: getTestsByCategory('engagement').length },
  ];

  return (
    <div className="test-library-container">
      <style>{testLibraryStyles}</style>
      
      {/* Header */}
      <div className="library-header">
        <div className="header-content">
          <h1>Assessment Library</h1>
          <p>Comprehensive psychometric assessments for employee wellbeing and development</p>
        </div>
        
        <div className="library-stats">
          <div className="stat-item">
            <span className="stat-number">{getAllTests().length}</span>
            <span className="stat-label">Assessments</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">5</span>
            <span className="stat-label">Categories</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">2-20</span>
            <span className="stat-label">Minutes</span>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="library-controls">
        <div className="search-container">
          <input
            type="text"
            placeholder="Search assessments..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <span className="search-icon">🔍</span>
        </div>

        <div className="category-filters">
          {categories.map(category => (
            <button
              key={category.key}
              onClick={() => setCategoryFilter(category.key)}
              className={`category-filter ${categoryFilter === category.key ? 'active' : ''}`}
            >
              {category.label}
              <span className="category-count">{category.count}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Test Grid */}
      <div className="tests-grid">
        {filteredTests.length === 0 ? (
          <div className="no-results">
            <h3>No assessments found</h3>
            <p>Try adjusting your search or filter criteria</p>
          </div>
        ) : (
          filteredTests.map(test => {
            const difficulty = getDifficultyLevel(test.duration_minutes);
            const categoryColor = getCategoryColor(test.category);
            
            return (
              <div key={test.key} className="test-card">
                <div className="test-card-header">
                  <div className="test-category" style={{ backgroundColor: categoryColor }}>
                    <span className="category-icon">{getCategoryIcon(test.category)}</span>
                    <span className="category-name">{test.category}</span>
                  </div>
                  <div className="test-difficulty" style={{ color: difficulty.color }}>
                    {difficulty.level}
                  </div>
                </div>

                <div className="test-card-content">
                  <h3 className="test-title">{test.name}</h3>
                  <p className="test-description">{test.description}</p>
                  
                  <div className="test-metadata">
                    <div className="metadata-item">
                      <span className="metadata-icon">⏱️</span>
                      <span>{test.duration_minutes} min</span>
                    </div>
                    <div className="metadata-item">
                      <span className="metadata-icon">❓</span>
                      <span>{test.questions.length} questions</span>
                    </div>
                    {test.branching_enabled && (
                      <div className="metadata-item">
                        <span className="metadata-icon">🔀</span>
                        <span>Adaptive</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="test-card-actions">
                  <Link 
                    to={`/test/${test.key}`} 
                    className="btn-primary"
                  >
                    Start Assessment
                  </Link>
                  <button className="btn-secondary">
                    Learn More
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Featured Section */}
      <div className="featured-section">
        <h2>Recommended Assessments</h2>
        <div className="featured-grid">
          <div className="featured-card">
            <div className="featured-icon">🧠</div>
            <h3>Mental Wellbeing Suite</h3>
            <p>Comprehensive mental health screening including WHO-5, GAD-7, and PHQ-9</p>
            <div className="featured-tests">
              <span>WHO-5</span>
              <span>GAD-7</span>
              <span>PHQ-9</span>
            </div>
          </div>
          
          <div className="featured-card">
            <div className="featured-icon">🎭</div>
            <h3>Personality Profiling</h3>
            <p>Understand behavioral patterns and work styles with Big Five and DISC assessments</p>
            <div className="featured-tests">
              <span>Big Five</span>
              <span>DISC</span>
              <span>MBTI</span>
            </div>
          </div>
          
          <div className="featured-card">
            <div className="featured-icon">⚡</div>
            <h3>Stress & Burnout</h3>
            <p>Identify stress levels and burnout risk with validated clinical instruments</p>
            <div className="featured-tests">
              <span>PSS</span>
              <span>Maslach</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const testLibraryStyles = `
  .test-library-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  .library-header {
    background: linear-gradient(135deg, #4CAF50, #45a049);
    color: white;
    border-radius: 16px;
    padding: 40px;
    margin-bottom: 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 24px;
  }

  .header-content h1 {
    margin: 0 0 8px 0;
    font-size: 32px;
    font-weight: 700;
  }

  .header-content p {
    margin: 0;
    font-size: 16px;
    opacity: 0.9;
    line-height: 1.5;
  }

  .library-stats {
    display: flex;
    gap: 32px;
  }

  .stat-item {
    text-align: center;
  }

  .stat-number {
    display: block;
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 4px;
  }

  .stat-label {
    font-size: 14px;
    opacity: 0.8;
  }

  .library-controls {
    background: white;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 32px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }

  .search-container {
    position: relative;
    margin-bottom: 20px;
  }

  .search-input {
    width: 100%;
    padding: 12px 40px 12px 16px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 16px;
    transition: border-color 0.2s ease;
  }

  .search-input:focus {
    outline: none;
    border-color: #4CAF50;
  }

  .search-icon {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #666;
  }

  .category-filters {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }

  .category-filter {
    padding: 8px 16px;
    border: 2px solid #e0e0e0;
    border-radius: 20px;
    background: white;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
  }

  .category-filter:hover {
    border-color: #4CAF50;
    background: #f8fff8;
  }

  .category-filter.active {
    border-color: #4CAF50;
    background: #4CAF50;
    color: white;
  }

  .category-count {
    background: rgba(0,0,0,0.1);
    padding: 2px 6px;
    border-radius: 10px;
    font-size: 12px;
  }

  .category-filter.active .category-count {
    background: rgba(255,255,255,0.2);
  }

  .tests-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 24px;
    margin-bottom: 48px;
  }

  .test-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    border: 2px solid transparent;
  }

  .test-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    border-color: #4CAF50;
  }

  .test-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .test-category {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 8px;
    border-radius: 12px;
    color: white;
    font-size: 12px;
    font-weight: 500;
    text-transform: capitalize;
  }

  .category-icon {
    font-size: 14px;
  }

  .test-difficulty {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .test-card-content {
    margin-bottom: 20px;
  }

  .test-title {
    margin: 0 0 8px 0;
    font-size: 18px;
    font-weight: 600;
    color: #1a1a1a;
    line-height: 1.3;
  }

  .test-description {
    margin: 0 0 16px 0;
    color: #666;
    line-height: 1.5;
    font-size: 14px;
  }

  .test-metadata {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
  }

  .metadata-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: #666;
  }

  .metadata-icon {
    font-size: 14px;
  }

  .test-card-actions {
    display: flex;
    gap: 12px;
  }

  .btn-primary {
    background: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    text-decoration: none;
    text-align: center;
    transition: background 0.2s ease;
    flex: 1;
  }

  .btn-primary:hover {
    background: #45a049;
  }

  .btn-secondary {
    background: transparent;
    color: #4CAF50;
    border: 2px solid #4CAF50;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-secondary:hover {
    background: #4CAF50;
    color: white;
  }

  .no-results {
    grid-column: 1 / -1;
    text-align: center;
    padding: 60px 20px;
    color: #666;
  }

  .no-results h3 {
    margin: 0 0 8px 0;
    color: #333;
  }

  .featured-section {
    background: white;
    border-radius: 12px;
    padding: 32px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }

  .featured-section h2 {
    margin: 0 0 24px 0;
    font-size: 24px;
    font-weight: 600;
    color: #1a1a1a;
  }

  .featured-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
  }

  .featured-card {
    padding: 24px;
    border: 2px solid #f0f0f0;
    border-radius: 12px;
    text-align: center;
    transition: all 0.3s ease;
  }

  .featured-card:hover {
    border-color: #4CAF50;
    background: #f8fff8;
  }

  .featured-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }

  .featured-card h3 {
    margin: 0 0 8px 0;
    font-size: 18px;
    font-weight: 600;
    color: #1a1a1a;
  }

  .featured-card p {
    margin: 0 0 16px 0;
    color: #666;
    line-height: 1.5;
    font-size: 14px;
  }

  .featured-tests {
    display: flex;
    gap: 8px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .featured-tests span {
    background: #e8f5e8;
    color: #2e7d32;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
  }

  @media (max-width: 768px) {
    .library-header {
      flex-direction: column;
      text-align: center;
    }

    .library-stats {
      gap: 20px;
    }

    .category-filters {
      justify-content: center;
    }

    .tests-grid {
      grid-template-columns: 1fr;
    }

    .test-card-actions {
      flex-direction: column;
    }
  }
`;
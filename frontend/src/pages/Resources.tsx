import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';

interface Resource {
  id: string;
  title: string;
  description: string;
  type: 'article' | 'video' | 'audio' | 'exercise' | 'tool' | 'course' | 'book' | 'app';
  category: 'stress' | 'anxiety' | 'depression' | 'sleep' | 'mindfulness' | 'exercise' | 'nutrition' | 'relationships' | 'work_life_balance' | 'resilience';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  duration?: string;
  url?: string;
  content?: string;
  tags: string[];
  rating: number;
  reviewCount: number;
  isFree: boolean;
  author?: string;
  publishedAt: Date;
  estimatedReadTime?: number;
  isPersonalized?: boolean;
  relevanceScore?: number;
}

interface Recommendation {
  id: string;
  title: string;
  description: string;
  reason: string;
  resources: Resource[];
  priority: 'low' | 'medium' | 'high';
  category: Resource['category'];
  completedAt?: Date;
  isBookmarked: boolean;
}

interface UserPreferences {
  categories: Resource['category'][];
  types: Resource['type'][];
  difficulty: Resource['difficulty'];
  timeAvailable: number; // in minutes
  languages: string[];
  accessibilityNeeds: string[];
}

export default function Resources() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [preferences, setPreferences] = useState<UserPreferences>({
    categories: ['mindfulness', 'stress'],
    types: ['article', 'video'],
    difficulty: 'beginner',
    timeAvailable: 15,
    languages: ['en'],
    accessibilityNeeds: []
  });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'all' | 'recommended' | 'bookmarked' | 'completed'>('recommended');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<Resource['category'] | 'all'>('all');
  const [selectedType, setSelectedType] = useState<Resource['type'] | 'all'>('all');
  const [bookmarkedResources, setBookmarkedResources] = useState<Set<string>>(new Set());
  const [completedResources, setCompletedResources] = useState<Set<string>>(new Set());
  const [showPreferences, setShowPreferences] = useState(false);

  useEffect(() => {
    loadResources();
    loadRecommendations();
    loadUserData();
  }, []);

  const loadResources = async () => {
    try {
      // Mock data - replace with actual API call
      const mockResources: Resource[] = [
        {
          id: '1',
          title: '5-Minute Breathing Exercise for Instant Calm',
          description: 'A simple breathing technique that can help reduce stress and anxiety in just 5 minutes.',
          type: 'exercise',
          category: 'stress',
          difficulty: 'beginner',
          duration: '5 minutes',
          content: `
            # 5-Minute Breathing Exercise
            
            ## Steps:
            1. Find a comfortable seated position
            2. Close your eyes or soften your gaze
            3. Breathe in slowly for 4 counts
            4. Hold your breath for 4 counts
            5. Exhale slowly for 6 counts
            6. Repeat for 5 minutes
            
            ## Benefits:
            - Reduces stress hormones
            - Lowers heart rate
            - Improves focus
            - Promotes relaxation
          `,
          tags: ['breathing', 'quick', 'stress-relief'],
          rating: 4.8,
          reviewCount: 1247,
          isFree: true,
          author: 'Dr. Sarah Martinez',
          publishedAt: new Date('2024-01-15'),
          estimatedReadTime: 2,
          isPersonalized: true,
          relevanceScore: 0.95
        },
        {
          id: '2',
          title: 'Understanding Workplace Stress: A Complete Guide',
          description: 'Comprehensive article covering the causes, effects, and management strategies for workplace stress.',
          type: 'article',
          category: 'work_life_balance',
          difficulty: 'intermediate',
          duration: '15 minutes',
          url: 'https://example.com/workplace-stress-guide',
          tags: ['workplace', 'stress-management', 'productivity'],
          rating: 4.6,
          reviewCount: 892,
          isFree: true,
          author: 'Michael Chen',
          publishedAt: new Date('2024-01-10'),
          estimatedReadTime: 15,
          isPersonalized: false,
          relevanceScore: 0.78
        },
        {
          id: '3',
          title: 'Mindfulness Meditation for Beginners',
          description: 'Learn the basics of mindfulness meditation with this guided 10-minute session.',
          type: 'audio',
          category: 'mindfulness',
          difficulty: 'beginner',
          duration: '10 minutes',
          url: 'https://example.com/mindfulness-audio',
          tags: ['meditation', 'guided', 'relaxation'],
          rating: 4.9,
          reviewCount: 2156,
          isFree: true,
          author: 'Anna Thompson',
          publishedAt: new Date('2024-01-05'),
          isPersonalized: true,
          relevanceScore: 0.92
        },
        {
          id: '4',
          title: 'The Science of Sleep: Optimizing Your Rest',
          description: 'Video course exploring sleep hygiene, circadian rhythms, and strategies for better sleep quality.',
          type: 'video',
          category: 'sleep',
          difficulty: 'intermediate',
          duration: '45 minutes',
          url: 'https://example.com/sleep-science',
          tags: ['sleep-hygiene', 'circadian-rhythm', 'health'],
          rating: 4.7,
          reviewCount: 678,
          isFree: false,
          author: 'Dr. Robert Kim',
          publishedAt: new Date('2024-01-01'),
          estimatedReadTime: 45,
          isPersonalized: false,
          relevanceScore: 0.65
        },
        {
          id: '5',
          title: 'Building Emotional Resilience at Work',
          description: 'Interactive tool to assess and develop your emotional resilience in challenging situations.',
          type: 'tool',
          category: 'resilience',
          difficulty: 'intermediate',
          duration: '20 minutes',
          url: 'https://example.com/resilience-tool',
          tags: ['emotional-intelligence', 'resilience', 'self-assessment'],
          rating: 4.5,
          reviewCount: 445,
          isFree: true,
          author: 'Jennifer Lopez',
          publishedAt: new Date('2023-12-28'),
          isPersonalized: true,
          relevanceScore: 0.88
        }
      ];

      setResources(mockResources);
    } catch (error) {
      console.error('Failed to load resources:', error);
    }
  };

  const loadRecommendations = async () => {
    try {
      // Mock recommendations - replace with actual API call
      const mockRecommendations: Recommendation[] = [
        {
          id: 'rec1',
          title: 'Stress Management Starter Pack',
          description: 'Based on your recent assessments, we recommend focusing on stress reduction techniques.',
          reason: 'Your stress levels have been elevated in recent assessments. These resources can help.',
          resources: [], // Will be populated with resource IDs
          priority: 'high',
          category: 'stress',
          isBookmarked: false
        },
        {
          id: 'rec2',
          title: 'Mindfulness for Better Focus',
          description: 'Improve your concentration and reduce anxiety with these mindfulness practices.',
          reason: 'Users with similar profiles have found these mindfulness resources particularly helpful.',
          resources: [],
          priority: 'medium',
          category: 'mindfulness',
          isBookmarked: true
        }
      ];

      setRecommendations(mockRecommendations);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUserData = async () => {
    try {
      // Mock user data - replace with actual API call
      setBookmarkedResources(new Set(['3', '5']));
      setCompletedResources(new Set(['1']));
    } catch (error) {
      console.error('Failed to load user data:', error);
    }
  };

  const toggleBookmark = async (resourceId: string) => {
    try {
      const newBookmarks = new Set(bookmarkedResources);
      if (newBookmarks.has(resourceId)) {
        newBookmarks.delete(resourceId);
      } else {
        newBookmarks.add(resourceId);
      }
      setBookmarkedResources(newBookmarks);
      // API call to save bookmark
    } catch (error) {
      console.error('Failed to toggle bookmark:', error);
    }
  };

  const markAsCompleted = async (resourceId: string) => {
    try {
      const newCompleted = new Set(completedResources);
      newCompleted.add(resourceId);
      setCompletedResources(newCompleted);
      // API call to mark as completed
    } catch (error) {
      console.error('Failed to mark as completed:', error);
    }
  };

  const updatePreferences = async (newPreferences: Partial<UserPreferences>) => {
    try {
      setPreferences(prev => ({ ...prev, ...newPreferences }));
      // API call to save preferences
      // Reload recommendations based on new preferences
      await loadRecommendations();
    } catch (error) {
      console.error('Failed to update preferences:', error);
    }
  };

  const getFilteredResources = () => {
    let filtered = resources;

    // Filter by tab
    switch (activeTab) {
      case 'recommended':
        filtered = filtered.filter(r => r.isPersonalized || r.relevanceScore > 0.8);
        break;
      case 'bookmarked':
        filtered = filtered.filter(r => bookmarkedResources.has(r.id));
        break;
      case 'completed':
        filtered = filtered.filter(r => completedResources.has(r.id));
        break;
    }

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(r => 
        r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(r => r.category === selectedCategory);
    }

    // Filter by type
    if (selectedType !== 'all') {
      filtered = filtered.filter(r => r.type === selectedType);
    }

         // Sort by relevance for recommended tab
     if (activeTab === 'recommended') {
       filtered.sort((a, b) => (b.relevanceScore ?? 0) - (a.relevanceScore ?? 0));
     }

    return filtered;
  };

  const getResourceIcon = (type: Resource['type']) => {
    switch (type) {
      case 'article': return '📖';
      case 'video': return '🎥';
      case 'audio': return '🎧';
      case 'exercise': return '🧘';
      case 'tool': return '🛠️';
      case 'course': return '🎓';
      case 'book': return '📚';
      case 'app': return '📱';
    }
  };

  const getCategoryColor = (category: Resource['category']) => {
    const colors = {
      stress: '#f44336',
      anxiety: '#ff9800',
      depression: '#9c27b0',
      sleep: '#3f51b5',
      mindfulness: '#4caf50',
      exercise: '#ff5722',
      nutrition: '#8bc34a',
      relationships: '#e91e63',
      work_life_balance: '#2196f3',
      resilience: '#607d8b'
    };
    return colors[category] || '#666';
  };

  const getDifficultyColor = (difficulty: Resource['difficulty']) => {
    switch (difficulty) {
      case 'beginner': return '#4caf50';
      case 'intermediate': return '#ff9800';
      case 'advanced': return '#f44336';
    }
  };

  const filteredResources = getFilteredResources();

  if (loading) {
    return (
      <div className="resources-container">
        <style>{resourcesStyles}</style>
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading resources...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="resources-container">
      <style>{resourcesStyles}</style>

      {/* Header */}
      <div className="resources-header">
        <div className="header-content">
          <h1>🌟 Wellbeing Resources</h1>
          <p>Personalized recommendations and curated content to support your mental health journey</p>
        </div>
        
        <button 
          className="preferences-btn"
          onClick={() => setShowPreferences(true)}
        >
          ⚙️ Preferences
        </button>
      </div>

      {/* Recommendations Section */}
      {recommendations.length > 0 && (
        <div className="recommendations-section">
          <h2>🎯 Personalized Recommendations</h2>
          <div className="recommendations-grid">
            {recommendations.map(recommendation => (
              <div key={recommendation.id} className="recommendation-card">
                <div className="rec-header">
                  <h3>{recommendation.title}</h3>
                  <div 
                    className="priority-badge"
                    style={{ backgroundColor: 
                      recommendation.priority === 'high' ? '#f44336' :
                      recommendation.priority === 'medium' ? '#ff9800' : '#4caf50'
                    }}
                  >
                    {recommendation.priority} priority
                  </div>
                </div>
                
                <p className="rec-description">{recommendation.description}</p>
                <p className="rec-reason">💡 {recommendation.reason}</p>
                
                <div className="rec-actions">
                  <button className="btn-primary">Explore Resources</button>
                  <button 
                    className={`btn-bookmark ${recommendation.isBookmarked ? 'bookmarked' : ''}`}
                    onClick={() => {
                      // Toggle recommendation bookmark
                    }}
                  >
                    {recommendation.isBookmarked ? '🔖' : '📎'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filter Controls */}
      <div className="filter-controls">
        <div className="tabs">
          {(['all', 'recommended', 'bookmarked', 'completed'] as const).map(tab => (
            <button
              key={tab}
              className={`tab ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab === 'all' && '📚 All Resources'}
              {tab === 'recommended' && '⭐ Recommended'}
              {tab === 'bookmarked' && '🔖 Bookmarked'}
              {tab === 'completed' && '✅ Completed'}
            </button>
          ))}
        </div>

        <div className="filters">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search resources..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <span className="search-icon">🔍</span>
          </div>

          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value as any)}
            className="filter-select"
          >
            <option value="all">All Categories</option>
            <option value="stress">Stress Management</option>
            <option value="anxiety">Anxiety</option>
            <option value="depression">Depression</option>
            <option value="sleep">Sleep</option>
            <option value="mindfulness">Mindfulness</option>
            <option value="exercise">Exercise</option>
            <option value="nutrition">Nutrition</option>
            <option value="relationships">Relationships</option>
            <option value="work_life_balance">Work-Life Balance</option>
            <option value="resilience">Resilience</option>
          </select>

          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value as any)}
            className="filter-select"
          >
            <option value="all">All Types</option>
            <option value="article">Articles</option>
            <option value="video">Videos</option>
            <option value="audio">Audio</option>
            <option value="exercise">Exercises</option>
            <option value="tool">Tools</option>
            <option value="course">Courses</option>
            <option value="book">Books</option>
            <option value="app">Apps</option>
          </select>
        </div>
      </div>

      {/* Resources Grid */}
      <div className="resources-grid">
        {filteredResources.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">🔍</span>
            <h3>No resources found</h3>
            <p>Try adjusting your filters or search query</p>
          </div>
        ) : (
          filteredResources.map(resource => (
            <div key={resource.id} className="resource-card">
              <div className="resource-header">
                <div className="resource-meta">
                  <span className="resource-icon">{getResourceIcon(resource.type)}</span>
                  <span 
                    className="category-badge"
                    style={{ backgroundColor: getCategoryColor(resource.category) }}
                  >
                    {resource.category.replace('_', ' ')}
                  </span>
                  {resource.isPersonalized && (
                    <span className="personalized-badge" title="Personalized for you">✨</span>
                  )}
                </div>
                
                <div className="resource-actions">
                  <button
                    className={`bookmark-btn ${bookmarkedResources.has(resource.id) ? 'bookmarked' : ''}`}
                    onClick={() => toggleBookmark(resource.id)}
                    title={bookmarkedResources.has(resource.id) ? 'Remove bookmark' : 'Bookmark'}
                  >
                    {bookmarkedResources.has(resource.id) ? '🔖' : '📎'}
                  </button>
                  
                  {completedResources.has(resource.id) && (
                    <span className="completed-badge" title="Completed">✅</span>
                  )}
                </div>
              </div>

              <h3 className="resource-title">{resource.title}</h3>
              <p className="resource-description">{resource.description}</p>

              <div className="resource-details">
                <div className="detail-row">
                  <span className="detail-label">Duration:</span>
                  <span className="detail-value">{resource.duration || 'Self-paced'}</span>
                </div>
                
                <div className="detail-row">
                  <span className="detail-label">Difficulty:</span>
                  <span 
                    className="difficulty-badge"
                    style={{ backgroundColor: getDifficultyColor(resource.difficulty) }}
                  >
                    {resource.difficulty}
                  </span>
                </div>
                
                <div className="detail-row">
                  <span className="detail-label">Rating:</span>
                  <div className="rating">
                    <span className="stars">{'⭐'.repeat(Math.floor(resource.rating))}</span>
                    <span className="rating-text">{resource.rating} ({resource.reviewCount})</span>
                  </div>
                </div>
              </div>

              <div className="resource-tags">
                {resource.tags.map(tag => (
                  <span key={tag} className="tag">#{tag}</span>
                ))}
              </div>

              <div className="resource-footer">
                <div className="author-info">
                  <span className="author">By {resource.author}</span>
                  <span className="publish-date">{format(resource.publishedAt, 'MMM dd, yyyy')}</span>
                </div>
                
                <div className="resource-cta">
                  {resource.url ? (
                    <a 
                      href={resource.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="btn-primary"
                    >
                      {resource.type === 'article' && 'Read Article'}
                      {resource.type === 'video' && 'Watch Video'}
                      {resource.type === 'audio' && 'Listen'}
                      {resource.type === 'exercise' && 'Start Exercise'}
                      {resource.type === 'tool' && 'Use Tool'}
                      {resource.type === 'course' && 'Take Course'}
                      {resource.type === 'book' && 'Read Book'}
                      {resource.type === 'app' && 'Download App'}
                    </a>
                  ) : (
                    <button 
                      className="btn-primary"
                      onClick={() => {
                        // Show resource content in modal
                      }}
                    >
                      View Content
                    </button>
                  )}
                  
                  {!completedResources.has(resource.id) && (
                    <button
                      className="btn-secondary"
                      onClick={() => markAsCompleted(resource.id)}
                    >
                      Mark Complete
                    </button>
                  )}
                </div>
              </div>

              {!resource.isFree && (
                <div className="premium-overlay">
                  <span className="premium-badge">💎 Premium</span>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Preferences Modal */}
      {showPreferences && (
        <div className="preferences-overlay">
          <div className="preferences-modal">
            <div className="modal-header">
              <h3>🎯 Personalization Preferences</h3>
              <button 
                className="close-btn"
                onClick={() => setShowPreferences(false)}
              >
                ×
              </button>
            </div>

            <div className="modal-content">
              <div className="pref-section">
                <h4>Preferred Categories</h4>
                <div className="checkbox-grid">
                  {(['stress', 'anxiety', 'depression', 'sleep', 'mindfulness', 'exercise', 'nutrition', 'relationships', 'work_life_balance', 'resilience'] as const).map(category => (
                    <label key={category} className="checkbox-item">
                      <input
                        type="checkbox"
                        checked={preferences.categories.includes(category)}
                        onChange={(e) => {
                          const newCategories = e.target.checked
                            ? [...preferences.categories, category]
                            : preferences.categories.filter(c => c !== category);
                          updatePreferences({ categories: newCategories });
                        }}
                      />
                      <span>{category.replace('_', ' ')}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="pref-section">
                <h4>Content Types</h4>
                <div className="checkbox-grid">
                  {(['article', 'video', 'audio', 'exercise', 'tool', 'course', 'book', 'app'] as const).map(type => (
                    <label key={type} className="checkbox-item">
                      <input
                        type="checkbox"
                        checked={preferences.types.includes(type)}
                        onChange={(e) => {
                          const newTypes = e.target.checked
                            ? [...preferences.types, type]
                            : preferences.types.filter(t => t !== type);
                          updatePreferences({ types: newTypes });
                        }}
                      />
                      <span>{type}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="pref-section">
                <h4>Difficulty Level</h4>
                <div className="radio-group">
                  {(['beginner', 'intermediate', 'advanced'] as const).map(difficulty => (
                    <label key={difficulty} className="radio-item">
                      <input
                        type="radio"
                        name="difficulty"
                        value={difficulty}
                        checked={preferences.difficulty === difficulty}
                        onChange={(e) => updatePreferences({ difficulty: e.target.value as any })}
                      />
                      <span>{difficulty}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="pref-section">
                <h4>Available Time</h4>
                <div className="time-selector">
                  <input
                    type="range"
                    min="5"
                    max="60"
                    value={preferences.timeAvailable}
                    onChange={(e) => updatePreferences({ timeAvailable: parseInt(e.target.value) })}
                  />
                  <span>{preferences.timeAvailable} minutes</span>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button 
                className="btn-secondary"
                onClick={() => setShowPreferences(false)}
              >
                Cancel
              </button>
              <button 
                className="btn-primary"
                onClick={() => setShowPreferences(false)}
              >
                Save Preferences
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const resourcesStyles = `
  .resources-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f8f9fa;
    min-height: 100vh;
  }

  .resources-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 16px;
    padding: 32px;
    margin-bottom: 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .header-content h1 {
    margin: 0 0 8px 0;
    font-size: 32px;
    font-weight: 700;
  }

  .header-content p {
    margin: 0;
    opacity: 0.9;
    font-size: 16px;
    line-height: 1.5;
  }

  .preferences-btn {
    background: rgba(255,255,255,0.9);
    color: #333;
    border: none;
    padding: 12px 20px;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .preferences-btn:hover {
    background: white;
    transform: translateY(-1px);
  }

  .recommendations-section {
    margin-bottom: 40px;
  }

  .recommendations-section h2 {
    margin: 0 0 24px 0;
    font-size: 24px;
    color: #333;
  }

  .recommendations-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 24px;
    margin-bottom: 32px;
  }

  .recommendation-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border-left: 4px solid #4caf50;
  }

  .rec-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
  }

  .rec-header h3 {
    margin: 0;
    font-size: 18px;
    color: #333;
  }

  .priority-badge {
    padding: 4px 8px;
    border-radius: 12px;
    color: white;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
  }

  .rec-description {
    margin: 0 0 12px 0;
    color: #555;
    line-height: 1.5;
  }

  .rec-reason {
    margin: 0 0 20px 0;
    color: #666;
    font-style: italic;
    font-size: 14px;
  }

  .rec-actions {
    display: flex;
    gap: 12px;
  }

  .filter-controls {
    background: white;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 32px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }

  .tabs {
    display: flex;
    gap: 4px;
    margin-bottom: 20px;
    border-bottom: 1px solid #e0e0e0;
  }

  .tab {
    padding: 12px 20px;
    border: none;
    background: none;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    color: #666;
    border-bottom: 2px solid transparent;
    transition: all 0.2s ease;
  }

  .tab.active {
    color: #4caf50;
    border-bottom-color: #4caf50;
  }

  .tab:hover {
    color: #4caf50;
  }

  .filters {
    display: flex;
    gap: 16px;
    align-items: center;
    flex-wrap: wrap;
  }

  .search-box {
    position: relative;
    flex: 1;
    min-width: 250px;
  }

  .search-box input {
    width: 100%;
    padding: 12px 40px 12px 16px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 14px;
  }

  .search-icon {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #666;
  }

  .filter-select {
    padding: 12px 16px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 14px;
    background: white;
    cursor: pointer;
  }

  .resources-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    gap: 24px;
  }

  .resource-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
  }

  .resource-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  }

  .resource-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .resource-meta {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .resource-icon {
    font-size: 20px;
  }

  .category-badge {
    padding: 4px 8px;
    border-radius: 12px;
    color: white;
    font-size: 12px;
    font-weight: 600;
    text-transform: capitalize;
  }

  .personalized-badge {
    font-size: 16px;
    title: "Personalized for you";
  }

  .resource-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .bookmark-btn {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    transition: background-color 0.2s ease;
  }

  .bookmark-btn:hover {
    background: #f0f0f0;
  }

  .bookmark-btn.bookmarked {
    color: #ff9800;
  }

  .completed-badge {
    font-size: 16px;
  }

  .resource-title {
    margin: 0 0 12px 0;
    font-size: 18px;
    font-weight: 600;
    color: #333;
    line-height: 1.3;
  }

  .resource-description {
    margin: 0 0 16px 0;
    color: #555;
    line-height: 1.5;
    font-size: 14px;
  }

  .resource-details {
    margin-bottom: 16px;
  }

  .detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .detail-label {
    font-size: 14px;
    color: #666;
    font-weight: 500;
  }

  .detail-value {
    font-size: 14px;
    color: #333;
  }

  .difficulty-badge {
    padding: 2px 8px;
    border-radius: 8px;
    color: white;
    font-size: 12px;
    font-weight: 600;
    text-transform: capitalize;
  }

  .rating {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .stars {
    color: #ffc107;
  }

  .rating-text {
    font-size: 14px;
    color: #666;
  }

  .resource-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 20px;
  }

  .tag {
    padding: 4px 8px;
    background: #f0f0f0;
    border-radius: 8px;
    font-size: 12px;
    color: #666;
  }

  .resource-footer {
    border-top: 1px solid #f0f0f0;
    padding-top: 16px;
  }

  .author-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    font-size: 12px;
    color: #666;
  }

  .author {
    font-weight: 500;
  }

  .resource-cta {
    display: flex;
    gap: 12px;
  }

  .btn-primary {
    background: #4caf50;
    color: white;
    border: none;
    padding: 10px 16px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    text-decoration: none;
    transition: background 0.2s ease;
    flex: 1;
    text-align: center;
  }

  .btn-primary:hover {
    background: #45a049;
  }

  .btn-secondary {
    background: #f0f0f0;
    color: #666;
    border: none;
    padding: 10px 16px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s ease;
  }

  .btn-secondary:hover {
    background: #e0e0e0;
  }

  .btn-bookmark {
    background: none;
    border: 1px solid #ddd;
    padding: 8px 12px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-bookmark.bookmarked {
    background: #fff3e0;
    border-color: #ff9800;
    color: #ff9800;
  }

  .premium-overlay {
    position: absolute;
    top: 12px;
    right: 12px;
    background: linear-gradient(45deg, #ffd700, #ffed4e);
    border-radius: 12px;
    padding: 4px 8px;
  }

  .premium-badge {
    font-size: 12px;
    font-weight: 600;
    color: #333;
  }

  .empty-state {
    grid-column: 1 / -1;
    text-align: center;
    padding: 60px 20px;
    color: #666;
  }

  .empty-icon {
    font-size: 64px;
    display: block;
    margin-bottom: 16px;
  }

  .empty-state h3 {
    margin: 0 0 8px 0;
    font-size: 20px;
  }

  .empty-state p {
    margin: 0;
    font-size: 16px;
  }

  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 20px;
    text-align: center;
  }

  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f0f0f0;
    border-top: 4px solid #4caf50;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .preferences-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .preferences-modal {
    background: white;
    border-radius: 12px;
    width: 600px;
    max-width: 90vw;
    max-height: 80vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .modal-header {
    padding: 24px;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .modal-header h3 {
    margin: 0;
    font-size: 20px;
    color: #333;
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 24px;
    color: #666;
    cursor: pointer;
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
  }

  .close-btn:hover {
    background: #f0f0f0;
  }

  .modal-content {
    padding: 24px;
    overflow-y: auto;
    flex: 1;
  }

  .pref-section {
    margin-bottom: 32px;
  }

  .pref-section h4 {
    margin: 0 0 16px 0;
    font-size: 16px;
    color: #333;
    font-weight: 600;
  }

  .checkbox-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
  }

  .checkbox-item, .radio-item {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }

  .checkbox-item input, .radio-item input {
    margin: 0;
  }

  .checkbox-item span, .radio-item span {
    font-size: 14px;
    color: #333;
    text-transform: capitalize;
  }

  .radio-group {
    display: flex;
    gap: 24px;
  }

  .time-selector {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .time-selector input[type="range"] {
    flex: 1;
  }

  .time-selector span {
    font-weight: 600;
    color: #333;
    min-width: 80px;
  }

  .modal-footer {
    padding: 24px;
    border-top: 1px solid #e0e0e0;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }

  @media (max-width: 768px) {
    .resources-header {
      flex-direction: column;
      text-align: center;
      gap: 16px;
    }

    .recommendations-grid {
      grid-template-columns: 1fr;
    }

    .resources-grid {
      grid-template-columns: 1fr;
    }

    .filters {
      flex-direction: column;
      align-items: stretch;
    }

    .search-box {
      min-width: auto;
    }

    .tabs {
      flex-wrap: wrap;
    }

    .preferences-modal {
      width: calc(100vw - 32px);
      height: calc(100vh - 32px);
    }

    .checkbox-grid {
      grid-template-columns: 1fr;
    }

    .radio-group {
      flex-direction: column;
      gap: 12px;
    }
  }
`;
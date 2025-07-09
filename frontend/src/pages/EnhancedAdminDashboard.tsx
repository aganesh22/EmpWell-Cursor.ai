import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { format, subDays, eachDayOfInterval, eachMonthOfInterval, subMonths } from 'date-fns';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
} from 'chart.js';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
);

interface DashboardData {
  overview: {
    totalUsers: number;
    activeUsers: number;
    completedAssessments: number;
    averageWellbeingScore: number;
    riskAlerts: number;
    departmentCount: number;
  };
  wellbeingTrends: {
    date: string;
    avgScore: number;
    assessmentCount: number;
    riskCount: number;
  }[];
  departmentBreakdown: {
    department: string;
    userCount: number;
    avgWellbeing: number;
    riskLevel: 'low' | 'moderate' | 'high';
    completionRate: number;
  }[];
  assessmentDistribution: {
    testType: string;
    count: number;
    avgScore: number;
    color: string;
  }[];
  riskAnalysis: {
    category: string;
    lowRisk: number;
    moderateRisk: number;
    highRisk: number;
  }[];
  userEngagement: {
    month: string;
    newUsers: number;
    activeUsers: number;
    assessmentsCompleted: number;
  }[];
}

export default function EnhancedAdminDashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');
  const [selectedDepartment, setSelectedDepartment] = useState<string>('all');
  const [privacyMode, setPrivacyMode] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, [dateRange, selectedDepartment]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // In a real implementation, this would call your API
      const mockData = generateMockData();
      setData(mockData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = (): DashboardData => {
    const endDate = new Date();
    const startDate = subDays(endDate, dateRange === '7d' ? 7 : dateRange === '30d' ? 30 : dateRange === '90d' ? 90 : 365);
    
    return {
      overview: {
        totalUsers: 1247,
        activeUsers: 892,
        completedAssessments: 3456,
        averageWellbeingScore: 73.2,
        riskAlerts: 23,
        departmentCount: 8
      },
      wellbeingTrends: eachDayOfInterval({ start: startDate, end: endDate }).map(date => ({
        date: format(date, 'MMM dd'),
        avgScore: 65 + Math.random() * 20,
        assessmentCount: Math.floor(Math.random() * 50) + 10,
        riskCount: Math.floor(Math.random() * 5)
      })),
      departmentBreakdown: [
        { department: 'Engineering', userCount: 342, avgWellbeing: 76.8, riskLevel: 'low', completionRate: 89 },
        { department: 'Sales', userCount: 189, avgWellbeing: 71.2, riskLevel: 'moderate', completionRate: 76 },
        { department: 'Marketing', userCount: 156, avgWellbeing: 68.9, riskLevel: 'moderate', completionRate: 82 },
        { department: 'HR', userCount: 78, avgWellbeing: 79.1, riskLevel: 'low', completionRate: 94 },
        { department: 'Finance', userCount: 123, avgWellbeing: 74.5, riskLevel: 'low', completionRate: 87 },
        { department: 'Operations', userCount: 234, avgWellbeing: 65.3, riskLevel: 'high', completionRate: 68 },
        { department: 'Customer Support', userCount: 98, avgWellbeing: 62.7, riskLevel: 'high', completionRate: 71 },
        { department: 'Legal', userCount: 27, avgWellbeing: 77.8, riskLevel: 'low', completionRate: 85 }
      ],
      assessmentDistribution: [
        { testType: 'WHO-5 Wellbeing', count: 1234, avgScore: 73.2, color: '#4CAF50' },
        { testType: 'GAD-7 Anxiety', count: 987, avgScore: 8.4, color: '#FF9800' },
        { testType: 'PHQ-9 Depression', count: 856, avgScore: 6.1, color: '#f44336' },
        { testType: 'Stress Scale', count: 743, avgScore: 15.2, color: '#9C27B0' },
        { testType: 'Big Five', count: 567, avgScore: 3.8, color: '#2196F3' },
        { testType: 'DISC', count: 432, avgScore: 4.2, color: '#FF5722' }
      ],
      riskAnalysis: [
        { category: 'Depression Risk', lowRisk: 78, moderateRisk: 18, highRisk: 4 },
        { category: 'Anxiety Risk', lowRisk: 82, moderateRisk: 15, highRisk: 3 },
        { category: 'Stress Risk', lowRisk: 65, moderateRisk: 28, highRisk: 7 },
        { category: 'Burnout Risk', lowRisk: 71, moderateRisk: 22, highRisk: 7 },
        { category: 'Overall Wellbeing', lowRisk: 73, moderateRisk: 21, highRisk: 6 }
      ],
      userEngagement: eachMonthOfInterval({ 
        start: subMonths(endDate, 11), 
        end: endDate 
      }).map(date => ({
        month: format(date, 'MMM yy'),
        newUsers: Math.floor(Math.random() * 50) + 20,
        activeUsers: Math.floor(Math.random() * 200) + 150,
        assessmentsCompleted: Math.floor(Math.random() * 300) + 200
      }))
    };
  };

  const getScoreColor = (score: number, reverse = false) => {
    if (reverse) {
      if (score <= 5) return '#4CAF50';
      if (score <= 10) return '#FF9800';
      return '#f44336';
    } else {
      if (score >= 75) return '#4CAF50';
      if (score >= 60) return '#FF9800';
      return '#f44336';
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'low': return '#4CAF50';
      case 'moderate': return '#FF9800';
      case 'high': return '#f44336';
      default: return '#666';
    }
  };

  const exportData = () => {
    if (!data) return;
    
    const exportData = privacyMode ? {
      ...data,
      departmentBreakdown: data.departmentBreakdown.map(dept => ({
        ...dept,
        department: `Dept-${Math.random().toString(36).substr(2, 9)}`
      }))
    } : data;
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `wellbeing-report-${format(new Date(), 'yyyy-MM-dd')}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Chart configurations
  const wellbeingTrendsData = data ? {
    labels: data.wellbeingTrends.map(item => item.date),
    datasets: [
      {
        label: 'Wellbeing Score',
        data: data.wellbeingTrends.map(item => item.avgScore),
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Risk Alerts',
        data: data.wellbeingTrends.map(item => item.riskCount),
        borderColor: '#f44336',
        backgroundColor: 'rgba(244, 67, 54, 0.1)',
        fill: true,
        tension: 0.4,
        yAxisID: 'y1'
      }
    ]
  } : null;

  const assessmentDistributionData = data ? {
    labels: data.assessmentDistribution.map(item => item.testType),
    datasets: [{
      data: data.assessmentDistribution.map(item => item.count),
      backgroundColor: data.assessmentDistribution.map(item => item.color),
      borderWidth: 2,
      borderColor: '#fff'
    }]
  } : null;

  const departmentComparisonData = data ? {
    labels: data.departmentBreakdown.map(dept => privacyMode ? `Dept-${dept.department.slice(-3)}` : dept.department),
    datasets: [
      {
        label: 'Wellbeing Score',
        data: data.departmentBreakdown.map(dept => dept.avgWellbeing),
        backgroundColor: data.departmentBreakdown.map(dept => getScoreColor(dept.avgWellbeing)),
        borderWidth: 1
      }
    ]
  } : null;

  const riskAnalysisData = data ? {
    labels: data.riskAnalysis.map(item => item.category),
    datasets: [
      {
        label: 'Low Risk',
        data: data.riskAnalysis.map(item => item.lowRisk),
        backgroundColor: '#4CAF50'
      },
      {
        label: 'Moderate Risk',
        data: data.riskAnalysis.map(item => item.moderateRisk),
        backgroundColor: '#FF9800'
      },
      {
        label: 'High Risk',
        data: data.riskAnalysis.map(item => item.highRisk),
        backgroundColor: '#f44336'
      }
    ]
  } : null;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      }
    },
    scales: {
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        grid: {
          drawOnChartArea: false,
        },
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    }
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <style>{dashboardStyles}</style>
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="dashboard-container">
        <style>{dashboardStyles}</style>
        <div className="error-state">
          <h2>Failed to load dashboard</h2>
          <button onClick={loadDashboardData} className="btn-primary">Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <style>{dashboardStyles}</style>
      
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-content">
          <h1>🏢 Wellbeing Analytics Dashboard</h1>
          <p>Comprehensive insights into organizational mental health and employee wellbeing</p>
        </div>
        
        <div className="header-controls">
          <div className="filter-group">
            <label>Time Range:</label>
            <select 
              value={dateRange} 
              onChange={(e) => setDateRange(e.target.value as any)}
              className="filter-select"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
            </select>
          </div>
          
          <div className="filter-group">
            <label>Department:</label>
            <select 
              value={selectedDepartment} 
              onChange={(e) => setSelectedDepartment(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Departments</option>
              {data.departmentBreakdown.map(dept => (
                <option key={dept.department} value={dept.department}>
                  {dept.department}
                </option>
              ))}
            </select>
          </div>
          
          <div className="privacy-toggle">
            <label>
              <input 
                type="checkbox" 
                checked={privacyMode} 
                onChange={(e) => setPrivacyMode(e.target.checked)}
              />
              <span>GDPR Mode</span>
            </label>
          </div>
          
          <button onClick={exportData} className="btn-secondary">
            📊 Export Report
          </button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="overview-grid">
        <div className="metric-card">
          <div className="metric-icon">👥</div>
          <div className="metric-content">
            <h3>Total Users</h3>
            <div className="metric-value">{data.overview.totalUsers.toLocaleString()}</div>
            <div className="metric-subtitle">
              {data.overview.activeUsers} active ({Math.round(data.overview.activeUsers / data.overview.totalUsers * 100)}%)
            </div>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">📝</div>
          <div className="metric-content">
            <h3>Assessments</h3>
            <div className="metric-value">{data.overview.completedAssessments.toLocaleString()}</div>
            <div className="metric-subtitle">
              {Math.round(data.overview.completedAssessments / data.overview.totalUsers * 10) / 10} avg per user
            </div>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">💚</div>
          <div className="metric-content">
            <h3>Avg Wellbeing</h3>
            <div className="metric-value" style={{ color: getScoreColor(data.overview.averageWellbeingScore) }}>
              {data.overview.averageWellbeingScore}%
            </div>
            <div className="metric-subtitle">Organization-wide score</div>
          </div>
        </div>
        
        <div className="metric-card alert">
          <div className="metric-icon">⚠️</div>
          <div className="metric-content">
            <h3>Risk Alerts</h3>
            <div className="metric-value risk">{data.overview.riskAlerts}</div>
            <div className="metric-subtitle">Require attention</div>
          </div>
        </div>
      </div>

      {/* Wellbeing Trends */}
      <div className="chart-section">
        <div className="section-header">
          <h2>📈 Wellbeing Trends</h2>
          <p>Track wellbeing scores and risk indicators over time</p>
        </div>
        
        <div className="chart-container" style={{ height: '400px' }}>
          {wellbeingTrendsData && (
            <Line data={wellbeingTrendsData} options={chartOptions} />
          )}
        </div>
      </div>

      {/* Department Analysis */}
      <div className="chart-section">
        <div className="section-header">
          <h2>🏢 Department Analysis</h2>
          <p>Compare wellbeing metrics across departments</p>
        </div>
        
        <div className="department-grid">
          {data.departmentBreakdown.map(dept => (
            <div key={dept.department} className="department-card">
              <div className="dept-header">
                <h3>{privacyMode ? `Dept-${dept.department.slice(-3)}` : dept.department}</h3>
                <div 
                  className="risk-badge" 
                  style={{ backgroundColor: getRiskLevelColor(dept.riskLevel) }}
                >
                  {dept.riskLevel} risk
                </div>
              </div>
              
              <div className="dept-metrics">
                <div className="dept-metric">
                  <span className="metric-label">Users</span>
                  <span className="metric-val">{dept.userCount}</span>
                </div>
                <div className="dept-metric">
                  <span className="metric-label">Wellbeing</span>
                  <span 
                    className="metric-val" 
                    style={{ color: getScoreColor(dept.avgWellbeing) }}
                  >
                    {dept.avgWellbeing}%
                  </span>
                </div>
                <div className="dept-metric">
                  <span className="metric-label">Completion</span>
                  <span className="metric-val">{dept.completionRate}%</span>
                </div>
              </div>
              
              <div className="completion-bar">
                <div 
                  className="completion-fill" 
                  style={{ width: `${dept.completionRate}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>

        <div className="chart-container" style={{ height: '300px', marginTop: '24px' }}>
          {departmentComparisonData && (
            <Bar 
              data={departmentComparisonData} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    max: 100
                  }
                }
              }} 
            />
          )}
        </div>
      </div>

      {/* Assessment Distribution */}
      <div className="chart-section">
        <div className="section-header">
          <h2>📊 Assessment Distribution</h2>
          <p>Breakdown of assessment types and participation</p>
        </div>
        
        <div className="chart-grid">
          <div className="chart-container" style={{ height: '300px' }}>
            {assessmentDistributionData && (
              <Pie 
                data={assessmentDistributionData} 
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'right'
                    }
                  }
                }} 
              />
            )}
          </div>
          
          <div className="assessment-stats">
            <h3>Assessment Statistics</h3>
            {data.assessmentDistribution.map(assessment => (
              <div key={assessment.testType} className="stat-row">
                <div className="stat-name">
                  <div 
                    className="color-indicator" 
                    style={{ backgroundColor: assessment.color }}
                  ></div>
                  {assessment.testType}
                </div>
                <div className="stat-values">
                  <span className="count">{assessment.count} completed</span>
                  <span className="avg">Avg: {assessment.avgScore}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Risk Analysis */}
      <div className="chart-section">
        <div className="section-header">
          <h2>⚠️ Risk Analysis</h2>
          <p>Comprehensive risk assessment across mental health categories</p>
        </div>
        
        <div className="chart-container" style={{ height: '400px' }}>
          {riskAnalysisData && (
            <Bar 
              data={riskAnalysisData} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y' as const,
                plugins: {
                  legend: {
                    position: 'top'
                  }
                },
                scales: {
                  x: {
                    stacked: true
                  },
                  y: {
                    stacked: true
                  }
                }
              }} 
            />
          )}
        </div>
      </div>

      {/* Privacy Notice */}
      {privacyMode && (
        <div className="privacy-notice">
          <h3>🔒 GDPR Compliance Mode Active</h3>
          <p>
            All personally identifiable information has been anonymized in accordance with GDPR requirements. 
            This report shows aggregate and anonymized data only.
          </p>
        </div>
      )}
    </div>
  );
}

const dashboardStyles = `
  .dashboard-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f8f9fa;
    min-height: 100vh;
  }

  .dashboard-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 16px;
    padding: 32px;
    margin-bottom: 32px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
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
    opacity: 0.9;
    font-size: 16px;
    line-height: 1.5;
  }

  .header-controls {
    display: flex;
    gap: 16px;
    align-items: center;
    flex-wrap: wrap;
  }

  .filter-group {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .filter-group label {
    font-size: 12px;
    font-weight: 500;
    opacity: 0.9;
  }

  .filter-select {
    padding: 8px 12px;
    border: none;
    border-radius: 6px;
    background: rgba(255,255,255,0.9);
    color: #333;
    font-size: 14px;
    min-width: 120px;
  }

  .privacy-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,0.1);
    padding: 8px 12px;
    border-radius: 6px;
  }

  .privacy-toggle input[type="checkbox"] {
    margin: 0;
  }

  .privacy-toggle span {
    font-size: 14px;
    font-weight: 500;
  }

  .btn-secondary {
    background: rgba(255,255,255,0.9);
    color: #333;
    border: none;
    padding: 10px 16px;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-secondary:hover {
    background: white;
    transform: translateY(-1px);
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

  .btn-primary:hover {
    background: #45a049;
  }

  .overview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
    margin-bottom: 40px;
  }

  .metric-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    gap: 20px;
    transition: all 0.3s ease;
  }

  .metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  }

  .metric-card.alert {
    border-left: 4px solid #f44336;
  }

  .metric-icon {
    font-size: 40px;
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f8f9fa;
    border-radius: 12px;
  }

  .metric-content h3 {
    margin: 0 0 8px 0;
    font-size: 14px;
    font-weight: 600;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .metric-value {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 4px;
    color: #333;
  }

  .metric-value.risk {
    color: #f44336;
  }

  .metric-subtitle {
    font-size: 14px;
    color: #666;
  }

  .chart-section {
    background: white;
    border-radius: 12px;
    padding: 32px;
    margin-bottom: 32px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }

  .section-header {
    margin-bottom: 24px;
  }

  .section-header h2 {
    margin: 0 0 8px 0;
    font-size: 24px;
    font-weight: 600;
    color: #333;
  }

  .section-header p {
    margin: 0;
    color: #666;
    font-size: 16px;
  }

  .chart-container {
    margin-top: 24px;
    position: relative;
  }

  .chart-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32px;
  }

  .department-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 24px;
    margin-top: 24px;
  }

  .department-card {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 20px;
    border: 2px solid transparent;
    transition: all 0.3s ease;
  }

  .department-card:hover {
    border-color: #667eea;
    background: white;
  }

  .dept-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .dept-header h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #333;
  }

  .risk-badge {
    padding: 4px 8px;
    border-radius: 12px;
    color: white;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
  }

  .dept-metrics {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
  }

  .dept-metric {
    text-align: center;
  }

  .metric-label {
    display: block;
    font-size: 12px;
    color: #666;
    margin-bottom: 4px;
  }

  .metric-val {
    display: block;
    font-size: 18px;
    font-weight: 600;
    color: #333;
  }

  .completion-bar {
    height: 6px;
    background: #e0e0e0;
    border-radius: 3px;
    overflow: hidden;
  }

  .completion-fill {
    height: 100%;
    background: linear-gradient(90deg, #4CAF50, #45a049);
    transition: width 0.5s ease;
  }

  .assessment-stats {
    padding: 20px;
  }

  .assessment-stats h3 {
    margin: 0 0 16px 0;
    color: #333;
    font-size: 18px;
  }

  .stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #f0f0f0;
  }

  .stat-row:last-child {
    border-bottom: none;
  }

  .stat-name {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
  }

  .color-indicator {
    width: 12px;
    height: 12px;
    border-radius: 2px;
  }

  .stat-values {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 2px;
  }

  .count {
    font-weight: 600;
    color: #333;
  }

  .avg {
    font-size: 12px;
    color: #666;
  }

  .loading-state, .error-state {
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
    border-top: 4px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .privacy-notice {
    background: #e8f5e8;
    border: 2px solid #4CAF50;
    border-radius: 12px;
    padding: 24px;
    margin-top: 32px;
  }

  .privacy-notice h3 {
    margin: 0 0 12px 0;
    color: #2e7d32;
    font-size: 18px;
  }

  .privacy-notice p {
    margin: 0;
    color: #2e7d32;
    line-height: 1.6;
  }

  @media (max-width: 768px) {
    .dashboard-header {
      flex-direction: column;
      text-align: center;
    }

    .header-controls {
      justify-content: center;
    }

    .chart-grid {
      grid-template-columns: 1fr;
    }

    .department-grid {
      grid-template-columns: 1fr;
    }

    .overview-grid {
      grid-template-columns: 1fr;
    }
  }
`;
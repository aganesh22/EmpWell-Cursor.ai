import React, { useState, useEffect, useCallback } from 'react';
import { format } from 'date-fns';

interface Notification {
  id: string;
  type: 'assessment_reminder' | 'risk_alert' | 'system' | 'achievement' | 'recommendation';
  title: string;
  message: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  channels: ('in_app' | 'email' | 'sms' | 'push' | 'slack')[];
  scheduledFor?: Date;
  sentAt?: Date;
  readAt?: Date;
  actionUrl?: string;
  metadata?: Record<string, any>;
  userId?: number;
  departmentId?: string;
  isGlobal?: boolean;
}

interface NotificationSettings {
  assessmentReminders: boolean;
  riskAlerts: boolean;
  systemUpdates: boolean;
  achievements: boolean;
  recommendations: boolean;
  emailEnabled: boolean;
  smsEnabled: boolean;
  pushEnabled: boolean;
  slackEnabled: boolean;
  reminderFrequency: 'daily' | 'weekly' | 'monthly';
  quietHours: {
    enabled: boolean;
    start: string;
    end: string;
  };
}

interface NotificationSystemProps {
  userId?: number;
  isAdmin?: boolean;
}

export default function NotificationSystem({ userId, isAdmin = false }: NotificationSystemProps) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [settings, setSettings] = useState<NotificationSettings>({
    assessmentReminders: true,
    riskAlerts: true,
    systemUpdates: true,
    achievements: true,
    recommendations: true,
    emailEnabled: true,
    smsEnabled: false,
    pushEnabled: true,
    slackEnabled: false,
    reminderFrequency: 'weekly',
    quietHours: {
      enabled: false,
      start: '22:00',
      end: '08:00'
    }
  });
  const [showSettings, setShowSettings] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isExpanded, setIsExpanded] = useState(false);
  const [filter, setFilter] = useState<'all' | 'unread' | 'high' | 'urgent'>('all');

  useEffect(() => {
    loadNotifications();
    loadSettings();
    
    // Set up real-time connection
    const eventSource = new EventSource('/api/notifications/stream');
    
    eventSource.onmessage = (event) => {
      const notification: Notification = JSON.parse(event.data);
      handleNewNotification(notification);
    };

    return () => {
      eventSource.close();
    };
  }, [userId]);

  const loadNotifications = async () => {
    try {
      // Mock data - replace with actual API call
      const mockNotifications: Notification[] = [
        {
          id: '1',
          type: 'assessment_reminder',
          title: 'Weekly Wellbeing Check-in',
          message: 'It\'s time for your weekly wellbeing assessment. Taking care of your mental health is important!',
          priority: 'medium',
          channels: ['in_app', 'email'],
          scheduledFor: new Date(Date.now() + 24 * 60 * 60 * 1000),
          actionUrl: '/assessments/new',
          userId: userId
        },
        {
          id: '2',
          type: 'achievement',
          title: 'Streak Achievement! 🎉',
          message: 'Congratulations! You\'ve completed assessments for 7 days in a row. Keep up the great work!',
          priority: 'low',
          channels: ['in_app', 'push'],
          sentAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
          actionUrl: '/profile/achievements',
          userId: userId
        },
        {
          id: '3',
          type: 'recommendation',
          title: 'Personalized Recommendations',
          message: 'Based on your recent assessments, we have some wellness resources that might help you.',
          priority: 'medium',
          channels: ['in_app', 'email'],
          sentAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
          actionUrl: '/resources',
          userId: userId
        }
      ];

      if (isAdmin) {
        mockNotifications.push(
          {
            id: '4',
            type: 'risk_alert',
            title: 'High Risk Alert - Department Operations',
            message: 'Multiple employees in Operations department showing elevated stress levels. Immediate attention required.',
            priority: 'urgent',
            channels: ['in_app', 'email', 'sms'],
            sentAt: new Date(Date.now() - 30 * 60 * 1000),
            actionUrl: '/admin/alerts/4',
            departmentId: 'operations'
          },
          {
            id: '5',
            type: 'system',
            title: 'System Maintenance Scheduled',
            message: 'Scheduled maintenance on Sunday 2AM-4AM EST. All users will be notified.',
            priority: 'medium',
            channels: ['in_app', 'email'],
            scheduledFor: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
            isGlobal: true
          }
        );
      }

      setNotifications(mockNotifications);
      setUnreadCount(mockNotifications.filter(n => !n.readAt && n.sentAt).length);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  };

  const loadSettings = async () => {
    try {
      // Mock settings - replace with actual API call
      // In real implementation, load from user preferences
    } catch (error) {
      console.error('Failed to load notification settings:', error);
    }
  };

  const handleNewNotification = useCallback((notification: Notification) => {
    setNotifications(prev => [notification, ...prev]);
    setUnreadCount(prev => prev + 1);
    
    // Show in-app notification
    if (notification.channels.includes('in_app')) {
      showInAppNotification(notification);
    }
    
    // Request push notification permission and send
    if (notification.channels.includes('push') && 'Notification' in window) {
      if (Notification.permission === 'granted') {
        new Notification(notification.title, {
          body: notification.message,
          icon: '/icon-192x192.png',
          badge: '/badge-72x72.png'
        });
      } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then(permission => {
          if (permission === 'granted') {
            new Notification(notification.title, {
              body: notification.message,
              icon: '/icon-192x192.png'
            });
          }
        });
      }
    }
  }, []);

  const showInAppNotification = (notification: Notification) => {
    // Create temporary toast notification
    const toast = document.createElement('div');
    toast.className = `notification-toast ${notification.priority}`;
    toast.innerHTML = `
      <div class="toast-content">
        <div class="toast-icon">${getNotificationIcon(notification.type)}</div>
        <div class="toast-text">
          <div class="toast-title">${notification.title}</div>
          <div class="toast-message">${notification.message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
      </div>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (toast.parentElement) {
        toast.remove();
      }
    }, 5000);
  };

  const markAsRead = async (notificationId: string) => {
    try {
      // API call to mark as read
      setNotifications(prev => 
        prev.map(n => 
          n.id === notificationId 
            ? { ...n, readAt: new Date() }
            : n
        )
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const now = new Date();
      setNotifications(prev => 
        prev.map(n => ({ ...n, readAt: n.readAt || now }))
      );
      setUnreadCount(0);
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  };

  const deleteNotification = async (notificationId: string) => {
    try {
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  };

  const updateSettings = async (newSettings: Partial<NotificationSettings>) => {
    try {
      setSettings(prev => ({ ...prev, ...newSettings }));
      // API call to save settings
    } catch (error) {
      console.error('Failed to update settings:', error);
    }
  };

  const scheduleNotification = async (notification: Omit<Notification, 'id'>) => {
    try {
      // API call to schedule notification
      console.log('Scheduling notification:', notification);
    } catch (error) {
      console.error('Failed to schedule notification:', error);
    }
  };

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'assessment_reminder': return '📝';
      case 'risk_alert': return '⚠️';
      case 'system': return '🔧';
      case 'achievement': return '🏆';
      case 'recommendation': return '💡';
      default: return '📬';
    }
  };

  const getPriorityColor = (priority: Notification['priority']) => {
    switch (priority) {
      case 'urgent': return '#f44336';
      case 'high': return '#ff9800';
      case 'medium': return '#2196f3';
      case 'low': return '#4caf50';
    }
  };

  const filteredNotifications = notifications.filter(notification => {
    switch (filter) {
      case 'unread': return !notification.readAt && notification.sentAt;
      case 'high': return notification.priority === 'high';
      case 'urgent': return notification.priority === 'urgent';
      default: return true;
    }
  });

  return (
    <>
      <style>{notificationStyles}</style>
      
      {/* Notification Bell */}
      <div className="notification-bell" onClick={() => setIsExpanded(!isExpanded)}>
        <span className="bell-icon">🔔</span>
        {unreadCount > 0 && (
          <span className="notification-badge">{unreadCount > 99 ? '99+' : unreadCount}</span>
        )}
      </div>

      {/* Notification Panel */}
      {isExpanded && (
        <div className="notification-panel">
          <div className="panel-header">
            <h3>Notifications</h3>
            <div className="header-actions">
              <select 
                value={filter} 
                onChange={(e) => setFilter(e.target.value as any)}
                className="filter-select"
              >
                <option value="all">All</option>
                <option value="unread">Unread</option>
                <option value="high">High Priority</option>
                <option value="urgent">Urgent</option>
              </select>
              
              <button onClick={() => setShowSettings(!showSettings)} className="settings-btn">
                ⚙️
              </button>
              
              {unreadCount > 0 && (
                <button onClick={markAllAsRead} className="mark-all-btn">
                  Mark All Read
                </button>
              )}
            </div>
          </div>

          {/* Settings Panel */}
          {showSettings && (
            <div className="settings-panel">
              <h4>Notification Settings</h4>
              
              <div className="settings-group">
                <h5>Notification Types</h5>
                <label>
                  <input 
                    type="checkbox" 
                    checked={settings.assessmentReminders}
                    onChange={(e) => updateSettings({ assessmentReminders: e.target.checked })}
                  />
                  Assessment Reminders
                </label>
                <label>
                  <input 
                    type="checkbox" 
                    checked={settings.riskAlerts}
                    onChange={(e) => updateSettings({ riskAlerts: e.target.checked })}
                  />
                  Risk Alerts
                </label>
                <label>
                  <input 
                    type="checkbox" 
                    checked={settings.achievements}
                    onChange={(e) => updateSettings({ achievements: e.target.checked })}
                  />
                  Achievements
                </label>
                <label>
                  <input 
                    type="checkbox" 
                    checked={settings.recommendations}
                    onChange={(e) => updateSettings({ recommendations: e.target.checked })}
                  />
                  Recommendations
                </label>
              </div>

              <div className="settings-group">
                <h5>Delivery Channels</h5>
                <label>
                  <input 
                    type="checkbox" 
                    checked={settings.emailEnabled}
                    onChange={(e) => updateSettings({ emailEnabled: e.target.checked })}
                  />
                  Email Notifications
                </label>
                <label>
                  <input 
                    type="checkbox" 
                    checked={settings.pushEnabled}
                    onChange={(e) => updateSettings({ pushEnabled: e.target.checked })}
                  />
                  Push Notifications
                </label>
                <label>
                  <input 
                    type="checkbox" 
                    checked={settings.smsEnabled}
                    onChange={(e) => updateSettings({ smsEnabled: e.target.checked })}
                  />
                  SMS Notifications
                </label>
              </div>

              <div className="settings-group">
                <h5>Frequency</h5>
                <select 
                  value={settings.reminderFrequency}
                  onChange={(e) => updateSettings({ reminderFrequency: e.target.value as any })}
                  className="frequency-select"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>

              <div className="settings-group">
                <h5>Quiet Hours</h5>
                <label>
                  <input 
                    type="checkbox" 
                    checked={settings.quietHours.enabled}
                    onChange={(e) => updateSettings({ 
                      quietHours: { ...settings.quietHours, enabled: e.target.checked }
                    })}
                  />
                  Enable Quiet Hours
                </label>
                {settings.quietHours.enabled && (
                  <div className="quiet-hours">
                    <input 
                      type="time" 
                      value={settings.quietHours.start}
                      onChange={(e) => updateSettings({
                        quietHours: { ...settings.quietHours, start: e.target.value }
                      })}
                    />
                    <span>to</span>
                    <input 
                      type="time" 
                      value={settings.quietHours.end}
                      onChange={(e) => updateSettings({
                        quietHours: { ...settings.quietHours, end: e.target.value }
                      })}
                    />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Notifications List */}
          <div className="notifications-list">
            {filteredNotifications.length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">📭</span>
                <p>No notifications</p>
              </div>
            ) : (
              filteredNotifications.map(notification => (
                <div 
                  key={notification.id}
                  className={`notification-item ${!notification.readAt && notification.sentAt ? 'unread' : ''}`}
                  onClick={() => {
                    if (!notification.readAt && notification.sentAt) {
                      markAsRead(notification.id);
                    }
                    if (notification.actionUrl) {
                      window.location.href = notification.actionUrl;
                    }
                  }}
                >
                  <div className="notification-content">
                    <div className="notification-header">
                      <span className="notification-icon">
                        {getNotificationIcon(notification.type)}
                      </span>
                      <span 
                        className="priority-indicator"
                        style={{ backgroundColor: getPriorityColor(notification.priority) }}
                      ></span>
                      <span className="notification-title">{notification.title}</span>
                      <span className="notification-time">
                        {notification.sentAt 
                          ? format(notification.sentAt, 'MMM dd, HH:mm')
                          : notification.scheduledFor 
                            ? `Scheduled for ${format(notification.scheduledFor, 'MMM dd, HH:mm')}`
                            : 'Draft'
                        }
                      </span>
                    </div>
                    
                    <div className="notification-message">
                      {notification.message}
                    </div>
                    
                    <div className="notification-actions">
                      {notification.actionUrl && (
                        <button className="action-btn primary">
                          View Details
                        </button>
                      )}
                      <button 
                        className="action-btn secondary"
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteNotification(notification.id);
                        }}
                      >
                        Dismiss
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Admin Notification Creator */}
      {isAdmin && (
        <NotificationCreator onSchedule={scheduleNotification} />
      )}
    </>
  );
}

// Admin component for creating notifications
function NotificationCreator({ onSchedule }: { onSchedule: (notification: Omit<Notification, 'id'>) => void }) {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    type: 'system' as Notification['type'],
    title: '',
    message: '',
    priority: 'medium' as Notification['priority'],
    channels: ['in_app'] as Notification['channels'],
    scheduledFor: '',
    isGlobal: true,
    departmentId: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const notification: Omit<Notification, 'id'> = {
      ...formData,
      scheduledFor: formData.scheduledFor ? new Date(formData.scheduledFor) : undefined
    };
    
    onSchedule(notification);
    setIsOpen(false);
    setFormData({
      type: 'system',
      title: '',
      message: '',
      priority: 'medium',
      channels: ['in_app'],
      scheduledFor: '',
      isGlobal: true,
      departmentId: ''
    });
  };

  return (
    <>
      <button 
        className="create-notification-btn" 
        onClick={() => setIsOpen(true)}
        title="Create Notification"
      >
        📢
      </button>

      {isOpen && (
        <div className="notification-creator-overlay">
          <div className="notification-creator">
            <h3>Create Notification</h3>
            
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Type:</label>
                <select 
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
                >
                  <option value="system">System</option>
                  <option value="assessment_reminder">Assessment Reminder</option>
                  <option value="risk_alert">Risk Alert</option>
                  <option value="achievement">Achievement</option>
                  <option value="recommendation">Recommendation</option>
                </select>
              </div>

              <div className="form-group">
                <label>Title:</label>
                <input 
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Message:</label>
                <textarea 
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  required
                  rows={3}
                />
              </div>

              <div className="form-group">
                <label>Priority:</label>
                <select 
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value as any })}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>

              <div className="form-group">
                <label>Channels:</label>
                <div className="checkbox-group">
                  {(['in_app', 'email', 'push', 'sms'] as const).map(channel => (
                    <label key={channel}>
                      <input 
                        type="checkbox"
                        checked={formData.channels.includes(channel)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFormData({ 
                              ...formData, 
                              channels: [...formData.channels, channel] 
                            });
                          } else {
                            setFormData({ 
                              ...formData, 
                              channels: formData.channels.filter(c => c !== channel) 
                            });
                          }
                        }}
                      />
                      {channel.replace('_', ' ')}
                    </label>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label>Schedule for later (optional):</label>
                <input 
                  type="datetime-local"
                  value={formData.scheduledFor}
                  onChange={(e) => setFormData({ ...formData, scheduledFor: e.target.value })}
                />
              </div>

              <div className="form-actions">
                <button type="button" onClick={() => setIsOpen(false)}>Cancel</button>
                <button type="submit">
                  {formData.scheduledFor ? 'Schedule' : 'Send Now'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

const notificationStyles = `
  .notification-bell {
    position: relative;
    cursor: pointer;
    padding: 8px;
    border-radius: 50%;
    transition: background-color 0.2s ease;
  }

  .notification-bell:hover {
    background-color: rgba(0, 0, 0, 0.1);
  }

  .bell-icon {
    font-size: 20px;
  }

  .notification-badge {
    position: absolute;
    top: 0;
    right: 0;
    background: #f44336;
    color: white;
    border-radius: 10px;
    padding: 2px 6px;
    font-size: 12px;
    font-weight: bold;
    min-width: 18px;
    text-align: center;
  }

  .notification-panel {
    position: fixed;
    top: 60px;
    right: 20px;
    width: 400px;
    max-height: 600px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    border: 1px solid #e0e0e0;
    z-index: 1000;
    overflow: hidden;
  }

  .panel-header {
    padding: 16px 20px;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #f8f9fa;
  }

  .panel-header h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #333;
  }

  .header-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .filter-select {
    padding: 4px 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 12px;
  }

  .settings-btn, .mark-all-btn {
    padding: 6px 10px;
    border: none;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }

  .settings-btn {
    background: none;
  }

  .mark-all-btn {
    background: #2196f3;
    color: white;
  }

  .settings-panel {
    padding: 16px 20px;
    border-bottom: 1px solid #e0e0e0;
    background: #f8f9fa;
    max-height: 300px;
    overflow-y: auto;
  }

  .settings-panel h4 {
    margin: 0 0 16px 0;
    font-size: 16px;
    color: #333;
  }

  .settings-group {
    margin-bottom: 16px;
  }

  .settings-group h5 {
    margin: 0 0 8px 0;
    font-size: 14px;
    font-weight: 600;
    color: #666;
  }

  .settings-group label {
    display: block;
    margin-bottom: 6px;
    font-size: 14px;
    cursor: pointer;
  }

  .settings-group input[type="checkbox"] {
    margin-right: 8px;
  }

  .frequency-select {
    width: 100%;
    padding: 6px 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
  }

  .quiet-hours {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-top: 8px;
  }

  .quiet-hours input[type="time"] {
    padding: 4px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  .notifications-list {
    max-height: 400px;
    overflow-y: auto;
  }

  .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #666;
  }

  .empty-icon {
    font-size: 48px;
    display: block;
    margin-bottom: 16px;
  }

  .notification-item {
    padding: 16px 20px;
    border-bottom: 1px solid #f0f0f0;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }

  .notification-item:hover {
    background-color: #f8f9fa;
  }

  .notification-item.unread {
    background-color: #fff3e0;
    border-left: 4px solid #ff9800;
  }

  .notification-content {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .notification-header {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .notification-icon {
    font-size: 18px;
  }

  .priority-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  .notification-title {
    font-weight: 600;
    color: #333;
    flex: 1;
  }

  .notification-time {
    font-size: 12px;
    color: #666;
  }

  .notification-message {
    color: #555;
    font-size: 14px;
    line-height: 1.4;
  }

  .notification-actions {
    display: flex;
    gap: 8px;
    margin-top: 4px;
  }

  .action-btn {
    padding: 4px 12px;
    border: none;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }

  .action-btn.primary {
    background: #2196f3;
    color: white;
  }

  .action-btn.secondary {
    background: #f0f0f0;
    color: #666;
  }

  .create-notification-btn {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: #4CAF50;
    color: white;
    border: none;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: transform 0.2s ease;
  }

  .create-notification-btn:hover {
    transform: scale(1.1);
  }

  .notification-creator-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
  }

  .notification-creator {
    background: white;
    border-radius: 12px;
    padding: 24px;
    width: 500px;
    max-width: 90vw;
    max-height: 90vh;
    overflow-y: auto;
  }

  .notification-creator h3 {
    margin: 0 0 20px 0;
    font-size: 20px;
    color: #333;
  }

  .form-group {
    margin-bottom: 16px;
  }

  .form-group label {
    display: block;
    margin-bottom: 6px;
    font-weight: 600;
    color: #333;
  }

  .form-group input,
  .form-group textarea,
  .form-group select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
  }

  .checkbox-group {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
  }

  .checkbox-group label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: normal;
  }

  .form-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    margin-top: 24px;
  }

  .form-actions button {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }

  .form-actions button[type="button"] {
    background: #f0f0f0;
    color: #666;
  }

  .form-actions button[type="submit"] {
    background: #4CAF50;
    color: white;
  }

  .notification-toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    border-left: 4px solid #2196f3;
    padding: 0;
    z-index: 3000;
    animation: slideIn 0.3s ease;
    max-width: 400px;
  }

  .notification-toast.urgent {
    border-left-color: #f44336;
  }

  .notification-toast.high {
    border-left-color: #ff9800;
  }

  .toast-content {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 16px;
  }

  .toast-icon {
    font-size: 20px;
    margin-top: 2px;
  }

  .toast-text {
    flex: 1;
  }

  .toast-title {
    font-weight: 600;
    color: #333;
    margin-bottom: 4px;
  }

  .toast-message {
    color: #666;
    font-size: 14px;
    line-height: 1.4;
  }

  .toast-close {
    background: none;
    border: none;
    font-size: 18px;
    color: #999;
    cursor: pointer;
    padding: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  @media (max-width: 768px) {
    .notification-panel {
      width: calc(100vw - 40px);
      right: 20px;
      left: 20px;
    }

    .notification-creator {
      width: calc(100vw - 40px);
    }

    .checkbox-group {
      flex-direction: column;
    }
  }
`;
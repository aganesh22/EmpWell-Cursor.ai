# 🏢 Enterprise Wellbeing Platform

A comprehensive, enterprise-grade employee mental health and wellbeing assessment platform with advanced analytics, GDPR compliance, and multi-tenant support.

## ✨ Features

### 🧠 Assessment Engine
- **Multiple Assessment Types**: WHO-5, PHQ-9, GAD-7, MBTI, DISC, Big Five, Stress scales
- **Dynamic Question Logic**: Conditional branching and adaptive questioning
- **Real-time Scoring**: Instant results with clinical interpretation
- **Progress Tracking**: Historical data and trend analysis
- **Risk Detection**: Automated flagging of concerning scores

### 👤 User Management & Authentication
- **Multiple SSO Options**: Google Workspace, Azure AD/Microsoft 365
- **Role-based Access Control**: Employee, Manager, Admin, Super Admin
- **Traditional Authentication**: Email/password with secure hashing
- **Department Management**: Organizational structure support
- **User Profiles**: Comprehensive employee information

### 📊 Advanced Analytics & Reporting
- **Real-time Dashboard**: Interactive charts and visualizations
- **Department Comparisons**: Cross-departmental wellbeing metrics
- **Trend Analysis**: Historical data visualization
- **Risk Analytics**: Population-level risk assessment
- **Custom Reports**: Flexible reporting with filters
- **Data Export**: CSV, JSON, PDF report generation

### 🔔 Intelligent Notification System
- **Multi-channel Delivery**: In-app, email, SMS, push notifications
- **Smart Scheduling**: Quiet hours and frequency controls
- **Personalized Reminders**: Assessment completion nudges
- **Risk Alerts**: Automated notifications for concerning scores
- **Admin Notifications**: System alerts and compliance reminders

### � Resources & Recommendations
- **Personalized Content**: AI-driven resource recommendations
- **Multiple Content Types**: Articles, videos, exercises, tools, courses
- **Progress Tracking**: Completion status and bookmarking
- **Search & Filtering**: Advanced content discovery
- **User Preferences**: Customizable recommendation engine

### 🔒 GDPR Compliance & Privacy
- **Consent Management**: Granular consent tracking (Article 7)
- **Data Portability**: Complete data export functionality (Article 20)
- **Right to Erasure**: Account deletion with grace period (Article 17)
- **Processing Records**: Comprehensive audit trail (Article 30)
- **Data Anonymization**: Privacy-preserving analytics
- **Retention Policies**: Automated data lifecycle management

### 🏗️ Enterprise Architecture
- **Scalable Backend**: FastAPI with PostgreSQL
- **Modern Frontend**: React with TypeScript
- **Microservices Ready**: Modular router architecture
- **API-First Design**: RESTful APIs with OpenAPI documentation
- **Container Support**: Docker-ready deployment
- **Environment Flexibility**: Development, staging, production configs

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Redis (optional, for caching)

### Backend Setup

1. **Clone and Setup Environment**
```bash
git clone <repository-url>
cd wellbeing-platform/backend
cp .env.example .env
# Edit .env with your configuration
```

2. **Install Dependencies**
```bash
# Install core dependencies
pip install -r requirements.txt

# Install development/testing dependencies (optional)
pip install -r requirements-dev.txt

# Verify installation
python verify_dependencies.py
```

3. **Database Setup**
```bash
# Create database
createdb empwell

# Run GDPR migration
python create_gdpr_tables.py

# Start the server
uvicorn backend.app.main:app --reload
```

### Frontend Setup

1. **Install and Configure**
```bash
cd ../frontend
npm install
cp .env.example .env
# Edit .env with your configuration
```

2. **Start Development Server**
```bash
npm run dev
```

3. **Access the Application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📖 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/empwell

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# SSO Configuration (Optional)
GOOGLE_CLIENT_ID=your_google_client_id
AZURE_CLIENT_ID=your_azure_client_id
AZURE_TENANT_ID=your_azure_tenant_id

# Notification Services (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@company.com
SMTP_PASSWORD=your_app_password
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
```

#### Frontend (.env)
```bash
# API Configuration
VITE_API_URL=http://localhost:8000

# SSO Configuration (Optional)
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_AZURE_CLIENT_ID=your_azure_client_id
VITE_AZURE_AUTHORITY=https://login.microsoftonline.com/your_tenant_id
VITE_AZURE_REDIRECT_URI=http://localhost:5173
```

## 🏗️ Architecture

### Backend Structure
```
backend/
├── app/
│   ├── models.py          # Database models with GDPR support
│   ├── schemas.py         # Pydantic schemas for API
│   ├── database.py        # Database configuration
│   ├── auth.py           # Authentication utilities
│   ├── main.py           # FastAPI application
│   └── routers/
│       ├── auth.py       # Authentication endpoints
│       ├── users.py      # User management
│       ├── tests.py      # Assessment engine
│       ├── reports.py    # Analytics and reporting
│       ├── resources.py  # Content management
│       ├── notifications.py # Notification system
│       └── gdpr.py       # GDPR compliance
├── requirements.txt       # Python dependencies
└── create_gdpr_tables.py # Database migration
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/
│   │   └── NotificationSystem.tsx
│   ├── lib/
│   │   ├── api.ts           # API client
│   │   ├── google-auth.ts   # Google SSO
│   │   └── azure-auth.ts    # Azure AD SSO
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── Login.tsx
│   │   ├── Resources.tsx
│   │   ├── AdminDashboard.tsx
│   │   ├── EnhancedAdminDashboard.tsx
│   │   └── TestTaker.tsx
│   └── main.tsx
├── package.json
└── .env.example
```

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - Email/password login
- `POST /auth/google` - Google SSO authentication
- `POST /auth/azure` - Azure AD SSO authentication
- `GET /auth/me` - Get current user info

### Assessments
- `GET /tests` - List available assessments
- `GET /tests/{test_key}` - Get specific assessment
- `POST /tests/{test_key}/submit` - Submit assessment responses
- `GET /users/me/attempts` - Get user's assessment history

### Analytics & Reports
- `GET /reports/dashboard` - Main dashboard data
- `GET /reports/department/{dept}` - Department-specific analytics
- `GET /reports/trends` - Wellbeing trends over time
- `GET /reports/export` - Export data as CSV/JSON

### Resources
- `GET /resources` - List all resources
- `GET /resources/recommendations` - Personalized recommendations
- `POST /resources/{id}/bookmark` - Bookmark resource
- `POST /resources/{id}/complete` - Mark resource as completed

### Notifications
- `GET /notifications` - Get user notifications
- `POST /notifications/settings` - Update notification preferences
- `POST /notifications/create` - Create notification (admin)
- `SSE /notifications/stream` - Real-time notification stream

### GDPR Compliance
- `POST /gdpr/consent` - Manage user consent
- `GET /gdpr/consents` - Get user's consent history
- `POST /gdpr/data-export` - Request data export
- `GET /gdpr/data-export/{id}/download` - Download exported data
- `POST /gdpr/forget-me` - Request account deletion
- `GET /gdpr/compliance-report` - GDPR compliance report (admin)

## 🔐 Security Features

### Data Protection
- **Encryption at Rest**: Database encryption support
- **Encryption in Transit**: TLS/SSL for all communications
- **Access Controls**: Role-based permissions
- **Audit Logging**: Comprehensive activity tracking
- **Session Management**: Secure JWT tokens
- **Input Validation**: Comprehensive data sanitization

### Privacy Compliance
- **Data Minimization**: Collect only necessary data
- **Purpose Limitation**: Clear purpose for data processing
- **Storage Limitation**: Automated data retention policies
- **Consent Management**: Granular consent tracking
- **Data Portability**: Easy data export functionality
- **Right to Erasure**: Account deletion with anonymization

## 📊 Analytics & Insights

### Dashboard Features
- **Real-time Metrics**: Live wellbeing indicators
- **Trend Analysis**: Historical data visualization
- **Department Comparisons**: Cross-organizational insights
- **Risk Assessment**: Population-level risk analytics
- **Participation Rates**: Assessment completion tracking
- **Custom Filters**: Flexible data exploration

### Reporting Capabilities
- **Automated Reports**: Scheduled report generation
- **Custom Dashboards**: Configurable analytics views
- **Data Export**: Multiple format support (CSV, JSON, PDF)
- **GDPR-Safe Analytics**: Anonymized reporting options
- **Mobile-Responsive**: Access from any device

## � Deployment

### Development
```bash
# Backend
cd backend && uvicorn backend.app.main:app --reload

# Frontend
cd frontend && npm run dev
```

### Production
```bash
# Backend
cd backend && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm run build && npm run serve
```

### Docker (Coming Soon)
```bash
docker-compose up -d
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## � License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Documentation
- [API Documentation](http://localhost:8000/docs) (when running locally)
- [Frontend Components Guide](./frontend/README.md)
- [Backend API Guide](./backend/README.md)

### Getting Help
- Create an issue for bugs or feature requests
- Check existing documentation
- Review the code comments and examples

## 🗺️ Roadmap

### Upcoming Features
- [ ] Mobile app (React Native)
- [ ] Advanced ML recommendations
- [ ] Integration with HR systems
- [ ] Multi-language support
- [ ] Advanced reporting templates
- [ ] Slack/Teams bot integration
- [ ] Wellness program management
- [ ] Calendar integration for reminders

### Technical Improvements
- [ ] GraphQL API option
- [ ] Advanced caching with Redis
- [ ] Kubernetes deployment configs
- [ ] CI/CD pipeline setup
- [ ] Performance monitoring
- [ ] Load testing suite
- [ ] Security audit tooling

---

**Built with ❤️ for employee wellbeing and mental health support**
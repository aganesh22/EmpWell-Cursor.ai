# EmpWell - Corporate Employee Wellbeing Platform

A modern web application for corporate employee wellbeing assessment and psychometric analysis.

## ✨ Features

- **Employee Wellbeing Assessments**: WHO-5 Wellbeing Index and other validated psychometric tests
- **Dashboard Analytics**: Aggregate reporting for HR teams (department-level insights)
- **Resource Library**: Curated wellbeing resources and recommendations
- **User Management**: Role-based access control for employees and HR administrators
- **Modern UI**: Clean, accessible interface built with React and Tailwind CSS

## 🚀 Quick Start (Bolt/StackBlitz)

This project is optimized for cloud development environments:

1. **Frontend Demo**: The React application runs immediately with mock data
2. **Development**: Uses Vite for fast hot-reload development
3. **No Backend Required**: Mock API provides demo functionality

## 🛠️ Local Development

### Prerequisites
- Node.js 18+ and npm 9+
- Python 3.9+ (for backend)

### Frontend Only
```bash
cd frontend
npm install
npm run dev
```

### Full Stack Development
```bash
# Install frontend dependencies
cd frontend && npm install

# Set up backend (optional)
cd ../backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development servers
npm run dev  # Frontend at http://localhost:5173
# Backend at http://localhost:8000 (if running)
```

## 📁 Project Structure

```
EmpWell-Cursor.ai/
├── frontend/                # React TypeScript application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Route components
│   │   ├── lib/            # API client and utilities
│   │   └── main.tsx        # Application entry point
│   ├── package.json
│   └── vite.config.ts
├── backend/                # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── models/         # Database models
│   │   └── main.py         # FastAPI application
│   └── requirements.txt
├── package.json            # Root workspace configuration
└── stackblitz.config.json  # Cloud environment config
```

## 🎯 Demo Credentials

When using mock mode (default in cloud environments):
- **Email**: demo@example.com
- **Password**: Any password will work
- **Role**: Employee with full access

## 🔧 Environment Variables

```bash
# Frontend (.env in frontend/)
VITE_API_URL=http://localhost:8000  # Optional, defaults to mock mode

# Backend (.env in backend/)
DATABASE_URL=sqlite:///./empwell.db
SECRET_KEY=your-secret-key-here
```

## 🏗️ Architecture

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **State Management**: TanStack Query for server state
- **Routing**: React Router v6
- **API Client**: Axios with mock fallback
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Authentication**: JWT tokens

## 📊 Wellbeing Tests

Implemented psychometric assessments:
- **WHO-5 Wellbeing Index**: 5-question wellbeing assessment
- **Extensible Framework**: Easy to add new validated tests

## 🔒 Security Features

- JWT-based authentication
- Role-based access control (Employee/HR Admin)
- Password hashing with bcrypt
- Input validation and sanitization
- CORS configuration

## 🚀 Deployment

### Frontend (Netlify/Vercel)
```bash
cd frontend
npm run build
# Deploy dist/ folder
```

### Backend (Railway/Render)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Built with ❤️ for employee wellbeing and mental health awareness**
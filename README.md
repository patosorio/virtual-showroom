# Virtual Showroom

A comprehensive virtual showroom application for showcasing swimwear collections with technical specifications, interactive experiences, and complete collection management. Built for fashion designers and brands to present their collections professionally with detailed product information.

## Project Overview

This is a full-stack application designed specifically for fashion/swimwear brands, featuring:

- **Virtual Showroom Experience**: Interactive product showcase with 3D-like viewing
- **Collection Management**: Seasonal collection organization with detailed metadata
- **Product Catalog**: Complete product database with variants, images, and technical specs
- **Admin Dashboard**: Content management system for collections and products
- **Authentication System**: Firebase-based user authentication with role management
- **Technical Documentation**: Size charts, technical drawings, and specifications
- **Responsive Design**: Mobile-first approach with modern UI/UX

## Architecture

This project consists of two main components:

### Frontend (Client)
- **Technology**: Next.js 14 with TypeScript
- **Location**: `client/` directory
- **Key Features**:
  - Virtual showroom with interactive product displays
  - Collection browsing and management
  - Product showcase with color variants and technical specs
  - Lookbook galleries for visual presentation
  - Admin dashboard for content management
  - Authentication with Firebase integration
  - Responsive design with Tailwind CSS and Radix UI
  - React Query for efficient data fetching
  - Multi-tenant architecture support

### Backend (API)
- **Technology**: FastAPI with Python 3.9+
- **Location**: `backend/` directory
- **Key Features**:
  - RESTful API with comprehensive endpoints
  - Firebase Admin SDK integration for authentication
  - PostgreSQL database with SQLAlchemy ORM
  - File upload and storage management
  - Advanced filtering and pagination
  - Database migrations with Alembic
  - Comprehensive error handling and validation
  - Development tools (Black, Ruff, MyPy)

## Getting Started

### Prerequisites
- **Node.js 18+** (for frontend)
- **Python 3.9+** (for backend)
- **PostgreSQL 16** (database)
- **Docker** (optional, for database)
- **Firebase Account** (for authentication)

### Quick Start with Make

The project includes a Makefile for easy development:

```bash
# Start both frontend and backend
make dev

# Or start them individually
make dev-frontend  # Frontend only
make dev-backend   # Backend only
```

### Manual Setup

#### 1. Database Setup
```bash
# Using Docker (recommended)
cd backend
docker-compose up -d

# Or install PostgreSQL locally and create database
psql -c "CREATE DATABASE virtual_showroom;"
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (create .env file)
# See environment variables section below

# Run database migrations
alembic upgrade head

# Start development server
fastapi dev app/main.py
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

#### 3. Frontend Setup
```bash
cd client

# Install dependencies
npm install

# Set up environment variables (create .env.local file)
# See environment variables section below

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Environment Variables

### Backend (.env)
```bash
# Database
POSTGRES_DB=virtual_showroom
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost/virtual_showroom

# Firebase
FIREBASE_CREDENTIALS_PATH=path/to/firebase-service-account.json

# API Settings
ENV=development
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]

# PgAdmin (optional)
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=admin
PGADMIN_CONFIG_SERVER_MODE=False
PGADMIN_CONFIG_MASTER_PASSWORD_REQUIRED=False
```

### Frontend (.env.local)
```bash
# Firebase Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

### Ports
- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Database Admin**: `http://localhost:5051` (PgAdmin)

### Database Management
- **Migrations**: Use Alembic for database schema changes
- **Admin Interface**: PgAdmin available at port 5051
- **Docker**: PostgreSQL runs in Docker container

### Code Quality
- **Backend**: Black (formatting), Ruff (linting), MyPy (type checking)
- **Frontend**: ESLint, TypeScript strict mode
- **Git Hooks**: Pre-commit hooks for code quality

## Tech Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Tailwind Animate
- **UI Components**: Radix UI primitives
- **Icons**: Lucide React
- **Forms**: React Hook Form + Zod validation
- **State Management**: Zustand, React Query (TanStack Query)
- **Authentication**: Firebase Auth
- **HTTP Client**: Axios
- **Notifications**: React Hot Toast, Sonner
- **Development**: ESLint, PostCSS

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **Database**: PostgreSQL 16 with AsyncPG driver
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Authentication**: Firebase Admin SDK
- **Image Processing**: Pillow
- **Development**: Black, Ruff, MyPy
- **Testing**: Pytest
- **Monitoring**: Sentry SDK

### Infrastructure
- **Database**: PostgreSQL 16 (Docker)
- **Authentication**: Firebase
- **File Storage**: Local filesystem (configurable for cloud)
- **Development**: Docker Compose, Make
- **Environment**: Python virtual environments

## API Endpoints

The backend provides comprehensive REST APIs:

### Authentication (`/auth`)
- User registration and login with Firebase
- Profile management
- Role-based access control

### Collections (`/collections`)
- CRUD operations for fashion collections
- Advanced filtering (season, year, status)
- Publishing and SEO management
- Collection analytics

### Products (`/products`)
- Product catalog management
- Variants, images, and technical specifications
- Size charts and technical drawings
- Inventory tracking

### Files (`/files`)
- File upload and management
- Image processing and optimization
- Metadata extraction

### Admin (`/admin`)
- Administrative functions
- User management
- System analytics

## Database Schema

The application uses a comprehensive database schema including:

- **Collections**: Seasonal fashion collections with metadata
- **Products**: Complete product catalog with variants
- **Product Images**: Multi-image support per variant
- **Technical Specifications**: Detailed product specs
- **Technical Drawings**: Technical documentation files
- **Size Charts**: Sizing information and measurements
- **Users**: User profiles and authentication data
- **Files**: File storage and metadata

## Features

### User Authentication
- Firebase-based authentication
- Social login support
- Role-based access control
- Secure token management

### Collection Management
- Seasonal collection organization
- Draft/published states
- SEO optimization
- Order period management

### Product Catalog
- Multi-variant products
- Color and size variations
- Technical specifications
- Image galleries

### Admin Dashboard
- Collection statistics
- User management
- Content management tools
- Analytics overview

### Virtual Showroom
- Interactive product displays
- 3D-like product viewing
- Lookbook presentation
- Technical documentation viewer

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

### Development Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
black .                    # Format code
ruff check .              # Lint code
mypy .                    # Type checking
pytest                    # Run tests

# Frontend
cd client
npm install
npm run lint              # Lint code
npm run build             # Build for production
```

## License

This project is licensed under the [MIT License](LICENSE).
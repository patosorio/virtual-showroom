# Virtual Showroom

A modern virtual showroom application for showcasing swimwear collections with technical specifications and interactive experiences.

## Project Structure

This project consists of two main components:

### Frontend (Client)
- **Technology**: Next.js 14 with TypeScript
- **Location**: `client/` directory
- **Features**:
  - Virtual showroom experience
  - Collection management
  - Product showcases with technical specifications
  - Lookbook galleries
  - Admin dashboard for content management
  - Responsive design with Tailwind CSS

### Backend (API)
- **Technology**: FastAPI with Python
- **Location**: `backend/` directory (to be created)
- **Features**:
  - RESTful API for data management
  - File upload and storage
  - Authentication and authorization
  - Database integration
  - Image processing

## Getting Started

### Prerequisites
- Node.js 18+ (for frontend)
- Python 3.8+ (for backend)
- npm or yarn

### Frontend Setup
```bash
cd client
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Development

- Frontend development server runs on port 3000
- Backend API server runs on port 8000
- API documentation available at `http://localhost:8000/docs` (Swagger UI)

## Tech Stack

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- Lucide React (icons)
- React Hook Form

### Backend
- FastAPI
- Python 3.8+
- SQLAlchemy (ORM)
- Pydantic (data validation)
- JWT authentication

## License

[Add your license here]

## Project Status

🚧 **In Development** - This project is currently in active development.

## Support

For support, please open an issue in the GitHub repository. 
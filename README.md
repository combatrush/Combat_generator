# Combat Gods Animation Platform

An AI-powered animation generation platform that enables users to create high-quality animated content using state-of-the-art AI models.

## 🚀 Features

### Character Generation
- AI-powered character creation from text descriptions
- Multiple style options (modern, fantasy, sci-fi, historical)
- Advanced trait analysis and personality mapping
- Customizable body types and age ranges

### Animation System
- Real-time animation rendering
- Progress tracking and status updates
- Support for various output formats
- Scene composition and management

### AI Integration
- State-of-the-art Stable Diffusion models
- Zero-shot classification for character traits
- Style transfer capabilities
- Advanced scene understanding

## 🛠 Tech Stack

### Backend
- Python 3.9+
- Flask (Web Framework)
- SQLAlchemy (ORM)
- Celery (Task Queue)
- Redis (Cache & Message Broker)
- PostgreSQL (Database)

### Frontend
- React 18
- TypeScript
- Material-UI
- Axios

### AI/ML
- PyTorch
- Transformers
- Stable Diffusion
- Sentence Transformers

## 🏗 Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL
- Redis

### Backend Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Initialize the database:
   ```bash
   flask db upgrade
   ```

5. Start the server:
   ```bash
   flask run
   ```

### Frontend Setup
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

### Running Celery
Start the Celery worker:
```bash
celery -A combat_generator.celery worker --loglevel=info
```

## 📝 API Documentation

### Authentication
- POST `/api/auth/register` - Register a new user
- POST `/api/auth/login` - Login and get JWT token
- POST `/api/auth/logout` - Logout and invalidate token

### Character Generation
- POST `/api/animation/character` - Generate a new character
- GET `/api/animation/character/{id}` - Get character details
- PUT `/api/animation/character/{id}` - Update character

### Animation Management
- POST `/api/animation/create` - Create new animation
- GET `/api/animation/{id}` - Get animation details
- PUT `/api/animation/{id}` - Update animation
- DELETE `/api/animation/{id}` - Delete animation

## 🔒 Security

- JWT-based authentication
- Role-based access control
- Secure password hashing
- API rate limiting
- Input validation and sanitization

## 🧪 Testing

Run backend tests:
```bash
pytest
```

Run frontend tests:
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Docker
1. Build the images:
   ```bash
   docker-compose build
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

### Manual Deployment
1. Set up a production server
2. Configure Nginx/Apache
3. Set up SSL certificates
4. Configure environment variables
5. Start the application with Gunicorn
6. Set up monitoring with Supervisor

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For support, email support@combatgods.com or join our Discord channel.

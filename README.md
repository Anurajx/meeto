# Automated Meeting Secretary

A full-stack application that automatically extracts action items from meeting recordings using Whisper (speech-to-text) and LLM-based extraction, then allows you to sync tasks to Jira or Trello.

## Features

- 🎤 **Audio Processing**: Upload meeting recordings and convert to text using Whisper
- 🤖 **AI-Powered Extraction**: Automatically extract action items, owners, deadlines, and priorities
- 🔐 **Authentication**: OAuth (Google) and Email/Password authentication
- 📋 **Task Management**: View, edit, confirm, and delete extracted tasks
- 🔗 **Integrations**: Sync confirmed tasks to Jira or Trello
- 🔒 **Privacy**: Local-only mode for processing without sending data externally
- 🛡️ **Security**: Automatic redaction of sensitive information (emails, phone numbers, etc.)

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **MySQL/MariaDB**: Database for storing meetings, tasks, and users
- **Whisper**: OpenAI Whisper for speech-to-text (local or API)
- **Groq API**: For LLM-based action item extraction (fast, affordable inference with open-source models)
- **SQLAlchemy**: ORM for database operations
- **JWT**: Authentication tokens

### Frontend
- **React 18**: UI library
- **Tailwind CSS**: Utility-first CSS framework
- **Vite**: Build tool and dev server
- **Axios**: HTTP client
- **React Router**: Client-side routing

## Project Structure

```
meeto/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── services/      # Business logic (Whisper, LLM, Jira, Trello)
│   │   ├── models.py      # Database models
│   │   ├── database.py    # Database configuration
│   │   ├── config.py      # Application settings
│   │   └── main.py        # FastAPI app entry point
│   ├── requirements.txt
│   └── alembic.ini        # Database migrations
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable React components
│   │   ├── contexts/      # React contexts (Auth)
│   │   ├── pages/         # Page components
│   │   ├── services/      # API client
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- MySQL 5.7+ or MariaDB 10.2+ (installed locally - **no Docker required!**)
- FFmpeg (for audio processing)

**MySQL Installation:**
- **Windows**: [Download MySQL Installer](https://dev.mysql.com/downloads/installer/) or use XAMPP - see `SETUP_MYSQL.md`
- **macOS**: `brew install mysql && brew services start mysql`
- **Linux**: `sudo apt-get install mysql-server && sudo systemctl start mysql`

**Note:** MySQL 5.7+ or MariaDB 10.2+ is required for JSON column support.

**Need help with MySQL setup?** See `SETUP_MYSQL.md` for detailed platform-specific instructions.

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg:**
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

5. **Set up MySQL database:**
   
   Create the database (replace with your MySQL root password):
   ```bash
   # Connect to MySQL
   mysql -u root -p
   
   # Create database
   CREATE DATABASE meeting_secretary CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   EXIT;
   ```

6. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

   Required environment variables:
   - `DATABASE_URL`: Supabase connection string (e.g., `postgresql://postgres:YOUR_PASSWORD@db.YOUR_REF.supabase.co:5432/postgres`)
   - `SECRET_KEY`: Secret key for JWT tokens
   - `GROQ_API_KEY`: Groq API key (for LLM extraction) - Get from [console.groq.com](https://console.groq.com) - see `SETUP_GROQ.md`
   - Optional: `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`
   - Optional: `TRELLO_API_KEY`, `TRELLO_API_TOKEN`
   
   **Important:** 
   - Get your Supabase connection string from Dashboard → Settings → Database
   - Get your Groq API key from [console.groq.com](https://console.groq.com) (free tier available)
   - Replace `YOUR_PASSWORD` and `YOUR_REF` with your actual Supabase credentials

7. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

   If migrations don't exist yet, create initial migration:
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

8. **Start the backend server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## Configuration

### Local-Only Mode

To enable local-only processing (no data sent to external APIs):

1. Set `ENABLE_LOCAL_MODE=true` in backend `.env`
2. Set `USE_LOCAL_WHISPER=true` to use local Whisper model
3. Use local LLM (Ollama) by setting `ENABLE_LOCAL_MODE=true` and running Ollama

### Whisper Models

Available Whisper models (from smallest to largest):
- `tiny` (~39 MB)
- `base` (~74 MB)
- `small` (~244 MB)
- `medium` (~769 MB)
- `large` (~1550 MB)

Set `WHISPER_MODEL=base` in `.env` (default is `base`)

### Data Redaction

Automatic redaction of sensitive information is enabled by default. Set `ENABLE_DATA_REDACTION=false` to disable.

Redacted patterns:
- Email addresses
- Phone numbers
- SSN
- Credit card numbers
- IP addresses
- API keys and tokens

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Meetings
- `POST /api/v1/meetings/upload` - Upload meeting audio
- `GET /api/v1/meetings` - List all meetings
- `GET /api/v1/meetings/{id}` - Get meeting details
- `DELETE /api/v1/meetings/{id}` - Delete meeting

### Tasks
- `GET /api/v1/tasks` - List tasks
- `GET /api/v1/tasks/{id}` - Get task details
- `PATCH /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `POST /api/v1/tasks/{id}/confirm` - Confirm task
- `POST /api/v1/tasks/{id}/sync` - Sync task to Jira/Trello

### Integrations
- `GET /api/v1/integrations` - List integrations
- `POST /api/v1/integrations` - Create integration
- `DELETE /api/v1/integrations/{id}` - Delete integration
- `PATCH /api/v1/integrations/{id}/toggle` - Toggle integration

## Usage

1. **Register/Login**: Create an account or login
2. **Upload Meeting**: Upload an audio file from your meeting
3. **Wait for Processing**: The system will transcribe and extract action items
4. **Review Tasks**: View extracted tasks on the Tasks page
5. **Edit/Confirm**: Edit task details and confirm important tasks
6. **Sync to External Services**: Connect Jira or Trello and sync confirmed tasks

## Jira Integration

1. Get your Jira API token:
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Create an API token

2. In the Integrations page, enter:
   - Base URL: `https://your-domain.atlassian.net`
   - Email: Your Jira email
   - API Token: Your API token
   - Project Key: Your project key (optional)

## Trello Integration

1. Get your Trello API key and token:
   - Go to https://trello.com/app-key
   - Copy your API key
   - Generate a token: `https://trello.com/1/authorize?expiration=never&scope=read,write&response_type=token&name=MeetingSecretary&key=YOUR_API_KEY`

2. In the Integrations page, enter:
   - API Key: Your Trello API key
   - API Token: Your generated token
   - Board ID: Your Trello board ID (optional)

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Database Migrations

```bash
cd backend
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` files
2. **API Keys**: Store securely and rotate regularly
3. **Data Redaction**: Enabled by default for sensitive information
4. **HTTPS**: Use HTTPS in production
5. **CORS**: Configure CORS origins appropriately
6. **Rate Limiting**: Consider adding rate limiting for production

## Production Deployment

1. Set `ENVIRONMENT=production` in `.env`
2. Use a production database (managed MySQL/MariaDB)
3. Set strong `SECRET_KEY`
4. Configure proper CORS origins
5. Use a reverse proxy (nginx) with SSL
6. Set up monitoring and logging

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.


# Quick Start Guide

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.9+ installed
- ✅ Node.js 18+ installed
- ✅ Supabase account (free tier works!)
- ✅ FFmpeg installed

## Step-by-Step Setup

### 1. Set Up Supabase (No Local Database Needed!)

**Create a Supabase account and project:**

1. Go to [supabase.com](https://supabase.com) and sign up (free tier available)
2. Click "New Project"
3. Fill in project details:
   - **Name**: `meeting-secretary` (or your choice)
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose closest to you
4. Wait 1-2 minutes for project creation

**Get your connection string:**

1. In Supabase dashboard → **Settings** → **Database**
2. Scroll to **Connection string** section
3. Copy the connection string (URI format)
4. It looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`
5. Replace `[YOUR-PASSWORD]` with the password you set

**Note:** No local database installation needed! Supabase handles everything.

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings (minimum: DATABASE_URL, SECRET_KEY)

# Initialize database (create tables)
python init_db.py

# Or use Alembic migrations
alembic upgrade head

# Start backend server
python run.py
# Or: uvicorn app.main:app --reload --port 8000
```

Backend will be running at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be running at `http://localhost:3000`

## First Steps

1. **Register/Login**: Go to `http://localhost:3000` and create an account
2. **Upload a Meeting**: Upload an audio file (MP3, WAV, etc.)
3. **Wait for Processing**: The system will transcribe and extract action items
4. **Review Tasks**: Check the Tasks page for extracted items
5. **Sync to External**: Configure Jira/Trello integration to sync tasks

## Environment Variables (Minimum Required)

In `backend/.env`:
```env
# Update with your Supabase connection string
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres
SECRET_KEY=your-secret-key-here

# Groq API for LLM extraction (recommended - fast and affordable)
GROQ_API_KEY=your-groq-api-key  # Get from console.groq.com - see SETUP_GROQ.md
LLM_MODEL=llama-3.1-70b-versatile  # Optional: Groq model name
```

**Need Groq API key?** See `SETUP_GROQ.md` for step-by-step setup instructions.

**Note:** 
- Replace `YOUR_PASSWORD` with your Supabase database password
- Replace `YOUR_PROJECT_REF` with your Supabase project reference ID
- Get the connection string from Supabase Dashboard → Settings → Database

## Local-Only Mode

For privacy, enable local-only mode:
```env
ENABLE_LOCAL_MODE=true
USE_LOCAL_WHISPER=true
```

This requires:
- Local Whisper model (downloaded automatically)
- Local LLM (Ollama) for extraction

## Troubleshooting

### Database Connection Error
- **Verify Supabase project is active**:
  - Go to Supabase dashboard
  - Check if project is paused (free tier pauses after 1 week inactivity)
  - Resume project if needed
- **Check connection string format**:
  - Must be: `postgresql://postgres:PASSWORD@db.REF.supabase.co:5432/postgres`
  - No spaces, proper URL encoding
  - Password might need URL encoding if it has special characters
- **Verify password**:
  - Reset password in Supabase Dashboard → Settings → Database if needed
- **Check Supabase dashboard**:
  - Go to Table Editor to see if connection works
  - Check SQL Editor to run test queries

**Need detailed Supabase setup?** See `SETUP_SUPABASE.md` for complete instructions.

### Whisper Model Download
- First run will download the Whisper model (can take time)
- Models are cached for future use

### Audio Processing Fails
- Ensure FFmpeg is installed and in PATH
- Check audio file format (supported: MP3, WAV, M4A, OGG, FLAC)
- Verify file size is under 100MB

### Frontend Can't Connect to Backend
- Ensure backend is running on port 8000
- Check CORS settings in backend config
- Verify API_BASE_URL in frontend

## Next Steps

- Configure Jira/Trello integrations for task syncing
- Set up email notifications (if using email auth)
- Customize extraction prompts for your use case
- Deploy to production (see README.md for production setup)


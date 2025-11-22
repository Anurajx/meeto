# Supabase Setup Guide

This project uses Supabase as the database (PostgreSQL-based backend-as-a-service). No local database installation needed!

## What is Supabase?

Supabase is an open-source Firebase alternative that provides:
- PostgreSQL database (hosted)
- Authentication
- Real-time subscriptions
- Storage
- And more...

**For this project, we only use the PostgreSQL database feature.**

## Step-by-Step Setup

### 1. Create a Supabase Account

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project" or "Sign up"
3. Sign up with GitHub, Google, or email

### 2. Create a New Project

1. Click "New Project" in your dashboard
2. Fill in the project details:
   - **Name**: `meeting-secretary` (or your preferred name)
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose the region closest to you
   - **Pricing Plan**: Free tier is fine for development

3. Wait for the project to be created (takes 1-2 minutes)

### 3. Get Your Database Connection String

1. In your Supabase project dashboard, go to **Settings** → **Database**
2. Scroll down to **Connection string**
3. Select **URI** or **Connection pooling** tab
4. Copy the connection string

**Option 1: Direct Connection (Recommended for Development)**
```
postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

**Option 2: Connection Pooler (Recommended for Production)**
```
postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

**Important:** Replace `[YOUR-PASSWORD]` with the database password you set when creating the project.

### 4. Get Your Project Reference

1. In Supabase dashboard, go to **Settings** → **General**
2. Find **Reference ID** - this is your `[YOUR-PROJECT-REF]`
3. You'll also see it in your connection string

### 5. Configure Your Backend

1. Open `backend/.env` file
2. Set your `DATABASE_URL`:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
```

Replace:
- `YOUR_PASSWORD` with your database password
- `xxxxx` with your project reference ID

**Example:**
```env
DATABASE_URL=postgresql://postgres:mypassword123@db.abcdefghijklmnop.supabase.co:5432/postgres
```

### 5. Initialize the Database Schema

Run the initialization script to create all tables:

```bash
cd backend
python init_db.py
```

Or use Alembic migrations:

```bash
cd backend
alembic upgrade head
```

That's it! Your database is ready to use.

## Connection String Formats

### Direct Connection
```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```
- Port: `5432`
- Good for: Development, direct access
- Max connections: Limited by your plan

### Connection Pooler (Session Mode)
```
postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
```
- Port: `5432`
- Good for: Applications with many connections
- Max connections: Higher limit

### Transaction Mode (Connection Pooler)
```
postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?pgbouncer=true
```
- Port: `6543`
- Good for: Serverless functions, edge functions
- Connection reuse: Optimized

## Finding Your Connection Details

### Method 1: Supabase Dashboard

1. Go to **Settings** → **Database**
2. Scroll to **Connection string** section
3. Copy the connection string
4. Replace `[YOUR-PASSWORD]` with your actual password

### Method 2: Supabase Dashboard - Connection Info

1. Go to **Settings** → **Database**
2. Find **Connection info** section
3. You'll see:
   - **Host**: `db.[PROJECT-REF].supabase.co`
   - **Database name**: `postgres`
   - **Port**: `5432`
   - **User**: `postgres`
   - **Password**: The one you set (or reset it here)

### Method 3: Using Supabase CLI (Advanced)

```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Link your project
supabase link --project-ref [YOUR-PROJECT-REF]

# Get connection string
supabase status
```

## Reset Database Password

If you forgot your password:

1. Go to **Settings** → **Database**
2. Scroll to **Database password** section
3. Click **Reset database password**
4. Enter a new password and confirm
5. Update your `.env` file with the new password

## Database Management

### Access via Supabase Dashboard

1. Go to **Table Editor** in your Supabase dashboard
2. View and edit data directly
3. Create tables manually (or use migrations)

### Access via SQL Editor

1. Go to **SQL Editor** in your Supabase dashboard
2. Run SQL queries directly
3. View query results

### Access via psql (Command Line)

```bash
# Install PostgreSQL client (if not installed)
# Windows: Included with PostgreSQL installer
# macOS: brew install postgresql
# Linux: sudo apt-get install postgresql-client

# Connect to Supabase
psql "postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres"
```

## Free Tier Limits

Supabase free tier includes:
- **Database size**: 500 MB
- **Bandwidth**: 2 GB
- **API requests**: Unlimited
- **Database connections**: Limited

**Note**: For production, consider upgrading to a paid plan.

## Security Best Practices

1. **Never commit passwords** - Use `.env` file (already in `.gitignore`)
2. **Use connection pooler** for production to handle more connections
3. **Enable Row Level Security (RLS)** if needed (not required for this project)
4. **Regular backups** - Supabase provides automatic backups on paid plans
5. **Monitor usage** - Check dashboard for usage limits

## Troubleshooting

### Can't Connect to Database

1. **Check connection string format**:
   - Must be: `postgresql://postgres:PASSWORD@db.REF.supabase.co:5432/postgres`
   - No spaces, proper URL encoding

2. **Verify password**:
   - Password might have special characters - URL encode if needed
   - Reset password in Supabase dashboard if unsure

3. **Check project status**:
   - Project might be paused (free tier pauses after 1 week of inactivity)
   - Resume project in Supabase dashboard

4. **Verify network access**:
   - Check if your IP is blocked (unlikely)
   - Try from different network

### Connection Timeout

1. **Use connection pooler** instead of direct connection
2. **Check your firewall** - port 5432 might be blocked
3. **Try transaction mode** pooler (port 6543)

### Database Size Limit

1. **Check usage** in Supabase dashboard
2. **Delete old data** if approaching limit
3. **Upgrade plan** if needed

### Migration Errors

1. **Check database connection** first
2. **Verify Alembic configuration** in `alembic.ini`
3. **Check Supabase SQL editor** for any errors
4. **Run migrations manually** via SQL editor if needed

## Switching Between Environments

### Development
Use direct connection string:
```env
DATABASE_URL=postgresql://postgres:dev_password@db.dev_ref.supabase.co:5432/postgres
```

### Production
Use connection pooler:
```env
DATABASE_URL=postgresql://postgres.prod_ref:prod_password@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true
```

## Useful Supabase Resources

- **Dashboard**: https://supabase.com/dashboard
- **Documentation**: https://supabase.com/docs
- **Database Docs**: https://supabase.com/docs/guides/database
- **Connection Pooling**: https://supabase.com/docs/guides/database/connecting-to-postgres

## Next Steps

After setting up Supabase:

1. ✅ Update `backend/.env` with your connection string
2. ✅ Run `python init_db.py` to create tables
3. ✅ Start your backend server
4. ✅ Verify connection by checking Supabase dashboard → Table Editor

Your database is now ready! 🎉


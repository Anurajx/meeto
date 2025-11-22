# Database Connection Troubleshooting

## Error: "could not translate host name to address"

This means your computer cannot resolve the Supabase hostname to an IP address. Here are solutions:

### Quick Fixes (Try These First)

#### 1. Check Your Internet Connection
```powershell
# Test if you can reach Supabase
ping supabase.com
```

#### 2. Try Using Google DNS (Temporary Fix)
```powershell
# Flush DNS cache
ipconfig /flushdns

# Test DNS resolution
nslookup db.jffnasosomfxbnufvocj.supabase.co
```

#### 3. Check if Supabase Project is Active

1. Go to [supabase.com/dashboard](https://supabase.com/dashboard)
2. Check if your project is **paused** (free tier pauses after 1 week inactivity)
3. If paused, click **"Resume"** or **"Restore"**
4. Wait 1-2 minutes for the project to wake up

#### 4. Verify Your Connection String

Check your `backend/.env` file:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.jffnasosomfxbnufvocj.supabase.co:5432/postgres
```

**Common Issues:**
- Password might have special characters that need URL encoding
- Hostname might be incorrect
- Port should be `5432` for direct connection

#### 5. Test Connection with psql (If Installed)

```powershell
# Test if you can connect directly
psql "postgresql://postgres:YOUR_PASSWORD@db.jffnasosomfxbnufvocj.supabase.co:5432/postgres"
```

### Network-Specific Fixes

#### Option 1: Change DNS Server (Windows)

1. Open **Network Settings**
2. Go to **Change adapter options**
3. Right-click your network → **Properties**
4. Select **Internet Protocol Version 4 (TCP/IPv4)** → **Properties**
5. Select **"Use the following DNS server addresses"**
6. Set:
   - Preferred DNS: `8.8.8.8` (Google)
   - Alternate DNS: `8.8.4.4` (Google)
7. Click **OK** and restart your computer

#### Option 2: Try Connection Pooler Instead

In Supabase Dashboard → Settings → Database:
- Use **Connection Pooler** connection string instead
- It might resolve differently

```env
# Instead of direct connection, try pooler:
DATABASE_URL=postgresql://postgres.jffnasosomfxbnufvocj:YOUR_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

#### Option 3: Check Firewall/Corporate Network

If you're on a corporate network:
- The network might block Supabase domains
- Try from a different network (mobile hotspot)
- Contact IT to whitelist `*.supabase.co`

### Verify Supabase Project Status

1. **Check Supabase Dashboard:**
   - Go to https://supabase.com/dashboard
   - Verify project `jffnasosomfxbnufvocj` exists
   - Check project status (Active/Paused)

2. **Get Fresh Connection String:**
   - Go to Settings → Database
   - Copy the connection string again
   - Make sure password is correct

3. **Reset Database Password** (if needed):
   - Go to Settings → Database
   - Click "Reset database password"
   - Update `.env` with new password

### Alternative: Use Connection Pooler

Connection pooler often works better through firewalls:

1. Go to Supabase Dashboard → Settings → Database
2. Find **Connection pooling** section
3. Copy the **Session mode** or **Transaction mode** connection string
4. Update your `.env`:

```env
# Session mode (recommended)
DATABASE_URL=postgresql://postgres.jffnasosomfxbnufvocj:YOUR_PASSWORD@aws-0-us-east-1.pooler.supabase.com:5432/postgres

# Or Transaction mode (for serverless)
DATABASE_URL=postgresql://postgres.jffnasosomfxbnufvocj:YOUR_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true
```

### Test DNS Resolution

Run these commands to diagnose:

```powershell
# Flush DNS cache
ipconfig /flushdns

# Try to resolve the hostname
nslookup db.jffnasosomfxbnufvocj.supabase.co

# Try ping
ping db.jffnasosomfxbnufvocj.supabase.co

# Check if port 5432 is accessible
Test-NetConnection -ComputerName db.jffnasosomfxbnufvocj.supabase.co -Port 5432
```

### If Nothing Works

1. **Create a new Supabase project** (if current one is problematic)
2. **Use a different network** (mobile hotspot)
3. **Contact Supabase support** if project seems deleted/corrupted

### Quick Test Script

Create a test file `test_connection.py`:

```python
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print("✅ Connection successful!")
        print(result.fetchone())
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run it:
```powershell
cd backend
python test_connection.py
```


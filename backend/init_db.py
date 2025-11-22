#!/usr/bin/env python3
"""
Initialize database and create tables
"""
import sys
import socket
from app.database import engine, Base
from app.models import User, Meeting, Task, Integration
from app.config import settings
from urllib.parse import urlparse

def test_dns_resolution(hostname):
    """Test if hostname can be resolved"""
    try:
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS Resolution: {hostname} -> {ip}")
        return True
    except socket.gaierror as e:
        print(f"❌ DNS Resolution Failed: {hostname}")
        print(f"   Error: {e}")
        return False

def test_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    # Extract hostname from DATABASE_URL
    try:
        parsed = urlparse(settings.DATABASE_URL)
        hostname = parsed.hostname
        port = parsed.port or 5432
        
        print(f"📡 Hostname: {hostname}")
        print(f"🔌 Port: {port}")
        
        # Test DNS resolution
        if not test_dns_resolution(hostname):
            print("\n❌ Cannot resolve hostname. Possible issues:")
            print("   1. Internet connection problem")
            print("   2. DNS server issue (try: ipconfig /flushdns)")
            print("   3. Supabase project might be paused")
            print("   4. Firewall blocking DNS queries")
            print("\n💡 Solutions:")
            print("   - Check Supabase dashboard to ensure project is active")
            print("   - Try using connection pooler instead")
            print("   - Check your internet connection")
            print("   - See TROUBLESHOOTING_DB.md for detailed help")
            return False
        
        # Try to connect
        print("\n🔗 Attempting to connect...")
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"   Database version: {version[:50]}...")
            return True
            
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\n💡 Troubleshooting steps:")
        print("   1. Verify DATABASE_URL in .env file is correct")
        print("   2. Check if Supabase project is active (not paused)")
        print("   3. Verify database password is correct")
        print("   4. Try connection pooler connection string")
        print("   5. See TROUBLESHOOTING_DB.md for detailed help")
        return False

def init_db():
    """Create all database tables"""
    print("=" * 60)
    print("🗄️  Database Initialization")
    print("=" * 60)
    
    # Test connection first
    if not test_connection():
        print("\n❌ Connection test failed. Cannot proceed with table creation.")
        sys.exit(1)
    
    print("\n📋 Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        print("\n📊 Tables created:")
        for table in Base.metadata.tables.keys():
            print(f"   - {table}")
    except Exception as e:
        print(f"\n❌ Failed to create tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()


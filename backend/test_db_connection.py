#!/usr/bin/env python3
"""
Quick database connection test script
"""
import socket
import sys
from urllib.parse import urlparse
from app.config import settings

def main():
    print("=" * 60)
    print("🧪 Database Connection Test")
    print("=" * 60)
    
    # Parse connection string
    try:
        parsed = urlparse(settings.DATABASE_URL)
        hostname = parsed.hostname
        port = parsed.port or 5432
        user = parsed.username
        database = parsed.path[1:] if parsed.path else "postgres"
        
        print(f"\n📋 Connection Details:")
        print(f"   Hostname: {hostname}")
        print(f"   Port: {port}")
        print(f"   User: {user}")
        print(f"   Database: {database}")
        print(f"   Has password: {'Yes' if parsed.password else 'No'}")
        
        # Test DNS
        print(f"\n🔍 Step 1: Testing DNS resolution...")
        try:
            ip = socket.gethostbyname(hostname)
            print(f"   ✅ Success: {hostname} -> {ip}")
        except socket.gaierror as e:
            print(f"   ❌ Failed: {e}")
            print(f"\n💡 DNS Resolution Failed!")
            print(f"   Your computer cannot resolve the hostname.")
            print(f"\n   Quick fixes:")
            print(f"   1. Check internet connection")
            print(f"   2. Run: ipconfig /flushdns (Windows)")
            print(f"   3. Check if Supabase project is active (not paused)")
            print(f"   4. Try different DNS server (8.8.8.8)")
            return False
        
        # Test port connectivity
        print(f"\n🔍 Step 2: Testing port connectivity...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((ip, port))
            sock.close()
            
            if result == 0:
                print(f"   ✅ Port {port} is open and reachable")
            else:
                print(f"   ⚠️  Port {port} might be blocked (firewall/proxy)")
                print(f"   But let's try connecting anyway...")
        except Exception as e:
            print(f"   ⚠️  Port test failed: {e}")
        
        # Test actual database connection
        print(f"\n🔍 Step 3: Testing database connection...")
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(settings.DATABASE_URL, connect_args={"connect_timeout": 10})
            
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                print(f"   ✅ Database connection successful!")
                print(f"   PostgreSQL version: {version[:80]}...")
                return True
                
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            
            error_str = str(e).lower()
            if "password" in error_str or "authentication" in error_str:
                print(f"\n💡 Authentication Error:")
                print(f"   - Check if database password is correct")
                print(f"   - Reset password in Supabase dashboard if needed")
            elif "timeout" in error_str:
                print(f"\n💡 Connection Timeout:")
                print(f"   - Check firewall settings")
                print(f"   - Try connection pooler instead")
            elif "could not translate host" in error_str:
                print(f"\n💡 DNS Resolution Error:")
                print(f"   - Project might be paused - check Supabase dashboard")
                print(f"   - Try: ipconfig /flushdns")
                print(f"   - Check internet connection")
            
            return False
            
    except Exception as e:
        print(f"\n❌ Error parsing connection string: {e}")
        print(f"   Check your DATABASE_URL in .env file")
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed! Database is ready to use.")
    else:
        print("❌ Connection test failed. See TROUBLESHOOTING_DB.md for help.")
    print("=" * 60)
    sys.exit(0 if success else 1)


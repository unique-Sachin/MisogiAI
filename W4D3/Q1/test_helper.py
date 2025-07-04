#!/usr/bin/env python3
"""
Interactive test helper for MCP Discord Server
Run this script to test the server endpoints interactively
"""

import requests
import json
import sys
from typing import Optional

BASE_URL = "http://localhost:8000"

class TestHelper:
    def __init__(self):
        self.admin_key: Optional[str] = None
        self.write_key: Optional[str] = None
        self.read_key: Optional[str] = None
        
    def test_health(self):
        """Test health endpoint"""
        print("🏥 Testing health endpoint...")
        try:
            response = requests.get(f"{BASE_URL}/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def create_admin_key(self, name: str = "Test Admin Key"):
        """Create an admin API key"""
        print(f"🔑 Creating admin API key: {name}")
        try:
            response = requests.post(
                f"{BASE_URL}/admin/api-keys",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": "bootstrap-admin-key"
                },
                json={
                    "name": name,
                    "role": "admin"
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 201:
                data = response.json()
                self.admin_key = data["secret"]
                print(f"✅ Admin key created: {self.admin_key}")
                print("⚠️  SAVE THIS KEY - it won't be shown again!")
                return True
            else:
                print(f"❌ Failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def create_write_key(self, name: str = "Test Write Key"):
        """Create a write API key"""
        if not self.admin_key:
            print("❌ Need admin key first!")
            return False
            
        print(f"✍️  Creating write API key: {name}")
        try:
            response = requests.post(
                f"{BASE_URL}/admin/api-keys",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.admin_key
                },
                json={
                    "name": name,
                    "role": "write"
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 201:
                data = response.json()
                self.write_key = data["secret"]
                print(f"✅ Write key created: {self.write_key}")
                return True
            else:
                print(f"❌ Failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def create_read_key(self, name: str = "Test Read Key"):
        """Create a read API key"""
        if not self.admin_key:
            print("❌ Need admin key first!")
            return False
            
        print(f"👁️  Creating read API key: {name}")
        try:
            response = requests.post(
                f"{BASE_URL}/admin/api-keys",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.admin_key
                },
                json={
                    "name": name,
                    "role": "read"
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 201:
                data = response.json()
                self.read_key = data["secret"]
                print(f"✅ Read key created: {self.read_key}")
                return True
            else:
                print(f"❌ Failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def list_api_keys(self):
        """List all API keys"""
        if not self.admin_key:
            print("❌ Need admin key first!")
            return False
            
        print("📋 Listing API keys...")
        try:
            response = requests.get(
                f"{BASE_URL}/admin/api-keys",
                headers={"X-API-Key": self.admin_key}
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                keys = response.json()
                print(f"Found {len(keys)} keys:")
                for key in keys:
                    print(f"  - {key['name']} ({key['role']}) - Created: {key['created_at']}")
                return True
            else:
                print(f"❌ Failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_discord_send_message(self, channel_id: str, message: str):
        """Test sending a Discord message"""
        if not self.write_key:
            print("❌ Need write key first!")
            return False
            
        print(f"💬 Sending message to channel {channel_id}")
        try:
            response = requests.post(
                f"{BASE_URL}/discord/send_message",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.write_key
                },
                json={
                    "channel_id": channel_id,
                    "content": message
                }
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_discord_get_messages(self, channel_id: str, limit: int = 10):
        """Test getting Discord messages"""
        if not self.read_key:
            print("❌ Need read key first!")
            return False
            
        print(f"📨 Getting {limit} messages from channel {channel_id}")
        try:
            response = requests.get(
                f"{BASE_URL}/discord/messages",
                params={"channel_id": channel_id, "limit": limit},
                headers={"X-API-Key": self.read_key}
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                messages = response.json()
                print(f"Found {len(messages)} messages")
                for msg in messages[:3]:  # Show first 3
                    print(f"  - {msg.get('author', {}).get('username', 'Unknown')}: {msg.get('content', '')[:50]}...")
                return True
            else:
                print(f"❌ Failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_discord_channel_info(self, channel_id: str):
        """Test getting Discord channel info"""
        if not self.read_key:
            print("❌ Need read key first!")
            return False
            
        print(f"ℹ️  Getting channel info for {channel_id}")
        try:
            response = requests.get(
                f"{BASE_URL}/discord/channel_info",
                params={"channel_id": channel_id},
                headers={"X-API-Key": self.read_key}
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                info = response.json()
                print(f"Channel: {info.get('name', 'Unknown')} (Type: {info.get('type', 'Unknown')})")
                return True
            else:
                print(f"❌ Failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_permission_failure(self):
        """Test that read key can't send messages"""
        if not self.read_key:
            print("❌ Need read key first!")
            return False
            
        print("🚫 Testing permission failure (read key trying to send message)")
        try:
            response = requests.post(
                f"{BASE_URL}/discord/send_message",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.read_key
                },
                json={
                    "channel_id": "123456789",
                    "content": "This should fail"
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 403:
                print("✅ Permission correctly denied!")
                return True
            else:
                print(f"❌ Expected 403, got {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

def main():
    helper = TestHelper()
    
    print("🚀 MCP Discord Server Test Helper")
    print("=" * 50)
    
    # Test health
    if not helper.test_health():
        print("❌ Server not responding! Make sure it's running on port 8000")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Create keys
    print("Setting up API keys...")
    helper.create_admin_key()
    helper.create_write_key()
    helper.create_read_key()
    
    print("\n" + "=" * 50)
    
    # List keys
    helper.list_api_keys()
    
    print("\n" + "=" * 50)
    
    # Interactive testing
    print("🎯 Interactive Testing")
    print("Enter a Discord channel ID to test with (or 'skip' to skip Discord tests):")
    channel_id = input("Channel ID: ").strip()
    
    if channel_id and channel_id.lower() != 'skip':
        print(f"\nTesting with channel ID: {channel_id}")
        
        # Test Discord endpoints
        helper.test_discord_channel_info(channel_id)
        print()
        
        helper.test_discord_get_messages(channel_id, 5)
        print()
        
        print("Enter a message to send (or 'skip'):")
        message = input("Message: ").strip()
        if message and message.lower() != 'skip':
            helper.test_discord_send_message(channel_id, message)
            print()
        
        # Test permission failure
        helper.test_permission_failure()
    
    print("\n" + "=" * 50)
    print("✅ Testing complete!")
    print(f"Admin key: {helper.admin_key}")
    print(f"Write key: {helper.write_key}")
    print(f"Read key: {helper.read_key}")
    print("\n📖 Check the manual_testing_guide.md for more detailed testing instructions")
    print("🌐 Visit http://localhost:8000/docs for interactive API documentation")

if __name__ == "__main__":
    main() 
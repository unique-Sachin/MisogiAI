# Manual Testing Guide for MCP Discord Server

## 1. Prerequisites

### PostgreSQL Setup
```bash
# 1. Install PostgreSQL (if not already installed)
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql postgresql-contrib
# Windows: Download from https://www.postgresql.org/download/

# 2. Start PostgreSQL service
# macOS: brew services start postgresql
# Ubuntu: sudo systemctl start postgresql
# Windows: Start PostgreSQL service

# 3. Run the setup script to create database and user
./setup_postgres.sh
```

### Environment Setup
```bash
# 1. Create .env file (already configured for PostgreSQL)
cp env.example .env
# Edit .env and add your real DISCORD_BOT_TOKEN if needed

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Discord Bot Setup
1. Go to https://discord.com/developers/applications
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token to your `.env` file as `DISCORD_BOT_TOKEN`
5. Invite the bot to your test server with appropriate permissions

## 2. Testing Flow

### Step 1: Health Check
```bash
curl -X GET "http://localhost:8000/health"
```
Expected: `{"status": "healthy"}`

### Step 2: Create Admin API Key
```bash
curl -X POST "http://localhost:8000/admin/api-keys" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: bootstrap-admin-key" \
  -d '{
    "name": "Test Admin Key",
    "role": "admin"
  }'
```
Expected: Returns API key with `secret` field - **SAVE THIS SECRET!**

### Step 3: Test API Key Listing
```bash
curl -X GET "http://localhost:8000/admin/api-keys" \
  -H "X-API-Key: YOUR_ADMIN_KEY_HERE"
```

### Step 4: Create Write/Read Keys
```bash
# Create Write key
curl -X POST "http://localhost:8000/admin/api-keys" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_ADMIN_KEY_HERE" \
  -d '{
    "name": "Write Key",
    "role": "write"
  }'

# Create Read key
curl -X POST "http://localhost:8000/admin/api-keys" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_ADMIN_KEY_HERE" \
  -d '{
    "name": "Read Key", 
    "role": "read"
  }'
```

## 3. Discord API Testing

### Get Channel Info (Read permission)
```bash
curl -X GET "http://localhost:8000/discord/channel_info?channel_id=YOUR_CHANNEL_ID" \
  -H "X-API-Key: YOUR_READ_OR_WRITE_KEY"
```

### Send Message (Write permission)
```bash
curl -X POST "http://localhost:8000/discord/send_message" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_WRITE_KEY" \
  -d '{
    "channel_id": "YOUR_CHANNEL_ID",
    "content": "Hello from MCP Server! 🚀"
  }'
```

### Get Messages (Read permission)
```bash
curl -X GET "http://localhost:8000/discord/messages?channel_id=YOUR_CHANNEL_ID&limit=10" \
  -H "X-API-Key: YOUR_READ_OR_WRITE_KEY"
```

### Search Messages (Read permission)
```bash
curl -X POST "http://localhost:8000/discord/search_messages" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_READ_OR_WRITE_KEY" \
  -d '{
    "channel_id": "YOUR_CHANNEL_ID",
    "query": "hello",
    "limit": 5
  }'
```

### Delete Message (Write permission)
```bash
curl -X DELETE "http://localhost:8000/discord/delete_message" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_WRITE_KEY" \
  -d '{
    "channel_id": "YOUR_CHANNEL_ID",
    "message_id": "MESSAGE_ID_TO_DELETE"
  }'
```

## 4. WebSocket Inspector Testing

### Connect to Inspector WebSocket
```bash
# Using websocat (install with: brew install websocat)
websocat "ws://localhost:8000/inspector/ws" -H "X-API-Key: YOUR_ADMIN_KEY"
```

Or use a WebSocket client like:
- Browser WebSocket extension
- Postman WebSocket feature
- wscat: `wscat -c "ws://localhost:8000/inspector/ws" -H "X-API-Key: YOUR_ADMIN_KEY"`

## 5. Permission Testing

### Test Read-only Key Restrictions
```bash
# This should FAIL with 403 Forbidden
curl -X POST "http://localhost:8000/discord/send_message" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_READ_ONLY_KEY" \
  -d '{
    "channel_id": "YOUR_CHANNEL_ID",
    "content": "This should fail"
  }'
```

### Test Admin-only Endpoints
```bash
# This should FAIL with 403 Forbidden using write/read keys
curl -X POST "http://localhost:8000/admin/api-keys" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_WRITE_KEY" \
  -d '{
    "name": "Should Fail",
    "role": "read"
  }'
```

## 6. Error Testing

### Invalid API Key
```bash
curl -X GET "http://localhost:8000/discord/messages?channel_id=123" \
  -H "X-API-Key: invalid-key"
```
Expected: 401 Unauthorized

### Invalid Channel ID
```bash
curl -X GET "http://localhost:8000/discord/channel_info?channel_id=invalid" \
  -H "X-API-Key: YOUR_READ_KEY"
```
Expected: 400 Bad Request or 404 Not Found

### Rate Limiting Test
```bash
# Run this command rapidly 15+ times
for i in {1..15}; do
  curl -X GET "http://localhost:8000/health" &
done
wait
```
Expected: Some requests should return 429 Too Many Requests

## 7. API Documentation

Visit: http://localhost:8000/docs for interactive Swagger UI
Visit: http://localhost:8000/redoc for ReDoc documentation

## 8. Monitoring & Logs

### Check Audit Logs
The server logs all requests. Watch the console output for audit entries.

### WebSocket Inspector
Connect to the WebSocket inspector to see real-time request logs:
```javascript
// Browser console
const ws = new WebSocket('ws://localhost:8000/inspector/ws');
ws.onopen = () => {
  ws.send(JSON.stringify({headers: {'X-API-Key': 'YOUR_ADMIN_KEY'}}));
};
ws.onmessage = (event) => {
  console.log('Audit log:', JSON.parse(event.data));
};
```

## 9. Common Issues & Solutions

### Discord Bot Token Issues
- Ensure bot has proper permissions in your Discord server
- Check that the token is valid and not expired
- Verify bot is added to the server where you're testing

### Database Issues
- The server uses SQLite by default for testing
- Check that the database file is writable
- Restart server if database connection issues occur

### Rate Limiting
- Discord has its own rate limits (separate from server rate limits)
- If you hit Discord rate limits, wait before retrying
- Server rate limits reset every minute

## 10. Success Criteria Checklist

- [ ] Health endpoint responds
- [ ] Admin API key creation works
- [ ] All Discord endpoints respond correctly
- [ ] Permission system blocks unauthorized access
- [ ] WebSocket inspector receives real-time logs
- [ ] Rate limiting activates under load
- [ ] Audit logs are generated for all requests
- [ ] API documentation is accessible 
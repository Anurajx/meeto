# Groq API Setup Guide

This project uses Groq API for fast, affordable LLM-based action item extraction from meeting transcripts.

## What is Groq?

Groq is an AI inference platform that provides:
- **Fast inference** - Sub-second response times
- **Affordable pricing** - Very cost-effective compared to alternatives
- **Open-source models** - Runs models like Llama, Mixtral, Gemma
- **Free tier** - Generous free usage for development

## Step-by-Step Setup

### 1. Create a Groq Account

1. Go to [console.groq.com](https://console.groq.com)
2. Click "Sign Up" or "Get Started"
3. Sign up with Google, GitHub, or email
4. Verify your email if required

### 2. Create an API Key

1. Once logged in, go to **API Keys** section (usually in the left sidebar or top menu)
2. Click **"Create API Key"** or **"New API Key"**
3. Give it a name (e.g., "Meeting Secretary")
4. Copy the API key immediately (you won't be able to see it again!)
5. Save it securely - you'll need it for your `.env` file

**Important:** The API key will only be shown once. If you lose it, create a new one.

### 3. Configure Your Backend

1. Open `backend/.env` file
2. Add your Groq API key:

```env
GROQ_API_KEY=gsk_your_actual_api_key_here
```

**Example:**
```env
GROQ_API_KEY=gsk_1234567890abcdefghijklmnopqrstuvwxyz
```

### 4. (Optional) Choose a Model

You can specify which Groq model to use in your `.env`:

```env
# Available Groq models:
LLM_MODEL=llama-3.1-70b-versatile      # Recommended: Best balance of speed and quality
LLM_MODEL=llama-3.1-8b-instant         # Fastest: Good for quick tasks
LLM_MODEL=mixtral-8x7b-32768           # High quality: Better reasoning
LLM_MODEL=gemma-7b-it                  # Compact: Efficient option
```

**Default:** `llama-3.1-70b-versatile` (recommended)

## Available Groq Models

### Recommended Models

1. **llama-3.1-70b-versatile** (Default)
   - Best balance of quality and speed
   - Great for action item extraction
   - Recommended for most use cases

2. **llama-3.1-8b-instant**
   - Fastest inference
   - Lower cost
   - Good for simple extractions

3. **mixtral-8x7b-32768**
   - High quality reasoning
   - Large context window (32K tokens)
   - Good for complex meeting transcripts

4. **gemma-7b-it**
   - Compact and efficient
   - Good for simple tasks
   - Lower resource usage

## Free Tier Limits

Groq free tier includes:
- **30 requests/minute**
- **14,400 requests/day**
- **Generous token limits**

**Note:** Free tier is usually sufficient for development and small-scale production use.

## Pricing (Paid Plans)

If you exceed free tier:
- **Pay-as-you-go** pricing
- Very affordable compared to alternatives
- Check [groq.com/pricing](https://groq.com/pricing) for current rates

## Testing Your Setup

1. Make sure your API key is set in `.env`
2. Start your backend server:
   ```bash
   cd backend
   python run.py
   ```
3. Upload a meeting audio file
4. Check if action items are extracted successfully

If you see errors:
- Verify API key is correct
- Check Groq dashboard for usage/errors
- Ensure you haven't exceeded rate limits

## Troubleshooting

### API Key Not Working

1. **Verify API key format:**
   - Should start with `gsk_`
   - Usually 40+ characters long
   - No spaces or extra characters

2. **Check if key is active:**
   - Go to Groq console → API Keys
   - Ensure key is enabled/active

3. **Create a new key** if needed:
   - Delete old key
   - Create new one
   - Update `.env` file

### Rate Limit Errors

If you see rate limit errors:
- **Free tier**: 30 requests/minute
- Wait a minute between requests
- Consider upgrading to paid plan for higher limits
- Or use local mode with Ollama (see ENABLE_LOCAL_MODE)

### Model Not Found

If you see model errors:
- Check model name spelling
- Ensure model is available in your region
- Try default model: `llama-3.1-70b-versatile`
- Check Groq documentation for available models

### Connection Errors

1. **Check internet connection**
2. **Verify Groq service status:**
   - Check [status.groq.com](https://status.groq.com) if available
   - Check Groq Discord/Twitter for outages

3. **Check firewall/proxy settings**
   - Ensure port 443 (HTTPS) is open
   - Groq API uses HTTPS only

## Alternative: Using OpenAI (Backward Compatibility)

The code still supports OpenAI API as a fallback. To use OpenAI instead:

```env
# Comment out GROQ_API_KEY
# GROQ_API_KEY=...

# Use OpenAI instead
OPENAI_API_KEY=sk-your-openai-key-here
LLM_MODEL=gpt-4o-mini
```

**Note:** OpenAI is more expensive than Groq. Groq is recommended for cost-effectiveness.

## Alternative: Local Mode (No API Calls)

For complete privacy, use local Ollama:

```env
ENABLE_LOCAL_MODE=true
USE_LOCAL_WHISPER=true
```

Then install Ollama locally:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download model
ollama pull llama3.2
```

## Monitoring Usage

1. Go to Groq Console dashboard
2. Check **Usage** or **Analytics** section
3. Monitor:
   - API requests
   - Tokens used
   - Rate limits
   - Costs (if on paid plan)

## Best Practices

1. **Keep API keys secret:**
   - Never commit to git
   - Use `.env` file (already in `.gitignore`)
   - Rotate keys periodically

2. **Monitor usage:**
   - Set up alerts if approaching limits
   - Track costs if on paid plan

3. **Use appropriate models:**
   - Use faster models for simple tasks
   - Use better models for complex extraction

4. **Handle errors gracefully:**
   - Code includes fallback to regex extraction
   - Always test with sample meetings first

## Getting Help

- **Groq Documentation**: [groq.com/docs](https://groq.com/docs)
- **Groq Discord**: Community support
- **GitHub Issues**: Report bugs
- **Console Dashboard**: [console.groq.com](https://console.groq.com)

## Next Steps

After setting up Groq:

1. ✅ Add `GROQ_API_KEY` to `backend/.env`
2. ✅ (Optional) Set `LLM_MODEL` to your preferred model
3. ✅ Start backend server
4. ✅ Upload a test meeting to verify extraction works
5. ✅ Check Groq dashboard to see API usage

Your Groq integration is ready! 🚀


# ANVIKSHAKA-X Deployment Guide

Complete guide for deploying ANVIKSHAKA-X in different environments with hybrid AI support.

## Table of Contents

1. [AI Provider Overview](#ai-provider-overview)
2. [Vercel Deployment](#vercel-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Local Development](#local-development)
5. [Environment Variables](#environment-variables)
6. [Troubleshooting](#troubleshooting)

---

## AI Provider Overview

ANVIKSHAKA-X supports three AI modes:

| Provider | Use Case | Requirements |
|----------|----------|--------------|
| **Gemini** | Production, online deployment | Google Gemini API key |
| **Ollama** | Local, offline, air-gapped | Ollama server running locally |
| **Rule-based** | Fallback, no AI needed | None (always available) |

### Selection Logic

Set `AI_PROVIDER` environment variable:

- **`auto`** (recommended): Automatically selects best available provider
  1. Gemini if `GEMINI_API_KEY` is set
  2. Ollama if server is running
  3. Rule-based fallback

- **`gemini`**: Force Gemini (fails gracefully to rule-based if unavailable)
- **`ollama`**: Force Ollama (fails gracefully to rule-based if unavailable)
- **`rule-based`**: Disable AI completely

---

## Vercel Deployment

### Prerequisites

- Vercel account
- Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- GitHub repository

### Step 1: Prepare Repository

Ensure these files exist:
- `vercel.json` (already configured)
- `frontend/.env.production` (already configured)
- `.env.example` (template for environment variables)

### Step 2: Deploy via Vercel Dashboard

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure project:
   - Framework Preset: **Other**
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `frontend/dist`

5. Add Environment Variables:
   ```
   AI_PROVIDER=gemini
   GEMINI_API_KEY=your_actual_api_key_here
   GEMINI_MODEL=gemini-1.5-flash
   DATABASE_URL=your_postgres_url (optional, for production DB)
   ```

6. Click "Deploy"

### Step 3: Deploy via CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod

# Set environment variables
vercel env add AI_PROVIDER production
# Enter: gemini

vercel env add GEMINI_API_KEY production
# Enter: your_api_key_here

vercel env add GEMINI_MODEL production
# Enter: gemini-1.5-flash
```

### Post-Deployment

1. Test the deployment:
   ```bash
   curl https://your-deployment-url.vercel.app/api/health
   ```

2. Expected response:
   ```json
   {
     "status": "healthy",
     "timestamp": "2024-...",
     "ai_provider": "gemini",
     "ai_available": true
   }
   ```

3. Visit the frontend at `https://your-deployment-url.vercel.app`

### Vercel-Specific Notes

- **Serverless functions**: Backend runs as serverless functions (cold starts may occur)
- **Database**: Switch to PostgreSQL for production (Vercel Postgres, Supabase, or external)
- **File storage**: SQLite doesn't persist; use PostgreSQL or external DB
- **Logs**: View in Vercel dashboard under "Logs" tab
- **Rate limits**: Monitor Gemini API usage in Google Cloud Console

---

## Docker Deployment

### Option A: Docker with Gemini (Online)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .
COPY ml/ ../ml/

# Environment
ENV AI_PROVIDER=gemini
ENV GEMINI_MODEL=gemini-1.5-flash

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t anvikshaka-backend .
docker run -d -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  anvikshaka-backend
```

### Option B: Docker Compose with Ollama (Offline)

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - AI_PROVIDER=ollama
      - OLLAMA_BASE_URL=http://ollama:11434
      - OLLAMA_MODEL=llama3
      - DATABASE_URL=sqlite:///./anvikshaka.db
    depends_on:
      - ollama
    volumes:
      - ./backend:/app
      - ./ml:/ml

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    command: serve

  frontend:
    image: node:18-alpine
    working_dir: /app
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
    command: sh -c "npm install && npm run dev -- --host"
    environment:
      - VITE_API_URL=http://localhost:8000/api

volumes:
  ollama_data:
```

Run:
```bash
docker-compose up -d

# Pull Ollama model (first time only)
docker exec -it anvikshaka-ollama-1 ollama pull llama3
```

### Production Docker with PostgreSQL

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AI_PROVIDER=gemini
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DATABASE_URL=postgresql://user:pass@db:5432/anvikshaka
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=anvikshaka
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=anvikshaka
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html

volumes:
  postgres_data:
```

---

## Local Development

### With Gemini (Online)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment
export AI_PROVIDER=gemini
export GEMINI_API_KEY=your_key

# Run
python main.py
```

### With Ollama (Offline)

```bash
# Install Ollama
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh
# Windows: Download from ollama.ai

# Pull model
ollama pull llama3

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment
export AI_PROVIDER=ollama

# Run
python main.py
```

### Auto Mode (Recommended for Development)

```bash
export AI_PROVIDER=auto
export GEMINI_API_KEY=your_key  # Optional, will use if available

# Will automatically choose:
# 1. Gemini if key is set
# 2. Ollama if running
# 3. Rule-based if neither
python main.py
```

---

## Environment Variables

### Backend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AI_PROVIDER` | No | `auto` | AI provider selection: `gemini`, `ollama`, `auto`, `rule-based` |
| `GEMINI_API_KEY` | For Gemini | - | Google Gemini API key |
| `GEMINI_MODEL` | No | `gemini-1.5-flash` | Gemini model name |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | No | `llama3` | Ollama model name |
| `DATABASE_URL` | No | `sqlite:///./anvikshaka.db` | Database connection URL |
| `API_HOST` | No | `0.0.0.0` | API server host |
| `API_PORT` | No | `8000` | API server port |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### Frontend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | No | `http://localhost:8000/api` | Backend API URL |

### Example .env Files

**Backend `.env` (Production with Gemini):**
```bash
AI_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...your_key
GEMINI_MODEL=gemini-1.5-flash
DATABASE_URL=postgresql://user:pass@host:5432/anvikshaka
LOG_LEVEL=INFO
```

**Backend `.env` (Local with Ollama):**
```bash
AI_PROVIDER=ollama
OLLAMA_MODEL=llama3
DATABASE_URL=sqlite:///./anvikshaka.db
LOG_LEVEL=DEBUG
```

**Frontend `.env.production`:**
```bash
VITE_API_URL=/api
```

---

## Troubleshooting

### Issue: "AI provider not available"

**Symptoms**: Health endpoint shows `"ai_provider": "rule-based"`

**Solutions**:
1. **For Gemini**: Verify `GEMINI_API_KEY` is set correctly
   ```bash
   curl -H "Authorization: Bearer $GEMINI_API_KEY" \
     https://generativelanguage.googleapis.com/v1/models
   ```

2. **For Ollama**: Check if Ollama is running
   ```bash
   curl http://localhost:11434/api/tags
   ```

3. Check logs:
   ```bash
   # Look for AI provider initialization messages
   grep "AI provider" backend.log
   ```

### Issue: Gemini API rate limit exceeded

**Symptoms**: 429 errors in logs, AI calls failing

**Solutions**:
1. Check quota in Google Cloud Console
2. Reduce request frequency
3. Implement caching (future enhancement)
4. Switch to Ollama for development

### Issue: Ollama cold start slow

**Symptoms**: First AI call takes 5-10 seconds

**Solutions**:
1. Keep Ollama running with `keep_alive` option
2. Warm-up happens automatically on startup
3. Use smaller models for faster response

### Issue: Vercel serverless timeout

**Symptoms**: 504 Gateway Timeout on long-running requests

**Solutions**:
1. Upgrade to Pro plan (60s timeout vs 10s)
2. Optimize agent pipeline for faster execution
3. Consider dedicated hosting for backend

### Issue: Database not persisting on Vercel

**Symptoms**: Data lost between deployments

**Solutions**:
1. Switch to PostgreSQL (Vercel Postgres, Supabase)
2. SQLite doesn't work in serverless environments
3. Use environment variable `DATABASE_URL` for external DB

---

## Security Checklist

- [ ] Never commit `.env` files with real credentials
- [ ] Use Vercel environment variables for secrets
- [ ] Rotate API keys regularly
- [ ] Enable CORS only for your frontend domain in production
- [ ] Use HTTPS in production
- [ ] Monitor API usage and set billing alerts
- [ ] Implement rate limiting (future enhancement)
- [ ] Use least-privilege database credentials

---

## Performance Optimization

### Gemini
- Use `gemini-1.5-flash` for speed (default)
- Use `gemini-1.5-pro` for better quality (slower, more expensive)
- Set appropriate `max_tokens` to reduce latency

### Ollama
- Use quantized models (Q4, Q5) for faster inference
- Keep model in memory with `keep_alive` option
- Run on GPU for 10-50x speedup

### Database
- Switch to PostgreSQL for production
- Add indexes on frequently queried columns
- Use connection pooling

---

## Next Steps

After deployment:
1. Test all endpoints: `/api/health`, `/api/mission`, `/api/chat`
2. Verify AI provider is active in health check
3. Monitor logs for errors
4. Set up uptime monitoring (UptimeRobot, Pingdom)
5. Configure alerts for API key usage limits
6. Plan database migration to PostgreSQL if using Vercel

---

**Questions?** Open an issue on [GitHub](https://github.com/SaiVarunPappla/ANVIKSHAKA-X/issues)

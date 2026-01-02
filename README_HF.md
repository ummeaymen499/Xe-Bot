---
title: Xe-Bot
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_file: Dockerfile.hf
app_port: 7860
pinned: false
license: mit
---

# Xe-Bot: Research Paper Animation Generator

Transform academic papers into visual explanations with AI-powered Manim animations.

## Features
- 🔍 Search arXiv papers
- 📄 Extract and segment introductions
- 🎬 Generate Manim animations
- 🎥 Video gallery

## API Endpoints
- `GET /` - API info
- `GET /docs` - Swagger documentation
- `GET /search/arxiv?query=...` - Search papers
- `POST /api/generate` - Generate animations
- `GET /api/jobs/{id}` - Check job status
- `GET /videos` - List videos
- `GET /download/{path}` - Download video files

## Environment Variables (Set in HF Space Secrets)
| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | ✅ | Your OpenRouter API key |
| `NEON_DATABASE_URL` | ✅ | Neon PostgreSQL connection string |
| `VIDEO_BASE_URL` | ❌ | Auto-detected (your-space.hf.space) |
| `CORS_ORIGINS` | ❌ | Frontend URLs (comma-separated) |

## Frontend Setup
Set `VITE_API_URL` in your frontend to: `https://YOUR-USERNAME-xe-bot.hf.space`

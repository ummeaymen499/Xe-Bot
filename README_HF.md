---
title: Xe-Bot
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
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
- `GET /videos` - List videos

## Environment Variables Required
- `OPENROUTER_API_KEY` - Your OpenRouter API key
- `DATABASE_URL` - Neon PostgreSQL connection string

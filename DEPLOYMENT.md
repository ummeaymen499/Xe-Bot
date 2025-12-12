# 🚀 Xe-Bot Free Deployment Guide

This guide covers deploying Xe-Bot for **free** using:
- **Frontend**: Vercel (React + Vite)
- **Backend**: Render (FastAPI + Manim)
- **Database**: Neon PostgreSQL (you already have this!)

---

## 📋 Prerequisites

- GitHub account with this repo pushed
- Neon PostgreSQL database URL (from `.env`)
- OpenRouter API key

---

## Step 1: Deploy Backend to Render

### 1.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub

### 1.2 Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repo: `ummeaymen499/Xe-Bot`
3. Configure:
   - **Name**: `xe-bot-api`
   - **Region**: Oregon (or closest to you)
   - **Branch**: `main`
   - **Runtime**: `Docker`
   - **Dockerfile Path**: `./Dockerfile.render`
   - **Plan**: `Free`

### 1.3 Add Environment Variables
In Render dashboard, add these environment variables:

| Key | Value |
|-----|-------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `DATABASE_URL` | Your Neon PostgreSQL URL |
| `NEON_DATABASE_URL` | Your Neon PostgreSQL URL |
| `VIDEO_BASE_URL` | `https://xe-bot-api.onrender.com` (your Render URL) |

### 1.4 Deploy
Click **"Create Web Service"** and wait for deployment (~5-10 min first time due to TeX dependencies).

**Your backend URL**: `https://xe-bot-api.onrender.com`

---

## Step 2: Deploy Frontend to Vercel

### 2.1 Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub

### 2.2 Import Project
1. Click **"Add New..."** → **"Project"**
2. Import your GitHub repo: `ummeaymen499/Xe-Bot`
3. Configure:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend` ← IMPORTANT!
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 2.3 Add Environment Variables
Click **"Environment Variables"** and add:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://xe-bot-api.onrender.com` (your Render URL) |

### 2.4 Deploy
Click **"Deploy"** and wait (~1-2 min).

**Your frontend URL**: `https://xe-bot.vercel.app` (or custom)

---

## Step 3: Update CORS (Important!)

After both are deployed, update the backend CORS settings:

In `server.py`, change:
```python
allow_origins=["*"]
```
To:
```python
allow_origins=[
    "https://xe-bot.vercel.app",  # Your Vercel URL
    "https://your-custom-domain.com",
    "http://localhost:3000",  # For local dev
]
```

Then redeploy the backend.

---

## 🔧 Troubleshooting

### Backend takes long to respond
- **Cause**: Render free tier sleeps after 15 min of inactivity
- **Fix**: First request takes ~30s to wake up (normal)

### Videos not loading
- **Check**: `VIDEO_BASE_URL` must match your Render URL exactly
- **Check**: CORS is configured correctly

### Database connection errors
- **Verify**: `DATABASE_URL` includes `?sslmode=require`
- **Format**: `postgresql://user:pass@host/db?sslmode=require`

### Animation generation fails
- **Check**: OpenRouter API key is valid
- **Check**: Manim dependencies loaded (check Render logs)

---

## 📊 Free Tier Limits

| Service | Limits | Notes |
|---------|--------|-------|
| **Vercel** | 100GB bandwidth/mo | Unlimited deploys |
| **Render** | 750 hours/mo | Sleeps after 15min inactive |
| **Neon** | 0.5GB storage | 191 compute hours/mo |

---

## 🔄 Auto-Deploy Setup

Both Vercel and Render auto-deploy when you push to `main` branch!

```bash
git add .
git commit -m "Update feature"
git push origin main
# ✅ Both frontend and backend redeploy automatically
```

---

## 🌐 Custom Domain (Optional)

### Vercel
1. Go to Project Settings → Domains
2. Add your domain
3. Update DNS records as shown

### Render
1. Go to Service Settings → Custom Domains
2. Add your domain (requires paid plan for custom domains)

---

## ✅ Deployment Checklist

- [ ] Backend deployed to Render
- [ ] Frontend deployed to Vercel
- [ ] Environment variables set on both platforms
- [ ] CORS updated for production domain
- [ ] Test: Can search papers
- [ ] Test: Can generate animations
- [ ] Test: Can view videos

---

## 🆘 Need Help?

- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Neon Docs: https://neon.tech/docs

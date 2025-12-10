"""
Video Server API
Serves generated animations via HTTP URLs
"""
import os
import uuid
import asyncio
import hashlib
import secrets
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends, Header
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn

from src.config import config
from src.database import db_manager, ResearchPaper, Animation, ProcessingStatus
from src.agents import orchestrator

# Initialize FastAPI app
app = FastAPI(
    title="Xe-Bot Animation API",
    description="Research Paper Animation Generator - Public API for generating Manim animations from arXiv papers",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security
security = HTTPBearer(auto_error=False)

# API Keys storage (in production, use database)
API_KEYS: Dict[str, Dict[str, Any]] = {
    # Default demo key - replace with database in production
    "demo-key-12345": {"name": "Demo User", "tier": "free", "requests_today": 0},
}

# Job storage (in production, use Redis or database)
JOBS: Dict[str, Dict[str, Any]] = {}

# Add CORS middleware for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
VIDEO_BASE_URL = os.getenv("VIDEO_BASE_URL", "http://localhost:8000")
VIDEOS_DIR = Path("output/media/videos")
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
ANIMATIONS_DIR = Path("output/animations/videos")
ANIMATIONS_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files for video serving (use /media to avoid conflict with /videos API)
try:
    app.mount("/media/videos", StaticFiles(directory=str(VIDEOS_DIR)), name="videos_static")
except Exception as e:
    print(f"Warning: Could not mount videos directory: {e}")

# Mount animations directory for serving original animation files
try:
    app.mount("/animations/videos", StaticFiles(directory=str(ANIMATIONS_DIR)), name="animations_static")
except Exception as e:
    print(f"Warning: Could not mount animations directory: {e}")


# ==================== API KEY AUTHENTICATION ====================

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[Dict]:
    """Verify API key and return user info"""
    if credentials is None:
        return None  # Allow unauthenticated for some endpoints
    
    api_key = credentials.credentials
    if api_key in API_KEYS:
        return API_KEYS[api_key]
    
    # Check environment variable for master key
    master_key = os.getenv("XE_BOT_API_KEY")
    if master_key and api_key == master_key:
        return {"name": "Master", "tier": "pro", "requests_today": 0}
    
    return None


async def require_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Require valid API key"""
    user = await verify_api_key(credentials)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Get one at /api/keys/create"
        )
    return user


# ==================== MODELS ====================

class PaperRequest(BaseModel):
    arxiv_id: str
    render: bool = True
    quality: str = "medium"  # low, medium, high


class AnimationResponse(BaseModel):
    id: int
    paper_id: int
    animation_type: str
    video_url: Optional[str]
    status: str
    created_at: datetime


class PaperResponse(BaseModel):
    id: int
    arxiv_id: str
    title: str
    authors: list
    status: str
    animations: list[AnimationResponse]


class VideoURLResponse(BaseModel):
    video_id: str
    video_url: str
    download_url: str
    file_path: str
    file_size: int
    duration_seconds: int


# ==================== VIDEO URL MANAGEMENT ====================

class VideoURLManager:
    """Manages video URLs and storage"""
    
    def __init__(self, base_url: str = VIDEO_BASE_URL):
        self.base_url = base_url
        self.videos_dir = VIDEOS_DIR
    
    def generate_video_url(self, file_path: str) -> dict:
        """
        Generate accessible URL for a video file
        
        Args:
            file_path: Local path to video file
        
        Returns:
            Dict with video_url, download_url, and metadata
        """
        path = Path(file_path)
        
        if not path.exists():
            return {"error": "Video file not found", "file_path": file_path}
        
        # Check if file is in animations directory (preferred - serve directly)
        try:
            relative_path = path.relative_to(ANIMATIONS_DIR)
            url_path = str(relative_path).replace("\\", "/")
            video_url = f"{self.base_url}/animations/videos/{url_path}"
            download_url = f"{self.base_url}/download/animations/{url_path}"
        except ValueError:
            # Check if file is in media/videos directory
            try:
                relative_path = path.relative_to(self.videos_dir)
                url_path = str(relative_path).replace("\\", "/")
                video_url = f"{self.base_url}/media/videos/{url_path}"
                download_url = f"{self.base_url}/download/{url_path}"
            except ValueError:
                # File is outside both directories - serve from animations path
                # Calculate relative path from output directory
                try:
                    output_dir = Path("output")
                    relative_path = path.relative_to(output_dir)
                    url_path = str(relative_path).replace("\\", "/")
                    video_url = f"{self.base_url}/animations/videos/{url_path}"
                    download_url = f"{self.base_url}/download/animations/{url_path}"
                except ValueError:
                    return {"error": "Video file outside serving directories", "file_path": file_path}
        
        # Get file metadata
        file_size = path.stat().st_size
        
        return {
            "video_id": path.stem,
            "video_url": video_url,
            "download_url": download_url,
            "file_path": str(path),
            "file_size": file_size,
            "relative_path": url_path
        }
    
    def get_all_videos(self) -> list:
        """Get all available videos with URLs"""
        videos = []
        
        for mp4_file in self.videos_dir.rglob("*.mp4"):
            # Skip partial movie files
            if "partial_movie_files" in str(mp4_file):
                continue
            
            video_info = self.generate_video_url(str(mp4_file))
            if "error" not in video_info:
                videos.append(video_info)
        
        return videos
    
    def save_video_url_to_db(self, animation_id: int, video_url: str):
        """Save video URL to database"""
        try:
            session = db_manager.get_session()
            animation = session.query(Animation).filter_by(id=animation_id).first()
            if animation:
                animation.file_path = video_url
                animation.status = ProcessingStatus.COMPLETED
                session.commit()
            session.close()
        except Exception as e:
            print(f"Error saving video URL: {e}")


# Global URL manager
url_manager = VideoURLManager()


# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Xe-Bot API",
        "version": "1.0.0",
        "description": "Research Paper Animation Generator",
        "endpoints": {
            "POST /process": "Process an arXiv paper",
            "GET /search/arxiv": "Search arXiv papers",
            "GET /search/domain": "Search papers by domain",
            "GET /papers": "List all processed papers",
            "GET /papers/{arxiv_id}": "Get paper details",
            "GET /videos": "List all generated videos",
            "GET /videos/{video_id}": "Get video URL",
            "GET /download/{path}": "Download video file"
        }
    }


@app.get("/search/arxiv")
async def search_arxiv(query: str, max_results: int = 10):
    """Search arXiv for papers matching a query"""
    import arxiv
    
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = []
        for result in client.results(search):
            papers.append({
                "arxiv_id": result.entry_id.split("/")[-1],
                "title": result.title,
                "authors": [a.name for a in result.authors],
                "summary": result.summary[:500] + "..." if len(result.summary) > 500 else result.summary,
                "published": result.published.isoformat() if result.published else None,
                "pdf_url": result.pdf_url
            })
        
        return {"papers": papers, "count": len(papers), "query": query}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/search/domain")
async def search_by_domain(domain: str, max_results: int = 10):
    """Search arXiv for papers in a specific domain/topic"""
    import arxiv
    
    try:
        # Create a search query for the domain
        search_query = f"all:{domain}"
        
        client = arxiv.Client()
        search = arxiv.Search(
            query=search_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = []
        for result in client.results(search):
            papers.append({
                "arxiv_id": result.entry_id.split("/")[-1],
                "title": result.title,
                "authors": [a.name for a in result.authors],
                "summary": result.summary[:500] + "..." if len(result.summary) > 500 else result.summary,
                "published": result.published.isoformat() if result.published else None,
                "pdf_url": result.pdf_url
            })
        
        return {"papers": papers, "count": len(papers), "domain": domain}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Domain search failed: {str(e)}")


@app.post("/process", response_model=dict)
async def process_paper(request: PaperRequest, background_tasks: BackgroundTasks):
    """
    Process a research paper and generate animations
    
    This endpoint:
    1. Fetches the paper from arXiv
    2. Extracts the introduction
    3. Segments it into topics
    4. Generates animations
    5. Returns URLs to access the videos
    """
    try:
        # Process the paper
        results = await orchestrator.process_paper(
            arxiv_id=request.arxiv_id,
            render_animations=request.render,
            save_to_db=True
        )
        
        # Generate URLs for any rendered videos
        video_urls = []
        for anim in results.get("animations", []):
            if anim.get("file_path"):
                url_info = url_manager.generate_video_url(anim["file_path"])
                video_urls.append(url_info)
        
        return {
            "status": results["status"],
            "paper": results.get("paper", {}),
            "segments": results.get("segments", []),
            "videos": video_urls,
            "message": f"Processed paper with {len(video_urls)} videos generated"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/papers")
async def list_papers():
    """List all processed papers"""
    try:
        session = db_manager.get_session()
        papers = session.query(ResearchPaper).all()
        
        result = []
        for paper in papers:
            result.append({
                "id": paper.id,
                "arxiv_id": paper.arxiv_id,
                "title": paper.title,
                "authors": paper.authors,
                "status": paper.status.value if paper.status else "unknown",
                "created_at": paper.created_at.isoformat() if paper.created_at else None
            })
        
        session.close()
        return {"papers": result, "count": len(result)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/papers/{arxiv_id}")
async def get_paper(arxiv_id: str):
    """Get details for a specific paper including video URLs"""
    try:
        session = db_manager.get_session()
        paper = session.query(ResearchPaper).filter_by(arxiv_id=arxiv_id).first()
        
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Get animations with URLs
        animations = []
        for anim in paper.animations:
            anim_data = {
                "id": anim.id,
                "type": anim.animation_type,
                "status": anim.status.value if anim.status else "unknown",
                "created_at": anim.created_at.isoformat() if anim.created_at else None
            }
            
            if anim.file_path:
                url_info = url_manager.generate_video_url(anim.file_path)
                anim_data["video_url"] = url_info.get("video_url")
                anim_data["download_url"] = url_info.get("download_url")
            
            animations.append(anim_data)
        
        # Get segments
        segments = []
        for seg in paper.segments:
            segments.append({
                "order": seg.segment_order,
                "topic": seg.topic,
                "category": seg.topic_category,
                "key_concepts": seg.key_concepts
            })
        
        session.close()
        
        return {
            "id": paper.id,
            "arxiv_id": paper.arxiv_id,
            "title": paper.title,
            "authors": paper.authors,
            "abstract": paper.abstract,
            "status": paper.status.value if paper.status else "unknown",
            "segments": segments,
            "animations": animations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/videos")
async def list_videos():
    """List all available videos with their URLs"""
    videos = url_manager.get_all_videos()
    return {
        "videos": videos,
        "count": len(videos),
        "base_url": VIDEO_BASE_URL
    }


@app.get("/videos/enriched")
async def list_videos_enriched():
    """List all videos with paper information from database"""
    try:
        # Get videos from filesystem
        fs_videos = url_manager.get_all_videos()
        
        # Get videos from database
        session = db_manager.get_session()
        db_animations = session.query(Animation).all()
        
        # Build enriched video list
        enriched_videos = []
        
        # First add database videos
        for anim in db_animations:
            video_info = {
                "video_id": f"db_{anim.id}",
                "animation_type": anim.animation_type,
                "status": anim.status.value if anim.status else "unknown",
                "created_at": anim.created_at.isoformat() if anim.created_at else None,
                "duration_seconds": anim.duration_seconds,
                "file_size": anim.file_size_bytes,
            }
            
            # Get paper info
            if anim.paper:
                video_info["paper_id"] = anim.paper.id
                video_info["paper_title"] = anim.paper.title
                video_info["paper_arxiv_id"] = anim.paper.arxiv_id
            
            # Get URLs
            if anim.file_path and Path(anim.file_path).exists():
                url_info = url_manager.generate_video_url(anim.file_path)
                video_info["video_url"] = url_info.get("video_url")
                video_info["download_url"] = url_info.get("download_url")
                video_info["file_path"] = anim.file_path
            elif anim.video_url:
                video_info["video_url"] = anim.video_url
                video_info["download_url"] = anim.download_url
            
            if video_info.get("video_url"):
                enriched_videos.append(video_info)
        
        # Add filesystem videos not in database
        db_paths = {a.file_path for a in db_animations if a.file_path}
        for fs_video in fs_videos:
            if fs_video.get("file_path") not in db_paths:
                fs_video["source"] = "filesystem"
                # Try to extract info from path
                path = fs_video.get("file_path", "")
                if "segment_" in path:
                    import re
                    match = re.search(r'segment_(\d+)', path)
                    fs_video["animation_type"] = f"Segment {match.group(1)}" if match else "Segment"
                elif "full_introduction" in path:
                    fs_video["animation_type"] = "Full Introduction"
                else:
                    fs_video["animation_type"] = "Animation"
                enriched_videos.append(fs_video)
        
        session.close()
        
        return {
            "videos": enriched_videos,
            "count": len(enriched_videos),
            "base_url": VIDEO_BASE_URL
        }
        
    except Exception as e:
        # Fallback to filesystem-only
        videos = url_manager.get_all_videos()
        return {
            "videos": videos,
            "count": len(videos),
            "base_url": VIDEO_BASE_URL,
            "warning": f"Database unavailable: {str(e)}"
        }


@app.get("/videos/{video_id}")
async def get_video_url(video_id: str):
    """Get URL for a specific video"""
    videos = url_manager.get_all_videos()
    
    for video in videos:
        if video_id in video.get("video_id", "") or video_id in video.get("relative_path", ""):
            return video
    
    raise HTTPException(status_code=404, detail="Video not found")


@app.get("/download/{path:path}")
async def download_video(path: str):
    """Download a video file"""
    file_path = VIDEOS_DIR / path
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        path=str(file_path),
        media_type="video/mp4",
        filename=file_path.name
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check database connection
    db_status = "healthy"
    try:
        session = db_manager.get_session()
        session.execute("SELECT 1")
        session.close()
    except Exception as e:
        db_status = f"unhealthy: {str(e)[:50]}"
    
    # Check FFmpeg
    import shutil
    ffmpeg_status = "installed" if shutil.which("ffmpeg") else "not found"
    
    # Check Manim
    manim_status = "installed" if shutil.which("manim") else "not found"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "videos_available": len(url_manager.get_all_videos()),
        "checks": {
            "database": db_status,
            "ffmpeg": ffmpeg_status,
            "manim": manim_status
        }
    }


# ==================== PUBLIC API ENDPOINTS ====================

class GenerateRequest(BaseModel):
    arxiv_id: str
    quality: str = "low"  # low, medium, high
    render: bool = True
    webhook_url: Optional[str] = None


class GenerateCodeRequest(BaseModel):
    topic: str
    key_concepts: list[str] = []
    style: str = "explanatory"


class APIKeyCreate(BaseModel):
    name: str
    email: Optional[str] = None


@app.post("/api/keys/create")
async def create_api_key(data: APIKeyCreate):
    """Create a new API key (free tier)"""
    # Generate secure API key
    api_key = f"xb_{secrets.token_urlsafe(24)}"
    
    API_KEYS[api_key] = {
        "name": data.name,
        "email": data.email,
        "tier": "free",
        "requests_today": 0,
        "created_at": datetime.utcnow().isoformat()
    }
    
    return {
        "api_key": api_key,
        "name": data.name,
        "tier": "free",
        "rate_limit": "10 requests/day",
        "message": "Save this key - it won't be shown again!"
    }


@app.get("/api/search")
async def api_search(
    query: str,
    max_results: int = 5,
    user: Dict = Depends(verify_api_key)
):
    """Search arXiv papers - Public API"""
    import arxiv
    
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=min(max_results, 20),
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = []
        for paper in client.results(search):
            papers.append({
                "arxiv_id": paper.entry_id.split("/")[-1],
                "title": paper.title,
                "authors": [a.name for a in paper.authors[:5]],
                "summary": paper.summary[:500] + "..." if len(paper.summary) > 500 else paper.summary,
                "published": paper.published.strftime("%Y-%m-%d") if paper.published else None,
                "pdf_url": paper.pdf_url
            })
        
        return {"papers": papers, "count": len(papers)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate")
async def api_generate(
    data: GenerateRequest,
    background_tasks: BackgroundTasks,
    user: Dict = Depends(require_api_key)
):
    """Generate animation - Returns job ID for async processing"""
    
    # Create job
    job_id = str(uuid.uuid4())[:12]
    
    JOBS[job_id] = {
        "status": "queued",
        "arxiv_id": data.arxiv_id,
        "quality": data.quality,
        "created_at": datetime.utcnow().isoformat(),
        "user": user.get("name"),
        "videos": [],
        "error": None
    }
    
    # Process in background
    background_tasks.add_task(
        process_animation_job,
        job_id,
        data.arxiv_id,
        data.quality,
        data.render,
        data.webhook_url
    )
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Animation job queued. Check status at /api/jobs/{job_id}",
        "estimated_time": "5-15 minutes depending on paper length"
    }


async def process_animation_job(
    job_id: str,
    arxiv_id: str,
    quality: str,
    render: bool,
    webhook_url: Optional[str]
):
    """Background task to process animation"""
    try:
        JOBS[job_id]["status"] = "processing"
        
        # Run the animation pipeline
        workflow = orchestrator.WorkflowOrchestrator()
        result = await workflow.process_paper(
            arxiv_id=arxiv_id,
            render_animations=render,
            save_to_db=True
        )
        
        # Collect video URLs
        videos = []
        for anim in result.get("animations", []):
            if anim.get("file_path"):
                video_info = url_manager.generate_video_url(anim["file_path"])
                videos.append({
                    "type": anim.get("type", "segment"),
                    "topic": anim.get("topic"),
                    "video_url": video_info.get("video_url"),
                    "download_url": video_info.get("download_url")
                })
                # Persist generated URLs back to the database (if animation record exists)
                try:
                    db_sess = db_manager.get_session()
                    try:
                        # Match by file_path stored in DB
                        anim_rec = db_sess.query(Animation).filter(Animation.file_path == anim.get("file_path")).first()
                        if anim_rec:
                            anim_rec.video_url = video_info.get("video_url")
                            anim_rec.download_url = video_info.get("download_url")
                            # Update file size if available
                            try:
                                anim_rec.file_size_bytes = int(video_info.get("file_size", anim_rec.file_size_bytes or 0))
                            except Exception:
                                pass
                            db_sess.commit()
                    finally:
                        db_sess.close()
                except Exception as _e:
                    # Non-fatal: log and continue
                    print(f"Warning: could not persist video URL to DB: {_e}")
        
        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["videos"] = videos
        JOBS[job_id]["paper"] = result.get("paper")
        JOBS[job_id]["segments_count"] = len(result.get("segments", []))
        JOBS[job_id]["completed_at"] = datetime.utcnow().isoformat()
        
        # Send webhook if provided
        if webhook_url:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(webhook_url, json={
                    "event": "job.completed",
                    "job_id": job_id,
                    "data": JOBS[job_id]
                })
                
    except Exception as e:
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)
        
        if webhook_url:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(webhook_url, json={
                    "event": "job.failed",
                    "job_id": job_id,
                    "error": str(e)
                })


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str, user: Dict = Depends(verify_api_key)):
    """Get job status and results"""
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JOBS[job_id]


@app.get("/api/jobs")
async def list_jobs(user: Dict = Depends(require_api_key)):
    """List all jobs for the authenticated user"""
    user_jobs = {
        k: v for k, v in JOBS.items() 
        if v.get("user") == user.get("name")
    }
    return {"jobs": user_jobs, "count": len(user_jobs)}


@app.post("/api/generate-code")
async def api_generate_code(
    data: GenerateCodeRequest,
    user: Dict = Depends(require_api_key)
):
    """Generate Manim code without rendering"""
    from src.llm.openrouter_client import openrouter_client
    
    try:
        segment = {
            "topic": data.topic,
            "topic_category": "concept",
            "key_concepts": data.key_concepts,
            "content": data.topic
        }
        
        code = await openrouter_client.generate_animation_code(
            segment,
            animation_style=data.style
        )
        
        return {
            "topic": data.topic,
            "manim_code": code,
            "usage": "Save as .py file and run: manim -pql filename.py SceneName"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/videos")
async def api_list_videos(user: Dict = Depends(verify_api_key)):
    """List all available videos"""
    videos = url_manager.get_all_videos()
    return {
        "videos": videos,
        "count": len(videos),
        "base_url": VIDEO_BASE_URL
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": str(request.url)
        }
    )


# ==================== MAIN ====================

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server"""
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║               Xe-Bot Animation API Server                 ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  Server: http://{host}:{port}                               ║
    ║  Docs:   http://{host}:{port}/docs                          ║
    ║                                                           ║
    ║  Public API Endpoints:                                    ║
    ║    POST /api/keys/create  - Get API key                   ║
    ║    GET  /api/search       - Search arXiv papers           ║
    ║    POST /api/generate     - Generate animation (async)    ║
    ║    GET  /api/jobs/{{id}}    - Check job status              ║
    ║    POST /api/generate-code - Get Manim code only          ║
    ║    GET  /api/videos       - List all videos               ║
    ║                                                           ║
    ║  Internal Endpoints:                                      ║
    ║    POST /process          - Process paper (sync)          ║
    ║    GET  /papers           - List all papers               ║
    ║    GET  /videos           - List videos                   ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host=host, port=port, timeout_keep_alive=120)


if __name__ == "__main__":
    run_server()

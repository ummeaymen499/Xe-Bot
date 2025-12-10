"""
Xe-Bot Animation SDK
Python client for the Xe-Bot Animation API
"""
import httpx
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class Video:
    """Generated video information"""
    type: str
    topic: Optional[str]
    video_url: str
    download_url: str


@dataclass
class AnimationResult:
    """Result of animation generation"""
    job_id: str
    status: str
    paper_title: Optional[str]
    videos: List[Video]
    segments_count: int


class XeBotClient:
    """
    Client for Xe-Bot Animation API
    
    Usage:
        client = XeBotClient(api_key="your-api-key")
        
        # Search for papers
        papers = client.search("transformers")
        
        # Generate animation
        result = client.generate_animation("1706.03762")
        
        # Get just the code
        code = client.generate_code("Neural Networks", ["layers", "activation"])
    """
    
    def __init__(
        self, 
        api_key: str,
        base_url: str = "http://localhost:8000"
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search arXiv for papers
        
        Args:
            query: Search query (topic, keywords, or arXiv ID)
            max_results: Maximum number of results (default 5, max 20)
        
        Returns:
            List of paper dictionaries
        """
        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/api/search",
                params={"query": query, "max_results": max_results},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get("papers", [])
    
    def generate_animation(
        self,
        arxiv_id: str,
        quality: str = "low",
        render: bool = True,
        wait: bool = True,
        timeout: int = 900
    ) -> AnimationResult:
        """
        Generate animation for an arXiv paper
        
        Args:
            arxiv_id: arXiv paper ID (e.g., "1706.03762")
            quality: Video quality - "low", "medium", or "high"
            render: Whether to render videos (False = code only)
            wait: Wait for completion (default True)
            timeout: Max wait time in seconds (default 900 = 15 min)
        
        Returns:
            AnimationResult with videos and metadata
        """
        with httpx.Client(timeout=30) as client:
            # Start the job
            response = client.post(
                f"{self.base_url}/api/generate",
                json={
                    "arxiv_id": arxiv_id,
                    "quality": quality,
                    "render": render
                },
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            job_id = data["job_id"]
            
            if not wait:
                return AnimationResult(
                    job_id=job_id,
                    status="queued",
                    paper_title=None,
                    videos=[],
                    segments_count=0
                )
            
            # Poll for completion
            start_time = time.time()
            while time.time() - start_time < timeout:
                status = self.get_job_status(job_id)
                
                if status["status"] == "completed":
                    videos = [
                        Video(
                            type=v.get("type", "segment"),
                            topic=v.get("topic"),
                            video_url=v.get("video_url", ""),
                            download_url=v.get("download_url", "")
                        )
                        for v in status.get("videos", [])
                    ]
                    return AnimationResult(
                        job_id=job_id,
                        status="completed",
                        paper_title=status.get("paper", {}).get("title"),
                        videos=videos,
                        segments_count=status.get("segments_count", 0)
                    )
                
                elif status["status"] == "failed":
                    raise Exception(f"Animation failed: {status.get('error')}")
                
                time.sleep(5)  # Poll every 5 seconds
            
            raise TimeoutError(f"Animation timed out after {timeout} seconds")
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of an animation job"""
        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/api/jobs/{job_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    def generate_code(
        self,
        topic: str,
        key_concepts: List[str] = None,
        style: str = "explanatory"
    ) -> str:
        """
        Generate Manim code without rendering
        
        Args:
            topic: Topic to visualize
            key_concepts: List of key concepts to include
            style: Animation style ("explanatory", "dramatic", "minimal")
        
        Returns:
            Manim Python code as string
        """
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/api/generate-code",
                json={
                    "topic": topic,
                    "key_concepts": key_concepts or [],
                    "style": style
                },
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get("manim_code", "")
    
    def list_videos(self) -> List[Dict[str, Any]]:
        """List all available videos"""
        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/api/videos",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get("videos", [])
    
    def download_video(self, video_url: str, save_path: str):
        """Download a video to local file"""
        with httpx.Client() as client:
            response = client.get(video_url)
            response.raise_for_status()
            
            with open(save_path, "wb") as f:
                f.write(response.content)


# Convenience function
def create_client(api_key: str, base_url: str = "http://localhost:8000") -> XeBotClient:
    """Create a Xe-Bot client"""
    return XeBotClient(api_key=api_key, base_url=base_url)


# Example usage
if __name__ == "__main__":
    # Create client
    client = XeBotClient(
        api_key="demo-key-12345",
        base_url="http://localhost:8000"
    )
    
    # Search for papers
    print("Searching for transformer papers...")
    papers = client.search("attention mechanism", max_results=3)
    for p in papers:
        print(f"  - {p['title'][:60]}... ({p['arxiv_id']})")
    
    # Generate code (quick)
    print("\nGenerating Manim code...")
    code = client.generate_code(
        "Self-Attention Mechanism",
        key_concepts=["query", "key", "value", "attention weights"]
    )
    print(f"Generated {len(code)} characters of code")
    
    # Optionally generate full animation
    # result = client.generate_animation("1706.03762")
    # print(f"Generated {len(result.videos)} videos")

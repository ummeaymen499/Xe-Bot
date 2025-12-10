"""
Xe-Bot MCP Server
Exposes animation generation as an MCP tool for AI assistants
"""
import os
import json
import asyncio
from pathlib import Path
from typing import Any
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from src.config import config
from src.agents.orchestrator import WorkflowOrchestrator
from src.extraction.paper_fetcher import PaperFetcher
from src.animation.generator import ManimAnimationGenerator

# Initialize server
server = Server("xe-bot-mcp")

# Initialize components
orchestrator = WorkflowOrchestrator()
fetcher = PaperFetcher()
animation_generator = ManimAnimationGenerator()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="search_arxiv",
            description="Search arXiv for research papers by query or topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (topic, keywords, or arXiv ID)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="generate_animation",
            description="Generate an animated video explanation for a research paper from arXiv",
            inputSchema={
                "type": "object",
                "properties": {
                    "arxiv_id": {
                        "type": "string",
                        "description": "arXiv paper ID (e.g., '2206.02977' or '2206.02977v1')"
                    },
                    "quality": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Video quality (default: low for faster generation)",
                        "default": "low"
                    },
                    "render": {
                        "type": "boolean",
                        "description": "Whether to render the animation (default: true)",
                        "default": True
                    }
                },
                "required": ["arxiv_id"]
            }
        ),
        Tool(
            name="get_paper_info",
            description="Get information about a specific arXiv paper",
            inputSchema={
                "type": "object",
                "properties": {
                    "arxiv_id": {
                        "type": "string",
                        "description": "arXiv paper ID"
                    }
                },
                "required": ["arxiv_id"]
            }
        ),
        Tool(
            name="list_animations",
            description="List all generated animations",
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_id": {
                        "type": "string",
                        "description": "Optional: Filter by paper arXiv ID"
                    }
                }
            }
        ),
        Tool(
            name="get_animation_code",
            description="Get the Manim code for a specific animation",
            inputSchema={
                "type": "object",
                "properties": {
                    "segment_topic": {
                        "type": "string",
                        "description": "Topic or content to generate animation code for"
                    },
                    "key_concepts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Key concepts to visualize"
                    }
                },
                "required": ["segment_topic"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls"""
    
    if name == "search_arxiv":
        return await handle_search_arxiv(arguments)
    elif name == "generate_animation":
        return await handle_generate_animation(arguments)
    elif name == "get_paper_info":
        return await handle_get_paper_info(arguments)
    elif name == "list_animations":
        return await handle_list_animations(arguments)
    elif name == "get_animation_code":
        return await handle_get_animation_code(arguments)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def handle_search_arxiv(arguments: dict) -> list[TextContent]:
    """Search arXiv for papers"""
    import arxiv
    
    query = arguments.get("query", "")
    max_results = arguments.get("max_results", 5)
    
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        for paper in client.results(search):
            results.append({
                "arxiv_id": paper.entry_id.split("/")[-1],
                "title": paper.title,
                "authors": [a.name for a in paper.authors[:3]],
                "summary": paper.summary[:300] + "..." if len(paper.summary) > 300 else paper.summary,
                "published": paper.published.strftime("%Y-%m-%d") if paper.published else None,
                "pdf_url": paper.pdf_url
            })
        
        return [TextContent(
            type="text",
            text=json.dumps({"papers": results, "count": len(results)}, indent=2)
        )]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error searching arXiv: {str(e)}")]


async def handle_generate_animation(arguments: dict) -> list[TextContent]:
    """Generate animation for a paper"""
    arxiv_id = arguments.get("arxiv_id", "")
    quality = arguments.get("quality", "low")
    render = arguments.get("render", True)
    
    if not arxiv_id:
        return [TextContent(type="text", text="Error: arxiv_id is required")]
    
    try:
        # Process the paper through the full pipeline
        result = await orchestrator.process_paper(
            arxiv_id=arxiv_id,
            render_animations=render,
            save_to_db=True
        )
        
        # Format response
        response = {
            "status": result.get("status"),
            "paper": result.get("paper"),
            "segments_count": len(result.get("segments", [])),
            "animations": []
        }
        
        # Add animation info
        for anim in result.get("animations", []):
            anim_info = {
                "type": anim.get("type", "segment"),
                "topic": anim.get("topic"),
                "status": anim.get("status"),
                "file_path": anim.get("file_path")
            }
            response["animations"].append(anim_info)
        
        return [TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error generating animation: {str(e)}")]


async def handle_get_paper_info(arguments: dict) -> list[TextContent]:
    """Get paper information"""
    arxiv_id = arguments.get("arxiv_id", "")
    
    if not arxiv_id:
        return [TextContent(type="text", text="Error: arxiv_id is required")]
    
    try:
        paper_data = await fetcher.fetch_paper(arxiv_id)
        
        response = {
            "arxiv_id": paper_data.get("arxiv_id"),
            "title": paper_data.get("title"),
            "authors": paper_data.get("authors"),
            "abstract": paper_data.get("abstract"),
            "pdf_url": paper_data.get("pdf_url"),
            "text_length": len(paper_data.get("full_text", ""))
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error fetching paper: {str(e)}")]


async def handle_list_animations(arguments: dict) -> list[TextContent]:
    """List generated animations"""
    paper_filter = arguments.get("paper_id")
    
    try:
        output_dir = Path("output/animations/videos")
        videos = []
        
        for mp4_file in output_dir.rglob("*.mp4"):
            if "partial_movie_files" in str(mp4_file):
                continue
            
            # Extract info from path
            relative_path = mp4_file.relative_to(output_dir)
            animation_type = "unknown"
            
            if "segment_" in str(relative_path):
                import re
                match = re.search(r'segment_(\d+)', str(relative_path))
                animation_type = f"segment_{match.group(1)}" if match else "segment"
            elif "full_introduction" in str(relative_path):
                animation_type = "full_introduction"
            
            videos.append({
                "file_path": str(mp4_file),
                "animation_type": animation_type,
                "file_size_mb": round(mp4_file.stat().st_size / (1024 * 1024), 2),
                "scene_name": mp4_file.stem
            })
        
        return [TextContent(
            type="text",
            text=json.dumps({"videos": videos, "count": len(videos)}, indent=2)
        )]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error listing animations: {str(e)}")]


async def handle_get_animation_code(arguments: dict) -> list[TextContent]:
    """Generate animation code without rendering"""
    from src.llm.openrouter_client import openrouter_client
    
    segment_topic = arguments.get("segment_topic", "")
    key_concepts = arguments.get("key_concepts", [])
    
    if not segment_topic:
        return [TextContent(type="text", text="Error: segment_topic is required")]
    
    try:
        segment = {
            "topic": segment_topic,
            "topic_category": "concept",
            "key_concepts": key_concepts,
            "content": segment_topic
        }
        
        code = await openrouter_client.generate_animation_code(
            segment,
            animation_style="explanatory"
        )
        
        return [TextContent(
            type="text",
            text=f"Generated Manim Code:\n\n```python\n{code}\n```"
        )]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error generating code: {str(e)}")]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

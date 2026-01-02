"""
Agentic Workflow Orchestrator
Implements the multi-agent flow for paper processing and animation generation
"""
import asyncio
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import config
from src.database import (
    db_manager, ResearchPaper, PaperIntroduction, 
    IntroSegment, Animation, AgentLog, ProcessingStatus
)
from src.extraction import paper_fetcher, PaperData
from src.llm import openrouter_client
from src.animation import animation_generator, templates

console = Console()


class AgentType(Enum):
    """Types of agents in the workflow"""
    FETCHER = "fetcher"
    EXTRACTOR = "extractor"
    SEGMENTER = "segmenter"
    ANIMATOR = "animator"
    ORCHESTRATOR = "orchestrator"


@dataclass
class AgentResult:
    """Result from an agent operation"""
    success: bool
    agent: AgentType
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time_ms: int = 0


class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.name = agent_type.value
    
    async def execute(self, *args, **kwargs) -> AgentResult:
        """Execute the agent's task"""
        raise NotImplementedError
    
    def log_action(self, session, paper_id: int, action: str, 
                   input_data: dict, output_data: dict, 
                   status: str = "success", error: str = None,
                   execution_time: int = 0):
        """Log agent action to database"""
        try:
            log = AgentLog(
                paper_id=paper_id,
                agent_name=self.name,
                action=action,
                input_data=input_data,
                output_data=output_data,
                status=status,
                error_message=error,
                execution_time_ms=execution_time
            )
            session.add(log)
            session.commit()
        except Exception as e:
            console.print(f"[yellow]Warning: Could not log action: {e}[/yellow]")


class FetcherAgent(BaseAgent):
    """Agent responsible for fetching research papers"""
    
    def __init__(self):
        super().__init__(AgentType.FETCHER)
    
    async def execute(self, arxiv_id: str, session=None) -> AgentResult:
        """Fetch a paper from arXiv"""
        start_time = time.time()
        
        try:
            console.print(f"\n[bold blue]🔍 Fetcher Agent: Retrieving paper {arxiv_id}[/bold blue]")
            
            # Fetch paper data
            paper_data = await paper_fetcher.fetch_and_extract(arxiv_id)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            result_data = {
                "arxiv_id": paper_data.arxiv_id,
                "title": paper_data.title,
                "authors": paper_data.authors,
                "abstract": paper_data.abstract,
                "pdf_url": paper_data.pdf_url,
                "full_text": paper_data.full_text,
                "text_length": len(paper_data.full_text or "")
            }
            
            console.print(f"[green]✓ Fetched: {paper_data.title[:60]}...[/green]")
            
            return AgentResult(
                success=True,
                agent=self.agent_type,
                data=result_data,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            console.print(f"[red]✗ Fetcher error: {e}[/red]")
            return AgentResult(
                success=False,
                agent=self.agent_type,
                error=str(e),
                execution_time_ms=execution_time
            )


class ExtractorAgent(BaseAgent):
    """Agent responsible for extracting introductions from papers"""
    
    def __init__(self):
        super().__init__(AgentType.EXTRACTOR)
    
    async def execute(self, paper_text: str, session=None) -> AgentResult:
        """Extract introduction from paper text"""
        start_time = time.time()
        
        try:
            console.print(f"\n[bold blue]📄 Extractor Agent: Extracting introduction[/bold blue]")
            
            # Use LLM to extract introduction
            introduction = await openrouter_client.extract_introduction(paper_text)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            word_count = len(introduction.split())
            
            result_data = {
                "introduction": introduction,
                "word_count": word_count
            }
            
            console.print(f"[green]✓ Extracted introduction ({word_count} words)[/green]")
            
            return AgentResult(
                success=True,
                agent=self.agent_type,
                data=result_data,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            console.print(f"[red]✗ Extractor error: {e}[/red]")
            return AgentResult(
                success=False,
                agent=self.agent_type,
                error=str(e),
                execution_time_ms=execution_time
            )


class SegmenterAgent(BaseAgent):
    """Agent responsible for segmenting introductions into topics"""
    
    def __init__(self):
        super().__init__(AgentType.SEGMENTER)
    
    async def execute(self, introduction: str, session=None) -> AgentResult:
        """Segment introduction into logical parts"""
        start_time = time.time()
        
        try:
            console.print(f"\n[bold blue]✂️ Segmenter Agent: Breaking into segments[/bold blue]")
            
            # Use LLM to segment introduction
            segments = await openrouter_client.segment_introduction(introduction)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            result_data = {
                "segments": segments,
                "segment_count": len(segments)
            }
            
            console.print(f"[green]✓ Created {len(segments)} segments[/green]")
            for i, seg in enumerate(segments):
                console.print(f"   {i+1}. {seg.get('topic', 'Unknown')} [{seg.get('topic_category', 'general')}]")
            
            return AgentResult(
                success=True,
                agent=self.agent_type,
                data=result_data,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            console.print(f"[red]✗ Segmenter error: {e}[/red]")
            return AgentResult(
                success=False,
                agent=self.agent_type,
                error=str(e),
                execution_time_ms=execution_time
            )


class AnimatorAgent(BaseAgent):
    """Agent responsible for generating animations"""
    
    def __init__(self):
        super().__init__(AgentType.ANIMATOR)
    
    async def execute(
        self, 
        title: str,
        segments: List[Dict[str, Any]], 
        generate_per_segment: bool = True,
        render: bool = True,
        session=None
    ) -> AgentResult:
        """Generate animations for segments"""
        start_time = time.time()
        
        try:
            console.print(f"\n[bold blue]🎬 Animator Agent: Generating animations[/bold blue]")
            
            animations = []
            
            if generate_per_segment:
                # Generate animation for each segment
                failed_segments = []
                for i, segment in enumerate(segments):
                    console.print(f"   Generating animation for segment {i+1}/{len(segments)}...")
                    
                    animation_data = {
                        "segment_index": i,
                        "topic": segment.get("topic", f"Segment {i+1}"),
                        "manim_code": None,
                        "file_path": None,
                        "status": "pending",
                        "error": None
                    }
                    
                    try:
                        # Generate code using LLM
                        code = await openrouter_client.generate_animation_code(
                            segment,
                            animation_style="explanatory"
                        )
                        animation_data["manim_code"] = code
                        animation_data["status"] = "code_generated"
                        
                        # Optionally render the animation
                        if render:
                            try:
                                result = animation_generator.render_animation(
                                    code,
                                    f"segment_{i+1}",
                                    quality="low_quality"  # Use low quality for speed
                                )
                                animation_data["file_path"] = result.file_path
                                animation_data["status"] = "rendered" if result.success else "render_failed"
                                if result.error_message:
                                    animation_data["error"] = result.error_message
                                    
                                if result.success:
                                    console.print(f"   [green]✓ Segment {i+1} rendered successfully[/green]")
                                else:
                                    console.print(f"   [yellow]⚠ Segment {i+1} render failed, continuing...[/yellow]")
                                    failed_segments.append(i+1)
                                    
                            except Exception as render_error:
                                console.print(f"   [yellow]⚠ Segment {i+1} render exception: {str(render_error)[:100]}[/yellow]")
                                animation_data["status"] = "render_exception"
                                animation_data["error"] = str(render_error)
                                failed_segments.append(i+1)
                                # Continue to next segment instead of failing entire process
                                
                    except Exception as gen_error:
                        console.print(f"   [yellow]⚠ Segment {i+1} code generation failed: {str(gen_error)[:100]}[/yellow]")
                        animation_data["status"] = "generation_failed"
                        animation_data["error"] = str(gen_error)
                        failed_segments.append(i+1)
                        # Continue to next segment instead of failing entire process
                    
                    animations.append(animation_data)
                
                # Report on failed segments
                if failed_segments:
                    console.print(f"   [yellow]Note: {len(failed_segments)} segment(s) had issues: {failed_segments}[/yellow]")
            
            # Also generate a combined full animation
            console.print("   Generating full combined animation...")
            
            full_animation = {
                "type": "full",
                "manim_code": None,
                "file_path": None,
                "status": "pending",
                "error": None
            }
            
            try:
                full_code = await openrouter_client.generate_full_animation_code(title, segments)
                full_animation["manim_code"] = full_code
                full_animation["status"] = "code_generated"
                
                if render:
                    try:
                        result = animation_generator.render_animation(
                            full_code,
                            "full_introduction",
                            quality="medium_quality"
                        )
                        full_animation["file_path"] = result.file_path
                        full_animation["status"] = "rendered" if result.success else "render_failed"
                        if result.error_message:
                            full_animation["error"] = result.error_message
                            
                        if result.success:
                            console.print(f"   [green]✓ Full animation rendered successfully[/green]")
                        else:
                            console.print(f"   [yellow]⚠ Full animation render failed: {result.error_message[:100] if result.error_message else 'Unknown'}[/yellow]")
                            
                    except Exception as render_error:
                        console.print(f"   [yellow]⚠ Full animation render exception: {str(render_error)[:100]}[/yellow]")
                        full_animation["status"] = "render_exception"
                        full_animation["error"] = str(render_error)
                        
            except Exception as gen_error:
                console.print(f"   [yellow]⚠ Full animation code generation failed: {str(gen_error)[:100]}[/yellow]")
                full_animation["status"] = "generation_failed"
                full_animation["error"] = str(gen_error)
            
            animations.append(full_animation)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            successful = sum(1 for a in animations if a.get("status") in ["rendered", "code_generated"])
            
            result_data = {
                "animations": animations,
                "total_count": len(animations),
                "successful_count": successful
            }
            
            console.print(f"[green]✓ Generated {successful}/{len(animations)} animations[/green]")
            
            return AgentResult(
                success=True,
                agent=self.agent_type,
                data=result_data,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            console.print(f"[red]✗ Animator error: {e}[/red]")
            return AgentResult(
                success=False,
                agent=self.agent_type,
                error=str(e),
                execution_time_ms=execution_time
            )


class WorkflowOrchestrator:
    """
    Main orchestrator for the agentic workflow
    Coordinates all agents to process papers and generate animations
    """
    
    def __init__(self):
        self.fetcher = FetcherAgent()
        self.extractor = ExtractorAgent()
        self.segmenter = SegmenterAgent()
        self.animator = AnimatorAgent()
        
        # Try to initialize database
        try:
            db_manager.init_sync_engine()
            self.db_available = True
        except Exception as e:
            console.print(f"[yellow]Warning: Database not available: {e}[/yellow]")
            self.db_available = False
    
    async def process_paper(
        self,
        arxiv_id: str,
        render_animations: bool = True,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Full pipeline to process a paper and generate animations
        
        Args:
            arxiv_id: arXiv paper ID
            render_animations: Whether to render animations (or just generate code)
            save_to_db: Whether to save results to database
        
        Returns:
            Complete processing results
        """
        console.print("\n" + "="*60)
        console.print("[bold magenta]🤖 Xe-Bot: Research Paper Animation Pipeline[/bold magenta]")
        console.print("="*60)
        
        results = {
            "arxiv_id": arxiv_id,
            "status": "processing",
            "stages": {},
            "animations": [],
            "errors": []
        }
        
        session = None
        paper_record = None
        
        if save_to_db and self.db_available:
            try:
                session = db_manager.get_session()
            except:
                session = None
        
        try:
            # Stage 1: Fetch Paper
            console.print("\n[bold]Stage 1/4: Fetching Paper[/bold]")
            fetch_result = await self.fetcher.execute(arxiv_id, session)
            results["stages"]["fetch"] = {
                "success": fetch_result.success,
                "time_ms": fetch_result.execution_time_ms
            }
            
            if not fetch_result.success:
                results["status"] = "failed"
                results["errors"].append(f"Fetch failed: {fetch_result.error}")
                return results
            
            paper_data = fetch_result.data
            results["paper"] = {
                "title": paper_data["title"],
                "authors": paper_data["authors"],
                "abstract": paper_data["abstract"][:500]
            }
            
            # Save paper to database (check if exists first)
            if session:
                # Check if paper already exists
                existing_paper = session.query(ResearchPaper).filter_by(arxiv_id=arxiv_id).first()
                if existing_paper:
                    # Update existing paper
                    paper_record = existing_paper
                    paper_record.status = ProcessingStatus.EXTRACTING
                    console.print(f"[yellow]Paper already exists, re-processing...[/yellow]")
                else:
                    # Create new paper record
                    paper_record = ResearchPaper(
                        arxiv_id=arxiv_id,
                        title=paper_data["title"],
                        authors=paper_data["authors"],
                        abstract=paper_data["abstract"],
                        pdf_url=paper_data["pdf_url"],
                        status=ProcessingStatus.EXTRACTING
                    )
                    session.add(paper_record)
                session.commit()
            
            # Stage 2: Extract Introduction
            console.print("\n[bold]Stage 2/4: Extracting Introduction[/bold]")
            extract_result = await self.extractor.execute(paper_data["full_text"], session)
            results["stages"]["extract"] = {
                "success": extract_result.success,
                "time_ms": extract_result.execution_time_ms
            }
            
            if not extract_result.success:
                results["status"] = "failed"
                results["errors"].append(f"Extract failed: {extract_result.error}")
                if paper_record:
                    paper_record.status = ProcessingStatus.FAILED
                    session.commit()
                return results
            
            introduction = extract_result.data["introduction"]
            results["introduction_preview"] = introduction[:500] + "..."
            
            # Save introduction to database
            if session and paper_record:
                intro_record = PaperIntroduction(
                    paper_id=paper_record.id,
                    content=introduction,
                    word_count=extract_result.data["word_count"]
                )
                session.add(intro_record)
                paper_record.status = ProcessingStatus.SEGMENTING
                session.commit()
            
            # Stage 3: Segment Introduction
            console.print("\n[bold]Stage 3/4: Segmenting Introduction[/bold]")
            segment_result = await self.segmenter.execute(introduction, session)
            results["stages"]["segment"] = {
                "success": segment_result.success,
                "time_ms": segment_result.execution_time_ms
            }
            
            if not segment_result.success:
                results["status"] = "failed"
                results["errors"].append(f"Segment failed: {segment_result.error}")
                if paper_record:
                    paper_record.status = ProcessingStatus.FAILED
                    session.commit()
                return results
            
            segments = segment_result.data["segments"]
            results["segments"] = [
                {
                    "topic": s.get("topic"),
                    "category": s.get("topic_category"),
                    "concepts": s.get("key_concepts", [])
                }
                for s in segments
            ]
            
            # Save segments to database
            if session and paper_record:
                for i, seg in enumerate(segments):
                    seg_record = IntroSegment(
                        paper_id=paper_record.id,
                        segment_order=i,
                        content=seg.get("content", ""),
                        topic=seg.get("topic"),
                        topic_category=seg.get("topic_category"),
                        key_concepts=seg.get("key_concepts", []),
                        animation_hints=seg.get("animation_hints", {})
                    )
                    session.add(seg_record)
                paper_record.status = ProcessingStatus.ANIMATING
                session.commit()
            
            # Stage 4: Generate Animations
            console.print("\n[bold]Stage 4/4: Generating Animations[/bold]")
            animation_result = await self.animator.execute(
                title=paper_data["title"],
                segments=segments,
                generate_per_segment=True,
                render=render_animations,
                session=session
            )
            results["stages"]["animate"] = {
                "success": animation_result.success,
                "time_ms": animation_result.execution_time_ms
            }
            
            if animation_result.success:
                results["animations"] = animation_result.data["animations"]
                
                # Save animations to database
                if session and paper_record:
                    try:
                        for anim_data in animation_result.data["animations"]:
                            anim_record = Animation(
                                paper_id=paper_record.id,
                                animation_type=anim_data.get("type", "segment"),
                                file_path=anim_data.get("file_path"),
                                manim_code=anim_data.get("manim_code"),
                                status=ProcessingStatus.COMPLETED if anim_data.get("file_path") else ProcessingStatus.PENDING
                            )
                            session.add(anim_record)
                        paper_record.status = ProcessingStatus.COMPLETED
                        session.commit()
                    except Exception as db_err:
                        console.print(f"[yellow]Warning: Could not save to database: {db_err}[/yellow]")
                        session.rollback()
            
            results["status"] = "completed"
            
            # Summary
            console.print("\n" + "="*60)
            console.print("[bold green]✓ Pipeline Complete![/bold green]")
            console.print(f"  Paper: {paper_data['title'][:50]}...")
            console.print(f"  Segments: {len(segments)}")
            console.print(f"  Animations: {len(results['animations'])}")
            console.print("="*60)
            
        except Exception as e:
            results["status"] = "failed"
            results["errors"].append(str(e))
            console.print(f"[red]Pipeline error: {e}[/red]")
            
            if session and paper_record:
                try:
                    paper_record.status = ProcessingStatus.FAILED
                    session.commit()
                except:
                    session.rollback()
        
        finally:
            if session:
                try:
                    session.close()
                except:
                    pass
        
        return results
    
    async def process_paper_with_callbacks(
        self,
        arxiv_id: str,
        render_animations: bool = True,
        save_to_db: bool = True,
        on_stage_change: callable = None
    ) -> Dict[str, Any]:
        """
        Full pipeline with stage callbacks for real-time tracking
        
        Args:
            arxiv_id: arXiv paper ID
            render_animations: Whether to render animations
            save_to_db: Whether to save to database
            on_stage_change: Callback function(stage, detail, progress)
        """
        def update(stage: str, detail: str, progress: int):
            if on_stage_change:
                on_stage_change(stage, detail, progress)
        
        console.print("\n" + "="*60)
        console.print("[bold magenta]🤖 Xe-Bot: Research Paper Animation Pipeline[/bold magenta]")
        console.print("="*60)
        
        results = {
            "arxiv_id": arxiv_id,
            "status": "processing",
            "stages": {},
            "animations": [],
            "segments": [],
            "errors": []
        }
        
        session = None
        paper_record = None
        
        if save_to_db and self.db_available:
            try:
                session = db_manager.get_session()
            except:
                session = None
        
        try:
            # Stage 1: Fetch Paper
            update("fetching", f"Downloading paper {arxiv_id} from arXiv...", 5)
            console.print("\n[bold]Stage 1/4: Fetching Paper[/bold]")
            fetch_result = await self.fetcher.execute(arxiv_id, session)
            results["stages"]["fetch"] = {
                "success": fetch_result.success,
                "time_ms": fetch_result.execution_time_ms
            }
            
            if not fetch_result.success:
                results["status"] = "failed"
                results["errors"].append(f"Fetch failed: {fetch_result.error}")
                update("failed", f"Failed to fetch paper: {fetch_result.error}", 5)
                return results
            
            paper_data = fetch_result.data
            results["paper"] = {
                "title": paper_data["title"],
                "authors": paper_data["authors"],
                "abstract": paper_data["abstract"][:500],
                "arxiv_id": arxiv_id
            }
            update("fetching", f"Downloaded: {paper_data['title'][:50]}...", 15)
            
            # Save paper to database
            if session:
                existing_paper = session.query(ResearchPaper).filter_by(arxiv_id=arxiv_id).first()
                if existing_paper:
                    paper_record = existing_paper
                    paper_record.status = ProcessingStatus.EXTRACTING
                else:
                    paper_record = ResearchPaper(
                        arxiv_id=arxiv_id,
                        title=paper_data["title"],
                        authors=paper_data["authors"],
                        abstract=paper_data["abstract"],
                        pdf_url=paper_data["pdf_url"],
                        status=ProcessingStatus.EXTRACTING
                    )
                    session.add(paper_record)
                session.commit()
            
            # Stage 2: Extract Introduction
            update("extracting", "Analyzing paper and extracting introduction...", 25)
            console.print("\n[bold]Stage 2/4: Extracting Introduction[/bold]")
            extract_result = await self.extractor.execute(paper_data["full_text"], session)
            results["stages"]["extract"] = {
                "success": extract_result.success,
                "time_ms": extract_result.execution_time_ms
            }
            
            if not extract_result.success:
                results["status"] = "failed"
                results["errors"].append(f"Extract failed: {extract_result.error}")
                update("failed", f"Failed to extract introduction: {extract_result.error}", 25)
                if paper_record:
                    paper_record.status = ProcessingStatus.FAILED
                    session.commit()
                return results
            
            introduction = extract_result.data["introduction"]
            word_count = extract_result.data["word_count"]
            results["introduction_preview"] = introduction[:500] + "..."
            update("extracting", f"Extracted {word_count} words from introduction", 35)
            
            # Save introduction to database
            if session and paper_record:
                intro_record = PaperIntroduction(
                    paper_id=paper_record.id,
                    content=introduction,
                    word_count=word_count
                )
                session.add(intro_record)
                paper_record.status = ProcessingStatus.SEGMENTING
                session.commit()
            
            # Stage 3: Segment Introduction
            update("segmenting", "Breaking introduction into logical segments...", 45)
            console.print("\n[bold]Stage 3/4: Segmenting Introduction[/bold]")
            segment_result = await self.segmenter.execute(introduction, session)
            results["stages"]["segment"] = {
                "success": segment_result.success,
                "time_ms": segment_result.execution_time_ms
            }
            
            if not segment_result.success:
                results["status"] = "failed"
                results["errors"].append(f"Segment failed: {segment_result.error}")
                update("failed", f"Failed to segment: {segment_result.error}", 45)
                if paper_record:
                    paper_record.status = ProcessingStatus.FAILED
                    session.commit()
                return results
            
            segments = segment_result.data["segments"]
            results["segments"] = [
                {
                    "topic": s.get("topic"),
                    "topic_category": s.get("topic_category"),
                    "key_concepts": s.get("key_concepts", []),
                    "content": s.get("content", "")[:200] + "..."
                }
                for s in segments
            ]
            update("segmenting", f"Created {len(segments)} segments", 55)
            
            # Save segments to database
            if session and paper_record:
                for i, seg in enumerate(segments):
                    seg_record = IntroSegment(
                        paper_id=paper_record.id,
                        segment_order=i,
                        content=seg.get("content", ""),
                        topic=seg.get("topic"),
                        topic_category=seg.get("topic_category"),
                        key_concepts=seg.get("key_concepts", []),
                        animation_hints=seg.get("animation_hints", {})
                    )
                    session.add(seg_record)
                paper_record.status = ProcessingStatus.ANIMATING
                session.commit()
            
            # Stage 4: Generate Animations
            update("animating", f"Generating animations for {len(segments)} segments...", 60)
            console.print("\n[bold]Stage 4/4: Generating Animations[/bold]")
            
            # Custom animation generation with progress tracking
            animations = []
            total_anims = len(segments) + 1  # segments + full animation
            
            for i, segment in enumerate(segments):
                anim_progress = 60 + int((i / total_anims) * 35)
                update("animating", f"Rendering segment {i+1}/{len(segments)}: {segment.get('topic', 'Unknown')[:30]}...", anim_progress)
                
                animation_data = {
                    "segment_index": i,
                    "type": "segment",
                    "topic": segment.get("topic", f"Segment {i+1}"),
                    "manim_code": None,
                    "file_path": None,
                    "status": "pending",
                    "error": None
                }
                
                try:
                    code = await openrouter_client.generate_animation_code(
                        segment,
                        animation_style="explanatory"
                    )
                    animation_data["manim_code"] = code
                    animation_data["status"] = "code_generated"
                    
                    if render_animations:
                        try:
                            result = animation_generator.render_animation(
                                code,
                                f"segment_{i+1}",
                                quality="low_quality"
                            )
                            animation_data["file_path"] = result.file_path
                            animation_data["status"] = "rendered" if result.success else "render_failed"
                            if result.error_message:
                                animation_data["error"] = result.error_message
                        except Exception as render_error:
                            animation_data["status"] = "render_exception"
                            animation_data["error"] = str(render_error)
                except Exception as gen_error:
                    animation_data["status"] = "generation_failed"
                    animation_data["error"] = str(gen_error)
                
                animations.append(animation_data)
            
            # Generate full combined animation
            update("animating", "Generating full combined animation...", 95)
            full_animation = {
                "type": "full",
                "topic": "Full Introduction",
                "manim_code": None,
                "file_path": None,
                "status": "pending",
                "error": None
            }
            
            try:
                full_code = await openrouter_client.generate_full_animation_code(paper_data["title"], segments)
                full_animation["manim_code"] = full_code
                full_animation["status"] = "code_generated"
                
                if render_animations:
                    try:
                        result = animation_generator.render_animation(
                            full_code,
                            "full_introduction",
                            quality="medium_quality"
                        )
                        full_animation["file_path"] = result.file_path
                        full_animation["status"] = "rendered" if result.success else "render_failed"
                        if result.error_message:
                            full_animation["error"] = result.error_message
                    except Exception as render_error:
                        full_animation["status"] = "render_exception"
                        full_animation["error"] = str(render_error)
            except Exception as gen_error:
                full_animation["status"] = "generation_failed"
                full_animation["error"] = str(gen_error)
            
            animations.append(full_animation)
            results["animations"] = animations
            
            # Save animations to database
            if session and paper_record:
                try:
                    for anim_data in animations:
                        anim_record = Animation(
                            paper_id=paper_record.id,
                            animation_type=anim_data.get("type", "segment"),
                            file_path=anim_data.get("file_path"),
                            manim_code=anim_data.get("manim_code"),
                            status=ProcessingStatus.COMPLETED if anim_data.get("file_path") else ProcessingStatus.PENDING
                        )
                        session.add(anim_record)
                    paper_record.status = ProcessingStatus.COMPLETED
                    session.commit()
                except Exception as db_err:
                    console.print(f"[yellow]Warning: Could not save to database: {db_err}[/yellow]")
                    session.rollback()
            
            results["status"] = "completed"
            update("completed", "All animations generated successfully!", 100)
            
            console.print("\n" + "="*60)
            console.print("[bold green]✓ Pipeline Complete![/bold green]")
            console.print(f"  Paper: {paper_data['title'][:50]}...")
            console.print(f"  Segments: {len(segments)}")
            console.print(f"  Animations: {len(animations)}")
            console.print("="*60)
            
        except Exception as e:
            results["status"] = "failed"
            results["errors"].append(str(e))
            update("failed", str(e), 0)
            console.print(f"[red]Pipeline error: {e}[/red]")
            
            if session and paper_record:
                try:
                    paper_record.status = ProcessingStatus.FAILED
                    session.commit()
                except:
                    session.rollback()
        
        finally:
            if session:
                try:
                    session.close()
                except:
                    pass
        
        return results
    
    async def generate_animation_only(
        self,
        text_content: str,
        title: str = "Research Animation"
    ) -> Dict[str, Any]:
        """
        Generate animation from any text content (without full pipeline)
        
        Args:
            text_content: Text content to animate
            title: Animation title
        
        Returns:
            Animation results
        """
        console.print("\n[bold magenta]🎬 Quick Animation Generation[/bold magenta]")
        
        # First segment the content
        segment_result = await self.segmenter.execute(text_content)
        
        if not segment_result.success:
            return {
                "success": False,
                "error": segment_result.error
            }
        
        segments = segment_result.data["segments"]
        
        # Generate animation
        animation_result = await self.animator.execute(
            title=title,
            segments=segments,
            generate_per_segment=False,
            render=True
        )
        
        return {
            "success": animation_result.success,
            "segments": segments,
            "animations": animation_result.data.get("animations", []),
            "error": animation_result.error
        }


# Global orchestrator instance
orchestrator = WorkflowOrchestrator()

"""
Manim Animation Generator
Core module for generating animations from research paper segments
"""
import os
import subprocess
import tempfile
import shutil
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from rich.console import Console

from src.config import config

console = Console()


@dataclass
class AnimationResult:
    """Result of animation generation"""
    success: bool
    file_path: Optional[str]
    manim_code: str
    error_message: Optional[str] = None
    duration_seconds: int = 0


class ManimAnimationGenerator:
    """
    Generates Manim animations from research paper content
    """
    
    def __init__(self):
        self.output_dir = config.animation.output_dir
        # Use lowest quality for faster rendering on limited resources
        self.quality = os.getenv("ANIMATION_QUALITY", "low_quality")
        self.fps = int(os.getenv("ANIMATION_FPS", "15"))  # Lower FPS for faster render
        self.render_timeout = int(os.getenv("RENDER_TIMEOUT", "120"))  # 2 min timeout
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _create_temp_script(self, code: str, scene_name: str) -> Path:
        """Create a temporary Python script with Manim code"""
        temp_dir = Path(tempfile.mkdtemp())
        script_path = temp_dir / f"{scene_name}.py"
        script_path.write_text(code, encoding='utf-8')
        return script_path
    
    def _extract_scene_name(self, code: str) -> str:
        """Extract the scene class name from Manim code"""
        import re
        match = re.search(r'class\s+(\w+)\s*\(\s*(?:Scene|MovingCameraScene|ThreeDScene)', code)
        if match:
            return match.group(1)
        return "GeneratedScene"
    
    def _inject_branding(self, code: str) -> str:
        """Inject 'Animation by Xe-Bot' branding at the end of construct method if not present"""
        import re
        
        # Check if branding already exists
        if "Animation by Xe-Bot" in code or "Xe-Bot" in code:
            return code
        
        # Branding code to inject
        branding_code = '''
        # === Xe-Bot Branding ===
        self.play(*[FadeOut(mob) for mob in self.mobjects if mob is not None])
        branding = Text("Animation by Xe-Bot", font_size=36, color=BLUE)
        self.play(FadeIn(branding))
        self.wait(2)
        self.play(FadeOut(branding))'''
        
        # Find the end of the construct method (last line before class ends or file ends)
        # Look for the construct method and inject branding before the method ends
        lines = code.split('\n')
        new_lines = []
        inside_construct = False
        construct_indent = 0
        injected = False
        
        for i, line in enumerate(lines):
            # Detect construct method start
            if 'def construct(self' in line:
                inside_construct = True
                construct_indent = len(line) - len(line.lstrip())
                new_lines.append(line)
                continue
            
            # If inside construct, check for method end
            if inside_construct and not injected:
                # Check if this line is at same or lower indent level (method end)
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    current_indent = len(line) - len(line.lstrip())
                    
                    # If we hit a new method definition or class, inject before
                    if current_indent <= construct_indent and ('def ' in line or 'class ' in line):
                        # Inject branding before this line
                        indent = ' ' * (construct_indent + 4)
                        new_lines.append(branding_code.replace('\n        ', f'\n{indent}'))
                        injected = True
                        inside_construct = False
            
            new_lines.append(line)
        
        # If still not injected (construct is the last method), append at the end
        if not injected:
            # Find the last non-empty line's indent that's inside construct
            indent = '        '  # Default 8 spaces
            new_lines.append(branding_code.replace('\n        ', f'\n{indent}'))
        
        return '\n'.join(new_lines)
    
    def _ensure_valid_manim_code(self, code: str) -> str:
        """Ensure the code has proper Manim imports and structure"""
        import re
        
        # Check if imports exist
        if "from manim import" not in code and "import manim" not in code:
            imports = "from manim import *\n\n"
            code = imports + code
        
        # Replace any MathTex/Tex with Text to avoid LaTeX requirement
        code = re.sub(r'MathTex\s*\(', 'Text(', code)
        code = re.sub(r'(?<!Ma)Tex\s*\(', 'Text(', code)  # Tex but not MathTex
        
        # Replace problematic unicode characters
        code = code.replace('•', '-')
        code = code.replace('→', '->')
        code = code.replace('←', '<-')
        code = code.replace('≈', '~')
        code = code.replace('≠', '!=')
        code = code.replace('≤', '<=')
        code = code.replace('≥', '>=')
        
        # Check if there's a Scene class
        if "class" not in code or "Scene" not in code:
            # Wrap the code in a basic scene
            code = f'''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Generated animation
        title = Text("Research Animation", font_size=48)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))
        
        # Branding
        branding = Text("Animation by Xe-Bot", font_size=36, color=BLUE)
        self.play(FadeIn(branding))
        self.wait(2)
        self.play(FadeOut(branding))
'''
        
        # Validate Python syntax
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            console.print(f"[yellow]Warning: Code has syntax error: {e}[/yellow]")
            # Return a fallback animation
            code = f'''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        title = Text("Animation Generation Error", font_size=36, color=RED)
        subtitle = Text("Using fallback animation", font_size=24)
        subtitle.next_to(title, DOWN)
        self.play(Write(title), FadeIn(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))
        
        # Branding
        branding = Text("Animation by Xe-Bot", font_size=36, color=BLUE)
        self.play(FadeIn(branding))
        self.wait(2)
        self.play(FadeOut(branding))
'''
        
        # Inject branding if not present
        code = self._inject_branding(code)
        
        return code
    
    def render_animation(
        self,
        manim_code: str,
        output_name: str,
        quality: Optional[str] = None
    ) -> AnimationResult:
        """
        Render a Manim animation from code
        
        Args:
            manim_code: Valid Manim Python code
            output_name: Name for the output file
            quality: Quality setting (low_quality, medium_quality, high_quality)
        
        Returns:
            AnimationResult with status and file path
        """
        quality = quality or self.quality
        
        # Ensure valid code
        manim_code = self._ensure_valid_manim_code(manim_code)
        
        # Extract scene name
        scene_name = self._extract_scene_name(manim_code)
        
        console.print(f"[blue]Rendering animation: {scene_name}[/blue]")
        
        # Create temp script
        script_path = self._create_temp_script(manim_code, output_name)
        temp_dir = script_path.parent
        
        try:
            # Build manim command
            quality_flag = f"--quality={quality[0]}" if quality else "-qm"
            if quality == "low_quality":
                quality_flag = "-ql"
            elif quality == "medium_quality":
                quality_flag = "-qm"
            elif quality == "high_quality":
                quality_flag = "-qh"
            
            output_path = self.output_dir / f"{output_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            
            # Use absolute path for media_dir
            media_dir = Path("output/animations").absolute()
            media_dir.mkdir(parents=True, exist_ok=True)
            
            cmd = [
                "manim",
                quality_flag,
                "--fps", str(self.fps),
                "-o", f"{scene_name}.mp4",
                "--media_dir", str(media_dir),
                str(script_path),
                scene_name
            ]
            
            console.print(f"[cyan]Running: {' '.join(cmd)}[/cyan]")
            
            # Run manim with configurable timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.render_timeout,  # Configurable timeout (default 2 min)
                cwd=temp_dir
            )
            
            # Log output for debugging
            if result.stdout:
                console.print(f"[dim]Manim stdout: {result.stdout[:200]}[/dim]")
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                
                # Check if the file was actually created despite the error
                # (sometimes manim returns error code but still produces output)
                output_file = self._find_output_file(output_name, scene_name)
                # Verify the file was created recently (within last 30 seconds) to avoid picking up old files
                if output_file and output_file.exists() and output_file.stat().st_size > 1000:
                    file_age = time.time() - output_file.stat().st_mtime
                    if file_age < 30:  # Only accept if created in last 30 seconds
                        console.print(f"[yellow]Manim reported error but output exists: {output_file}[/yellow]")
                        return AnimationResult(
                            success=True,
                            file_path=str(output_file),
                            manim_code=manim_code,
                            duration_seconds=self._get_video_duration(output_file)
                        )
                
                console.print(f"[red]Manim error (code {result.returncode}): {error_msg[:500]}[/red]")
                
                # Try fallback animation on failure
                fallback_result = self._render_fallback_animation(scene_name, media_dir)
                if fallback_result:
                    console.print(f"[yellow]Using fallback animation[/yellow]")
                    return AnimationResult(
                        success=True,
                        file_path=str(fallback_result),
                        manim_code=manim_code,
                        error_message=f"Original failed, using fallback: {error_msg[:100]}"
                    )
                
                return AnimationResult(
                    success=False,
                    file_path=None,
                    manim_code=manim_code,
                    error_message=error_msg
                )
            
            # Find the output file
            output_file = self._find_output_file(output_name, scene_name)
            
            if output_file:
                console.print(f"[green]✓ Animation rendered: {output_file}[/green]")
                return AnimationResult(
                    success=True,
                    file_path=str(output_file),
                    manim_code=manim_code,
                    duration_seconds=self._get_video_duration(output_file)
                )
            else:
                return AnimationResult(
                    success=False,
                    file_path=None,
                    manim_code=manim_code,
                    error_message="Output file not found after rendering"
                )
                
        except subprocess.TimeoutExpired:
            console.print(f"[yellow]⚠ Animation timed out, continuing...[/yellow]")
            return AnimationResult(
                success=False,
                file_path=None,
                manim_code=manim_code,
                error_message="Animation rendering timed out (>3 minutes)"
            )
        except Exception as e:
            return AnimationResult(
                success=False,
                file_path=None,
                manim_code=manim_code,
                error_message=str(e)
            )
        finally:
            # Cleanup temp directory
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
    
    def _render_fallback_animation(self, scene_name: str, media_dir: Path) -> Optional[Path]:
        """Render a simple fallback animation when main generation fails"""
        fallback_code = f'''from manim import *

class {scene_name}(Scene):
    def construct(self):
        # Simple fallback animation
        title = Text("{scene_name.replace('_', ' ')}", font_size=40, color=BLUE)
        title.to_edge(UP)
        
        box = Rectangle(width=8, height=4, color=WHITE, fill_opacity=0.1)
        
        content = Text("Animation content\\ngeneration in progress...", font_size=28)
        content.move_to(box)
        
        self.play(Write(title))
        self.play(Create(box), FadeIn(content))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(box), FadeOut(content))
        
        # Branding
        branding = Text("Animation by Xe-Bot", font_size=36, color=BLUE)
        self.play(FadeIn(branding))
        self.wait(2)
        self.play(FadeOut(branding))
'''
        try:
            temp_dir = Path(tempfile.mkdtemp())
            script_path = temp_dir / "fallback.py"
            script_path.write_text(fallback_code, encoding='utf-8')
            
            cmd = [
                "manim", "-ql", "--fps", "30",
                "-o", f"{scene_name}.mp4",
                "--media_dir", str(media_dir),
                str(script_path), scene_name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=temp_dir)
            
            if result.returncode == 0:
                # Find the output
                for mp4 in media_dir.rglob("*.mp4"):
                    if scene_name in mp4.stem and "partial" not in str(mp4):
                        return mp4
            
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None
        except:
            return None
    
    def _find_output_file(self, output_name: str, scene_name: str) -> Optional[Path]:
        """Find the rendered output file"""
        # Wait a moment for file system to sync
        time.sleep(0.5)
        
        # Check common output locations based on manim's output structure
        # Manim creates: media_dir/videos/script_name/quality/scene_name.mp4
        search_dirs = [
            self.output_dir,
            self.output_dir / "videos",
            self.output_dir / "media" / "videos",
            Path("output/media/videos"),
            Path("output/animations"),
        ]
        
        # Search for the scene name in any mp4 file
        for search_dir in search_dirs:
            if search_dir.exists():
                for mp4_file in search_dir.rglob("*.mp4"):
                    # Skip partial files
                    if "partial_movie_files" in str(mp4_file):
                        continue
                    # Match by scene name or output name - must be exact match in filename
                    if mp4_file.stem == scene_name or mp4_file.stem == output_name:
                        console.print(f"[dim]Found output: {mp4_file}[/dim]")
                        return mp4_file
        
        # Second pass: check for files containing the scene name (less strict)
        for search_dir in search_dirs:
            if search_dir.exists():
                for mp4_file in search_dir.rglob("*.mp4"):
                    if "partial_movie_files" in str(mp4_file):
                        continue
                    if scene_name in mp4_file.stem:
                        # Verify it was created recently (within last 30 seconds)
                        if (time.time() - mp4_file.stat().st_mtime) < 30:
                            console.print(f"[dim]Found output: {mp4_file}[/dim]")
                            return mp4_file
        
        # Do NOT fall back to "most recent file" - this causes wrong file to be returned
        # If we can't find the exact file, return None
        return None
    
    def _get_video_duration(self, video_path: Path) -> int:
        """Get video duration in seconds"""
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
                capture_output=True,
                text=True
            )
            return int(float(result.stdout.strip()))
        except:
            return 0
    
    def create_text_animation(self, text: str, title: str = "Research Insight") -> str:
        """
        Create a simple text-based animation
        
        Args:
            text: Text content to animate
            title: Title for the animation
        
        Returns:
            Manim code string
        """
        # Escape special characters
        text = text.replace('"', '\\"').replace('\n', '\\n')
        title = title.replace('"', '\\"')
        
        # Split text into chunks for better display
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) > 50:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        # Generate animation code
        code = f'''from manim import *

class ResearchAnimation(Scene):
    def construct(self):
        # Title
        title = Text("{title}", font_size=42, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # Content chunks
        chunks = {chunks}
        
        previous_text = None
        for i, chunk in enumerate(chunks):
            text = Text(chunk, font_size=28)
            text.next_to(title, DOWN, buff=1.5)
            
            if previous_text:
                self.play(
                    FadeOut(previous_text),
                    FadeIn(text)
                )
            else:
                self.play(Write(text))
            
            self.wait(2)
            previous_text = text
        
        # Fade out
        self.play(FadeOut(title), FadeOut(previous_text))
        self.wait(0.5)
'''
        return code
    
    def create_concept_animation(
        self,
        concepts: List[str],
        title: str = "Key Concepts"
    ) -> str:
        """
        Create an animation highlighting key concepts
        
        Args:
            concepts: List of key concepts
            title: Animation title
        
        Returns:
            Manim code string
        """
        concepts_str = str(concepts)
        
        code = f'''from manim import *

class ConceptAnimation(Scene):
    def construct(self):
        # Title
        title = Text("{title}", font_size=48, color=BLUE)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))
        
        # Concepts
        concepts = {concepts_str}
        
        concept_mobjects = []
        colors = [RED, GREEN, YELLOW, PURPLE, ORANGE, TEAL]
        
        for i, concept in enumerate(concepts):
            color = colors[i % len(colors)]
            text = Text(concept, font_size=32, color=color)
            concept_mobjects.append(text)
        
        # Arrange concepts
        group = VGroup(*concept_mobjects)
        group.arrange(DOWN, buff=0.5)
        group.next_to(title, DOWN, buff=1)
        
        # Animate each concept
        for i, mob in enumerate(concept_mobjects):
            self.play(FadeIn(mob, shift=RIGHT), run_time=0.5)
            self.wait(0.3)
        
        self.wait(2)
        
        # Highlight each concept
        for mob in concept_mobjects:
            self.play(
                mob.animate.scale(1.2),
                rate_func=there_and_back,
                run_time=0.5
            )
        
        self.wait(1)
        
        # Fade out
        self.play(FadeOut(group), FadeOut(title))
'''
        return code
    
    def create_segment_animation(
        self,
        segment: Dict[str, Any],
        segment_number: int
    ) -> str:
        """
        Create animation for a specific segment
        
        Args:
            segment: Segment data with content, topic, concepts
            segment_number: Segment order number
        
        Returns:
            Manim code string
        """
        topic = segment.get('topic', f'Segment {segment_number}')
        category = segment.get('topic_category', 'general')
        content = segment.get('content', '')[:300]  # Limit content length
        concepts = segment.get('key_concepts', [])[:5]  # Limit concepts
        
        # Escape strings
        topic = topic.replace('"', '\\"')
        content = content.replace('"', '\\"').replace('\n', ' ')
        
        # Color scheme based on category
        color_map = {
            'background': 'BLUE',
            'problem_statement': 'RED',
            'motivation': 'GREEN',
            'approach': 'YELLOW',
            'contributions': 'PURPLE',
            'outline': 'ORANGE'
        }
        main_color = color_map.get(category, 'WHITE')
        
        code = f'''from manim import *

class Segment{segment_number}Animation(Scene):
    def construct(self):
        # Segment header
        header = Text("Segment {segment_number}: {topic}", font_size=36, color={main_color})
        header.to_edge(UP)
        
        category_label = Text("[{category}]", font_size=24, color=GRAY)
        category_label.next_to(header, DOWN)
        
        self.play(Write(header))
        self.play(FadeIn(category_label))
        self.wait(1)
        
        # Content summary
        content_text = "{content}"
        
        # Split into lines
        words = content_text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > 45:
                lines.append(" ".join(current_line[:-1]))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
        
        content_group = VGroup()
        for line in lines[:6]:  # Max 6 lines
            text = Text(line, font_size=24)
            content_group.add(text)
        
        content_group.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        content_group.next_to(category_label, DOWN, buff=0.8)
        
        self.play(Write(content_group), run_time=2)
        self.wait(2)
        
        # Key concepts
        concepts = {concepts}
        if concepts:
            self.play(content_group.animate.scale(0.7).to_edge(LEFT))
            
            concepts_title = Text("Key Concepts:", font_size=28, color=YELLOW)
            concepts_title.to_edge(RIGHT).shift(UP * 1.5)
            self.play(Write(concepts_title))
            
            concept_group = VGroup()
            for c in concepts:
                bullet = Text(f"• {{c}}", font_size=22, color={main_color})
                concept_group.add(bullet)
            
            concept_group.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
            concept_group.next_to(concepts_title, DOWN, buff=0.5)
            
            for c in concept_group:
                self.play(FadeIn(c, shift=LEFT), run_time=0.3)
            
            self.wait(2)
        
        # Transition out
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        self.wait(0.5)
'''
        return code


# Global animation generator instance
animation_generator = ManimAnimationGenerator()

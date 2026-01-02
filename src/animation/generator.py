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
        self.render_timeout = int(os.getenv("RENDER_TIMEOUT", "180"))  # 3 min timeout (increased)
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
        match = re.search(r'class\s+(\w+)\s*\(\s*(?:Scene|MovingCameraScene|ThreeDScene|ZoomedScene)', code)
        if match:
            scene_name = match.group(1)
            # Sanitize scene name - remove invalid characters
            scene_name = re.sub(r'[^a-zA-Z0-9_]', '', scene_name)
            if scene_name and scene_name[0].isdigit():
                scene_name = 'Scene' + scene_name
            return scene_name if scene_name else "GeneratedScene"
        return "GeneratedScene"
    
    def _sanitize_scene_name(self, name: str) -> str:
        """Sanitize a string to be a valid Python class name"""
        import re
        # Remove invalid characters, keep alphanumeric and underscore
        name = re.sub(r'[^a-zA-Z0-9_]', '', name.replace(' ', '_').replace('-', '_'))
        # Ensure it starts with a letter
        if name and name[0].isdigit():
            name = 'Scene' + name
        # CamelCase conversion
        parts = name.split('_')
        name = ''.join(part.capitalize() for part in parts if part)
        return name if name else "GeneratedScene"
    
    def _ensure_fadeouts_between_sections(self, code: str) -> str:
        """Ensure FadeOut is called between sections to prevent text overlap"""
        import re
        
        # Pattern to find segment titles or section markers
        # Add FadeOut before creating new segment titles if not already present
        lines = code.split('\n')
        new_lines = []
        prev_had_fadeout = True  # Assume start is clean
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Check if this line creates a segment title or major section
            is_new_section = (
                'seg_title' in stripped.lower() or
                'segment' in stripped.lower() and 'Text(' in stripped or
                re.match(r'.*=\s*Text\(["\'](?:Segment|Section|Background|Problem|Approach|Method|Result|Conclusion)', stripped, re.IGNORECASE)
            )
            
            # If new section and previous lines don't have FadeOut, inject one
            if is_new_section and not prev_had_fadeout:
                indent = len(line) - len(line.lstrip())
                fadeout_line = ' ' * indent + 'self.play(*[FadeOut(m) for m in self.mobjects])'
                new_lines.append(fadeout_line)
            
            new_lines.append(line)
            
            # Track if current line has FadeOut
            if 'FadeOut' in stripped and 'self.mobjects' in stripped:
                prev_had_fadeout = True
            elif 'self.play(' in stripped or 'self.wait(' in stripped:
                prev_had_fadeout = False
        
        return '\n'.join(new_lines)
    
    def _inject_branding(self, code: str) -> str:
        """Inject 'Animation by Xe-Bot' branding at the end of construct method if not present"""
        import re
        
        # Check if branding already exists
        if "Animation by Xe-Bot" in code or "Xe-Bot" in code:
            return code
        
        # Branding code to inject (with FadeOut to clear screen first)
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
        """Ensure the code has proper Manim imports, structure, and FadeOuts between sections"""
        import re
        
        # Check if imports exist
        if "from manim import" not in code and "import manim" not in code:
            imports = "from manim import *\nimport numpy as np\n\n"
            code = imports + code
        
        # Ensure numpy is imported (used in some templates)
        if "import numpy" not in code and "np." in code:
            code = "import numpy as np\n" + code
        
        # Replace any MathTex/Tex with Text to avoid LaTeX requirement
        code = re.sub(r'MathTex\s*\(', 'Text(', code)
        code = re.sub(r'(?<!Ma)Tex\s*\(', 'Text(', code)  # Tex but not MathTex
        
        # Remove LaTeX-specific formatting that won't work with Text
        code = re.sub(r'\\\\frac\{[^}]*\}\{[^}]*\}', 'fraction', code)
        code = re.sub(r'\\\\[a-zA-Z]+\{[^}]*\}', '', code)  # Remove LaTeX commands
        code = re.sub(r'\$[^$]+\$', '', code)  # Remove inline math
        
        # Replace problematic unicode characters
        code = code.replace('•', '-')
        code = code.replace('→', '->')
        code = code.replace('←', '<-')
        code = code.replace('≈', '~')
        code = code.replace('≠', '!=')
        code = code.replace('≤', '<=')
        code = code.replace('≥', '>=')
        code = code.replace('"', '"').replace('"', '"')  # Smart quotes
        code = code.replace(''', "'").replace(''', "'")  # Smart apostrophes
        code = code.replace('…', '...')  # Ellipsis
        code = code.replace('–', '-').replace('—', '-')  # Dashes
        code = code.replace('α', 'alpha').replace('β', 'beta').replace('γ', 'gamma')
        code = code.replace('Δ', 'Delta').replace('δ', 'delta')
        code = code.replace('π', 'pi').replace('σ', 'sigma').replace('μ', 'mu')
        code = code.replace('∞', 'infinity').replace('∑', 'sum')
        
        # Fix common Manim errors
        # 1. Fix empty VGroup animations
        code = re.sub(r'self\.play\(\*\[\s*\]\)', '# Empty animation removed', code)
        
        # 2. Fix FadeIn/FadeOut with empty lists
        code = re.sub(r'self\.play\(\*\[FadeOut\(m\) for m in \[\]\]\)', '# Empty FadeOut removed', code)
        code = re.sub(r'self\.play\(\*\[FadeIn\(m\) for m in \[\]\]\)', '# Empty FadeIn removed', code)
        
        # 3. Ensure run_time is positive
        code = re.sub(r'run_time\s*=\s*0([,\)])', r'run_time=0.1\1', code)
        code = re.sub(r'run_time\s*=\s*-', 'run_time=0.5', code)
        
        # 4. Fix scale(0) which causes issues
        code = re.sub(r'\.scale\(0\)', '.scale(0.01)', code)
        
        # 5. Fix common typos
        code = re.sub(r'Fadeout', 'FadeOut', code)
        code = re.sub(r'Fadein', 'FadeIn', code)
        code = re.sub(r'fadeout', 'FadeOut', code)
        code = re.sub(r'fadein', 'FadeIn', code)
        
        # 6. Ensure proper color constants (fix common issues)
        code = re.sub(r'\bWHITE\s*=', 'WHITE_VAR =', code)  # Don't override constants
        code = re.sub(r'\bBLUE\s*=', 'BLUE_VAR =', code)
        code = re.sub(r'\bRED\s*=', 'RED_VAR =', code)
        
        # 7. Fix multiple inheritance issues
        code = re.sub(r'class\s+(\w+)\s*\(\s*Scene\s*,\s*Scene\s*\)', r'class \1(Scene)', code)
        
        # 8. Limit text length to prevent rendering issues
        def limit_text_length(match):
            text = match.group(1)
            if len(text) > 60:
                text = text[:57] + "..."
            return f'Text("{text}"'
        code = re.sub(r'Text\(["\']([^"\']{61,})["\']', limit_text_length, code)
        
        # 9. Ensure there's a wait at the end before fadeout to prevent abrupt endings
        if 'self.play(*[FadeOut(m) for m in self.mobjects])' in code:
            code = code.replace(
                'self.play(*[FadeOut(m) for m in self.mobjects])',
                'self.wait(0.5)\n        self.play(*[FadeOut(m) for m in self.mobjects])'
            )
        
        # 10. Fix potential division by zero in loops
        code = re.sub(r'/\s*0([^\d.])', r'/1\1', code)
        
        # 11. Add safety check for mobjects before FadeOut
        code = code.replace(
            'self.play(*[FadeOut(m) for m in self.mobjects])',
            'if self.mobjects: self.play(*[FadeOut(m) for m in self.mobjects if m is not None])'
        )
        
        # 12. Fix common issues with LaggedStart
        code = re.sub(r'LaggedStart\(\*\[\s*\]', 'LaggedStart(*[Wait(0.1)]', code)
        
        # 13. Fix Flash import/usage (Flash might need explicit position)
        code = re.sub(r'Flash\(\s*\)', 'Flash(ORIGIN)', code)
        
        # 14. Fix Arrow3D for non-3D scenes (replace with Arrow)
        if 'ThreeDScene' not in code and 'Arrow3D' in code:
            code = code.replace('Arrow3D', 'Arrow')
            code = code.replace('Dot3D', 'Dot')
        
        # 15. Fix invalid numpy operations
        code = re.sub(r'np\.array\(\[([^\]]*)\]\s*\)', lambda m: f'np.array([{m.group(1)}])', code)
        
        # 16. Remove any print statements that might cause issues
        code = re.sub(r'^\s*print\(.*\)\s*$', '# print removed', code, flags=re.MULTILINE)
        
        # 17. Fix common NameError for undefined colors
        color_fixes = {
            'GREY': 'GRAY',
            'GREY_A': 'GRAY_A', 
            'GREY_B': 'GRAY_B',
            'GREY_C': 'GRAY_C',
            'GREY_D': 'GRAY_D',
            'GREY_E': 'GRAY_E',
        }
        for wrong, correct in color_fixes.items():
            code = code.replace(wrong, correct)
        
        # 18. Ensure self.wait() has positive duration
        code = re.sub(r'self\.wait\(\s*0\s*\)', 'self.wait(0.1)', code)
        code = re.sub(r'self\.wait\(\s*-', 'self.wait(0.5', code)
        
        # 19. Fix issue with empty Text() calls
        code = re.sub(r'Text\(\s*\)', 'Text(" ")', code)
        code = re.sub(r'Text\(\s*""\s*\)', 'Text(" ")', code)
        code = re.sub(r"Text\(\s*''\s*\)", 'Text(" ")', code)
        
        # 20. Fix VGroup with None elements
        code = re.sub(r'VGroup\(\s*None\s*\)', 'VGroup()', code)
        
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
        """Render a simple but visually appealing fallback animation when main generation fails"""
        # Sanitize scene name for valid Python class
        safe_scene_name = self._sanitize_scene_name(scene_name)
        if not safe_scene_name:
            safe_scene_name = "FallbackScene"
        
        # Create a clean topic name from scene_name
        topic_name = scene_name.replace('_', ' ').replace('Scene', '').strip()
        if not topic_name:
            topic_name = "Research Concept"
        
        # Keep topic name short and ASCII-safe to avoid rendering issues
        topic_name = ''.join(c for c in topic_name if ord(c) < 128)  # ASCII only
        if len(topic_name) > 35:
            topic_name = topic_name[:32] + "..."
        if not topic_name.strip():
            topic_name = "Research Animation"
        
        # Very simple fallback that should always work
        fallback_code = f'''from manim import *
import numpy as np

class {safe_scene_name}(Scene):
    def construct(self):
        # Ultra-simple reliable animation
        
        # Title with safe text
        title = Text("{topic_name}", font_size=32, color=BLUE)
        title.to_edge(UP, buff=0.8)
        self.play(Write(title), run_time=1)
        
        # Simple circle animation
        circle = Circle(radius=1.5, color=BLUE, stroke_width=3)
        circle.set_fill(BLUE, opacity=0.2)
        self.play(GrowFromCenter(circle), run_time=1)
        
        # Simple dots around circle
        dots = VGroup()
        for i in range(6):
            angle = i * PI / 3
            dot = Dot(color=YELLOW, radius=0.1)
            dot.move_to(1.5 * np.array([np.cos(angle), np.sin(angle), 0]))
            dots.add(dot)
        
        self.play(*[GrowFromCenter(d) for d in dots], run_time=0.8)
        self.play(Rotate(dots, angle=PI, about_point=ORIGIN), run_time=2)
        
        # Simple pulse
        self.play(circle.animate.scale(1.1), run_time=0.3)
        self.play(circle.animate.scale(1/1.1), run_time=0.3)
        
        self.wait(0.5)
        
        # Clean exit
        self.play(FadeOut(title), FadeOut(circle), FadeOut(dots), run_time=0.8)
        
        # Branding
        brand = Text("Animation by Xe-Bot", font_size=28, color=BLUE)
        self.play(Write(brand), run_time=0.5)
        self.wait(1)
        self.play(FadeOut(brand), run_time=0.5)
'''
        try:
            temp_dir = Path(tempfile.mkdtemp())
            script_path = temp_dir / "fallback.py"
            script_path.write_text(fallback_code, encoding='utf-8')
            
            cmd = [
                "manim", "-ql", "--fps", "30",
                "-o", f"{safe_scene_name}.mp4",
                "--media_dir", str(media_dir),
                str(script_path), safe_scene_name
            ]
            
            console.print(f"[dim]Running fallback: {' '.join(cmd[:5])}...[/dim]")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=90, cwd=temp_dir)
            
            if result.returncode == 0:
                # Find the output
                for mp4 in media_dir.rglob("*.mp4"):
                    if safe_scene_name in mp4.stem and "partial" not in str(mp4):
                        console.print(f"[green]Fallback animation created: {mp4.name}[/green]")
                        shutil.rmtree(temp_dir, ignore_errors=True)
                        return mp4
            else:
                console.print(f"[red]Fallback failed: {result.stderr[:200] if result.stderr else 'Unknown error'}[/red]")
            
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None
        except Exception as e:
            console.print(f"[red]Fallback exception: {str(e)[:100]}[/red]")
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
    
    def create_quantum_animation(
        self,
        segment: Dict[str, Any],
        quantum_type: str = "auto"
    ) -> str:
        """
        Create animation for quantum physics topics.
        Automatically detects the type of quantum concept and generates appropriate visualization.
        
        Args:
            segment: Segment data with content, topic, concepts
            quantum_type: Type of quantum animation (auto, entanglement, superposition, 
                         tunneling, interference, decoherence, measurement, teleportation)
        
        Returns:
            Manim code string
        """
        from src.animation.quantum_templates import quantum_templates
        
        topic = segment.get('topic', 'Quantum Concept')
        content = segment.get('content', '').lower()
        concepts = segment.get('key_concepts', [])
        concepts_lower = ' '.join(concepts).lower()
        
        # Auto-detect quantum type from content
        if quantum_type == "auto":
            if any(kw in content or kw in concepts_lower for kw in ['entangle', 'epr', 'bell', 'non-local', 'correlated']):
                quantum_type = "entanglement"
            elif any(kw in content or kw in concepts_lower for kw in ['superposition', 'both states', 'simultaneously']):
                quantum_type = "superposition"
            elif any(kw in content or kw in concepts_lower for kw in ['tunnel', 'barrier', 'forbidden']):
                quantum_type = "tunneling"
            elif any(kw in content or kw in concepts_lower for kw in ['interference', 'double.slit', 'fringe']):
                quantum_type = "interference"
            elif any(kw in content or kw in concepts_lower for kw in ['decoherence', 'environment', 'classical limit']):
                quantum_type = "decoherence"
            elif any(kw in content or kw in concepts_lower for kw in ['measurement', 'collapse', 'observer']):
                quantum_type = "measurement"
            elif any(kw in content or kw in concepts_lower for kw in ['teleport', 'transfer']):
                quantum_type = "teleportation"
            elif any(kw in content or kw in concepts_lower for kw in ['wave function', 'psi', 'schrodinger']):
                quantum_type = "wave_function"
            else:
                # Default to entanglement for generic quantum topics
                quantum_type = "entanglement"
        
        # Get the appropriate template
        template_map = {
            "entanglement": lambda t: quantum_templates.quantum_entanglement(t),
            "superposition": lambda t: quantum_templates.superposition_state(t),
            "tunneling": lambda t: quantum_templates.quantum_tunneling(t),
            "interference": lambda t: quantum_templates.quantum_interference(t),
            "decoherence": lambda t: quantum_templates.quantum_decoherence(t),
            "measurement": lambda t: quantum_templates.quantum_measurement(t),
            "teleportation": lambda t: quantum_templates.quantum_teleportation(t),
            "wave_function": lambda t: quantum_templates.wave_function_collapse(t),
            "bell": lambda t: quantum_templates.bell_inequality(t),
            "epr": lambda t: quantum_templates.epr_paradox(t),
        }
        
        template_func = template_map.get(quantum_type, template_map["entanglement"])
        
        # Generate the code using the template
        code = template_func(topic)
        
        console.print(f"[cyan]Generated {quantum_type} quantum animation for: {topic}[/cyan]")
        
        return code
    
    def is_quantum_topic(self, segment: Dict[str, Any]) -> bool:
        """
        Detect if a segment is about quantum physics.
        
        Args:
            segment: Segment data
            
        Returns:
            True if quantum-related topic
        """
        quantum_keywords = [
            'quantum', 'entangle', 'superposition', 'qubit', 'wave function',
            'collapse', 'measurement', 'decoherence', 'tunneling', 'interference',
            'bell', 'epr', 'teleportation', 'spin', 'coherence', 'bloch',
            'schrodinger', 'heisenberg', 'uncertainty', 'observable', 'eigenstate',
            'hilbert', 'hermitian', 'unitary', 'density matrix', 'mixed state',
            'pure state', 'fidelity', 'tomography', 'error correction',
            'non-local', 'spooky action', 'hidden variable'
        ]
        
        content = segment.get('content', '').lower()
        topic = segment.get('topic', '').lower()
        concepts = ' '.join(segment.get('key_concepts', [])).lower()
        
        search_text = f"{content} {topic} {concepts}"
        
        return any(kw in search_text for kw in quantum_keywords)


# Global animation generator instance
animation_generator = ManimAnimationGenerator()

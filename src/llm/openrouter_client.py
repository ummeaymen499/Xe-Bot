"""
OpenRouter API Client for Xe-Bot
Handles all LLM interactions via OpenRouter
"""
import httpx
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential
from rich.console import Console

from src.config import config

console = Console()


@dataclass
class LLMResponse:
    """Structured LLM response"""
    content: str
    model: str
    usage: Dict[str, int]
    raw_response: Dict[str, Any]


class OpenRouterClient:
    """
    Client for interacting with OpenRouter API
    Supports multiple models through a unified interface
    """
    
    def __init__(self):
        self.api_key = config.openrouter.api_key
        self.base_url = config.openrouter.base_url
        self.default_model = config.openrouter.default_model
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://xe-bot.local",
            "X-Title": "Xe-Bot Research Animation Generator"
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        json_mode: bool = False
    ) -> LLMResponse:
        """
        Send a chat completion request to OpenRouter
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to config default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            json_mode: Whether to request JSON output
        
        Returns:
            LLMResponse with content and metadata
        """
        model = model or self.default_model
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as e:
                console.print(f"[red]OpenRouter API Error: {e.response.status_code}[/red]")
                console.print(f"[red]Response: {e.response.text}[/red]")
                console.print(f"[yellow]API Key (first 20 chars): {self.api_key[:20]}...[/yellow]")
                raise
        
        return LLMResponse(
            content=data["choices"][0]["message"]["content"],
            model=data.get("model", model),
            usage=data.get("usage", {}),
            raw_response=data
        )
    
    async def extract_introduction(self, paper_text: str) -> str:
        """
        Extract the introduction section from a research paper
        
        Args:
            paper_text: Full text of the research paper
        
        Returns:
            Extracted introduction text
        """
        messages = [
            {
                "role": "system",
                "content": """You are an expert at analyzing academic research papers. 
Your task is to extract ONLY the Introduction section from the paper.

Rules:
1. Extract the complete Introduction section, including all paragraphs
2. Do not include the Abstract
3. Do not include any section that comes after Introduction (like Methods, Related Work, etc.)
4. If the introduction has subsections, include them
5. Return ONLY the introduction text, nothing else
6. If you cannot identify a clear Introduction section, extract the first substantive section that introduces the topic"""
            },
            {
                "role": "user",
                "content": f"Extract the Introduction section from this research paper:\n\n{paper_text[:15000]}"
            }
        ]
        
        response = await self.chat_completion(messages, temperature=0.3)
        return response.content
    
    async def segment_introduction(self, introduction: str) -> List[Dict[str, Any]]:
        """
        Segment the introduction into logical parts with topic classification
        
        Args:
            introduction: The introduction text
        
        Returns:
            List of segments with topic labels and key concepts (3-5 segments)
        """
        messages = [
            {
                "role": "system",
                "content": """You are an expert at analyzing and segmenting academic text.
Your task is to break down a research paper introduction into logical segments.

=== CRITICAL REQUIREMENT ===
You MUST create between 3 and 5 segments (inclusive). No fewer than 3, no more than 5.
Keep it concise - combine related concepts to stay within 5 segments.

Suggested segment structure:
1. Background/Context (what field/area this is about)
2. Problem Statement (what problem exists and why it matters)
3. Proposed Approach (what this paper does)
4. Key Contributions (main contributions/innovations)
5. Summary/Outline (optional - brief overview)

For each segment, provide:
1. content: The actual text of the segment (keep it brief - 2-3 sentences max)
2. topic: A short descriptive title for the segment (2-4 words)
3. topic_category: One of [background, problem_statement, motivation, related_work, approach, contributions, outline]
4. key_concepts: List of 2-3 key terms/concepts mentioned
5. animation_hints: Brief suggestion for visualization (1 sentence)

Return a JSON object with a "segments" array containing 3-5 segments in order."""
            },
            {
                "role": "user",
                "content": f"Segment this introduction into 3-5 logical parts (keep it concise):\n\n{introduction}"
            }
        ]
        
        response = await self.chat_completion(messages, temperature=0.3, json_mode=True)
        
        try:
            result = json.loads(response.content)
            segments = result.get("segments", [])
            
            # Validate and enforce 4-7 segments
            segments = self._validate_segment_count(segments, introduction)
            
            return segments
        except json.JSONDecodeError:
            console.print("[yellow]Warning: Could not parse JSON response, using fallback[/yellow]")
            return self._create_fallback_segments(introduction)
    
    def _validate_segment_count(self, segments: List[Dict[str, Any]], introduction: str) -> List[Dict[str, Any]]:
        """
        Ensure segment count is between 3 and 5.
        If too few, split or add segments. If too many, merge.
        """
        MIN_SEGMENTS = 3
        MAX_SEGMENTS = 5
        
        if len(segments) < MIN_SEGMENTS:
            console.print(f"[yellow]Warning: Only {len(segments)} segments, creating fallback segments[/yellow]")
            return self._create_fallback_segments(introduction, existing_segments=segments)
        
        if len(segments) > MAX_SEGMENTS:
            console.print(f"[yellow]Warning: {len(segments)} segments exceeds max of {MAX_SEGMENTS}, trimming[/yellow]")
            # Keep only the first MAX_SEGMENTS
            segments = segments[:6] + [segments[-1]] if len(segments) > 7 else segments[:MAX_SEGMENTS]
        
        return segments
    
    def _create_fallback_segments(self, introduction: str, existing_segments: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Create fallback segments to ensure minimum of 4 segments.
        """
        if existing_segments is None:
            existing_segments = []
        
        # Default segment templates
        default_segments = [
            {
                "content": "Background and context of the research area.",
                "topic": "Background",
                "topic_category": "background",
                "key_concepts": ["research area", "context"],
                "animation_hints": {"type": "overview", "style": "expanding circles"}
            },
            {
                "content": "The problem this research addresses.",
                "topic": "Problem Statement",
                "topic_category": "problem_statement",
                "key_concepts": ["challenge", "limitation"],
                "animation_hints": {"type": "problem", "style": "highlight issues"}
            },
            {
                "content": "Why this problem is important to solve.",
                "topic": "Motivation",
                "topic_category": "motivation",
                "key_concepts": ["importance", "impact"],
                "animation_hints": {"type": "motivation", "style": "cause-effect"}
            },
            {
                "content": "The approach taken to address the problem.",
                "topic": "Approach",
                "topic_category": "approach",
                "key_concepts": ["method", "solution"],
                "animation_hints": {"type": "solution", "style": "flowchart"}
            }
        ]
        
        # If we have some existing segments, use them and fill in the rest
        if existing_segments:
            result = list(existing_segments)
            # Add from defaults until we have at least 4
            for default_seg in default_segments:
                if len(result) >= 4:
                    break
                # Check if this category already exists
                existing_categories = [s.get("topic_category") for s in result]
                if default_seg["topic_category"] not in existing_categories:
                    result.append(default_seg)
            return result
        
        # No existing segments, use defaults with actual introduction content
        # Split introduction into roughly equal parts
        words = introduction.split()
        total_words = len(words)
        chunk_size = max(total_words // 4, 50)  # At least 50 words per chunk
        
        result = []
        for i, default_seg in enumerate(default_segments):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, total_words)
            if start < total_words:
                content = ' '.join(words[start:end])
                seg = default_seg.copy()
                seg["content"] = content if content else default_seg["content"]
                result.append(seg)
        
        return result if len(result) >= 4 else default_segments[:4]
    
    def _old_fallback(self, introduction):
        return [{
                "content": introduction,
                "topic": "Introduction",
                "topic_category": "background",
                "key_concepts": [],
                "animation_hints": {}
            }]
    
    async def generate_animation_code(
        self,
        segment: Dict[str, Any],
        animation_style: str = "explanatory"
    ) -> str:
        """
        Generate Manim animation code for a segment
        
        Args:
            segment: Segment data with content, topic, and concepts
            animation_style: Style of animation (explanatory, dramatic, minimal)
        
        Returns:
            Valid Manim Python code
        """
        topic_category = segment.get('topic_category', 'general')
        
        # Choose visualization type based on category - ENHANCED for more graphics
        visualization_hints = {
            'background': '''ANIMATED CONTEXT SCENE:
- Create a VISUAL METAPHOR (e.g., gears for systems, waves for signals, network for connections)
- Use ICONS with Circle/Square shapes with small symbols inside
- Show TIMELINE with animated dots moving along a line
- Add PULSING effects with .animate.scale() for emphasis''',
            'problem_statement': '''VISUAL PROBLEM REPRESENTATION:
- Show BEFORE/AFTER split screen with Line separator
- Use RED X marks (Cross shape) over broken elements
- Create CRACKS or GAPS between shapes
- Animate a BROKEN CHAIN or MISSING PUZZLE piece
- Use color transition from GREEN to RED for degradation''',
            'motivation': '''CAUSE-EFFECT ANIMATION:
- Create DOMINO EFFECT with falling rectangles
- Show RIPPLE animation with expanding circles
- Use GROWTH animation (small to large) for impact
- Create BRANCHING tree showing consequences
- Animate VALUE METER going up/down''',
            'related_work': '''COMPARISON VISUALIZATION:
- Create SIDE-BY-SIDE boxes with VS in middle
- Use RADAR/SPIDER chart with polygons
- Show FEATURE MATRIX with checkmarks (green) and X (red)
- Animate SCALE/BALANCE showing trade-offs
- Create EVOLUTION timeline showing progression''',
            'approach': '''ARCHITECTURAL FLOWCHART:
- Create PIPELINE with boxes and animated arrows
- Show DATA FLOW with moving dots along paths
- Use LAYERED ARCHITECTURE (stacked rectangles)
- Create CIRCULAR PROCESS with rotating arrows
- Animate STEP-BY-STEP highlighting (glow effect)''',
            'contributions': '''ACHIEVEMENT SHOWCASE:
- Use NUMBERED BADGES (circles with numbers)
- Create TROPHY/STAR icons for key points
- Show CHECKMARK animations appearing
- Use SPOTLIGHT effect (bright circle) on each point
- Create BUILDING BLOCKS stacking animation''',
            'outline': '''ROADMAP VISUALIZATION:
- Create JOURNEY PATH with milestones
- Show CHAPTER ICONS connected by curved lines
- Use MAP-STYLE layout with location dots
- Animate PROGRESS BAR filling up
- Create BOOK/SCROLL unfurling effect''',
            'general': '''CONCEPT VISUALIZATION:
- Create MIND MAP with central node and branches
- Use ICON GRID with labeled symbols
- Show RELATIONSHIP WEB with connecting lines
- Create INFOGRAPHIC-STYLE layout
- Animate REVEAL sequence with staggered FadeIn'''
        }
        
        viz_hint = visualization_hints.get(topic_category, visualization_hints['general'])
        
        system_prompt = f'''You are an expert Manim animator creating CINEMATIC VISUAL EXPLANATIONS.

=== CORE PHILOSOPHY ===
Create VISUALLY STUNNING animations with MOTION GRAPHICS!
You are making a VISUAL STORY, not a PowerPoint. Use shapes, colors, motion!

=== CRITICAL: NO TEXT OVERLAP ===
EVERY section MUST start fresh. Before ANY new content:
  self.play(*[FadeOut(m) for m in self.mobjects])

=== VISUALIZATION STYLE FOR THIS SEGMENT ===
{viz_hint}

=== GRAPHICAL ELEMENTS TO USE ===
SHAPES: Circle, Square, Rectangle, RoundedRectangle, Triangle, Star, Arrow, Line, Arc, Polygon
GROUPS: VGroup to combine shapes, .arrange() for layout
EFFECTS: 
  - .animate.scale(1.2) for pulse/emphasis
  - .animate.set_color(NEW_COLOR) for color transitions
  - .animate.shift(direction) for movement
  - FadeIn(mob, shift=UP) for directional fades
  - GrowFromCenter(shape) for dramatic reveals
  - Rotating(mob) for spinning effects
  - Flash(point) for attention

=== ADVANCED TECHNIQUES ===
1. PARTICLE EFFECTS: Create VGroup of small dots, animate them moving
2. GLOW EFFECT: Create larger blurred shape behind main shape
3. PROGRESS BARS: Rectangle with another inside that grows
4. PULSING: Use .animate.scale(1.1) then .animate.scale(1) in loop
5. CONNECTIONS: Use CurvedArrow or bezier paths
6. ICONS: Combine basic shapes (circle + triangle = play button)
7. GRADIENTS: Use linear_gradient or fill_opacity variations

=== SHAPE RECIPES ===
# Neural Network Node
node = Circle(radius=0.3, color=BLUE, fill_opacity=0.8)

# Data Packet (moving dot)
packet = Dot(color=YELLOW).scale(1.5)

# Icon Box
icon = VGroup(
    RoundedRectangle(width=1.5, height=1.5, corner_radius=0.2, fill_opacity=0.2, color=GREEN),
    Star(n=5, color=YELLOW, fill_opacity=1).scale(0.3)
)

# Progress Bar
bg = RoundedRectangle(width=4, height=0.3, corner_radius=0.1, color=GRAY, fill_opacity=0.3)
fill = RoundedRectangle(width=0.1, height=0.25, corner_radius=0.1, color=GREEN, fill_opacity=1)
fill.align_to(bg, LEFT)
# Animate: self.play(fill.animate.stretch_to_fit_width(3.8))

=== ABSOLUTE REQUIREMENTS ===
1. Use ONLY: from manim import *
2. Scene class as base
3. NEVER use MathTex, Tex, or LaTeX - ONLY Text()
4. ASCII characters only (no unicode bullets, arrows)
5. Duration: 15-30 seconds
6. Minimum 5 animated shapes/objects (not counting text)
7. Use at least 3 different colors
8. Include at least ONE motion effect (scale, rotate, shift)

=== GOLDEN RULES ===
1. CREATE shapes first
2. POSITION with .shift() or .move_to()
3. CREATE labels AFTER positioning, then label.move_to(shape)
4. CREATE arrows AFTER positioning shapes
5. ANIMATE
6. FADEOUT everything: self.play(*[FadeOut(m) for m in self.mobjects])

=== LAYOUT ===
- Title: .to_edge(UP, buff=0.5), font_size=36
- Shapes: width 2-3, height 1-1.5
- Positions: LEFT*4, ORIGIN, RIGHT*4 for 3 items
- Labels inside shapes: font_size=18-20
- Colors: Use RED, BLUE, GREEN, ORANGE, PURPLE, YELLOW

=== EXAMPLE PATTERN ===
from manim import *

class SegmentAnimation(Scene):
    def construct(self):
        # Title
        title = Text("Topic Name", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        # Create shapes FIRST
        box1 = RoundedRectangle(width=2.5, height=1, corner_radius=0.1, color=RED, fill_opacity=0.3)
        box2 = RoundedRectangle(width=2.5, height=1, corner_radius=0.1, color=GREEN, fill_opacity=0.3)
        
        # Position SECOND
        box1.shift(LEFT*3 + DOWN*0.5)
        box2.shift(RIGHT*3 + DOWN*0.5)
        
        # Labels THIRD (after positioning)
        lbl1 = Text("Input", font_size=20)
        lbl1.move_to(box1)
        lbl2 = Text("Output", font_size=20)
        lbl2.move_to(box2)
        
        # Arrows FOURTH (after positioning)
        arrow = Arrow(box1.get_right(), box2.get_left(), buff=0.1, color=WHITE)
        
        # Animate
        self.play(Create(box1), Write(lbl1))
        self.play(GrowArrow(arrow))
        self.play(Create(box2), Write(lbl2))
        self.wait(2)
        
        # ALWAYS clear before next section or branding
        self.play(*[FadeOut(m) for m in self.mobjects])
        
        # Branding
        brand = Text("Animation by Xe-Bot", font_size=36, color=BLUE)
        self.play(FadeIn(brand))
        self.wait(2)
        self.play(FadeOut(brand))

Return ONLY Python code. No markdown, no explanations.'''
        
        # Extract first line of viz_hint for the required visual type
        viz_type = viz_hint.split('\n')[0].split(':')[0].strip() if '\n' in viz_hint else viz_hint.split(':')[0].strip()
        
        user_prompt = f'''Create a CINEMATIC, GRAPHICALLY RICH animation for this research concept.

Topic: {segment.get('topic', 'Research Concept')}
Category: {topic_category}
Key Concepts: {', '.join(segment.get('key_concepts', []))}

Context (use to INSPIRE your visuals, do NOT display as text):
{segment.get('content', '')[:600]}

=== YOUR MISSION ===
Create a {viz_type} with these REQUIREMENTS:
1. At least 5-8 animated SHAPES (circles, boxes, arrows, lines, stars)
2. MOTION: Objects should move, scale, pulse, or transform
3. COLOR TRANSITIONS: Use .animate.set_color() for emphasis
4. LAYERED COMPOSITION: Background elements + foreground action
5. SHORT labels only (1-3 words max per label)
6. SMOOTH FLOW: Each element leads to the next

=== STRUCTURE ===
1. Title appears (with subtle decoration)
2. Main visual builds piece by piece
3. Key elements PULSE or GLOW for emphasis
4. Optional: Data/info flows through the diagram
5. Smooth fadeout
6. Xe-Bot branding

Make it VISUALLY IMPRESSIVE - like a professional motion graphic!

Generate the Manim code:'''
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.chat_completion(messages, temperature=0.5, max_tokens=4096)
        
        # Clean up the response - remove markdown code blocks if present
        code = self._clean_code_response(response.content)
        
        return code

    def _clean_code_response(self, code: str) -> str:
        """Clean LLM response to extract valid Python code"""
        import re
        
        # Remove markdown code blocks
        code = code.strip()
        
        # Handle ```python ... ``` blocks
        if "```python" in code:
            match = re.search(r'```python\s*\n(.*?)```', code, re.DOTALL)
            if match:
                code = match.group(1)
        elif "```" in code:
            match = re.search(r'```\s*\n(.*?)```', code, re.DOTALL)
            if match:
                code = match.group(1)
        
        # Remove any leading/trailing ``` that might remain
        code = re.sub(r'^```\w*\n?', '', code)
        code = re.sub(r'\n?```$', '', code)
        
        # Replace MathTex/Tex with Text to avoid LaTeX dependency
        code = re.sub(r'MathTex\s*\(', 'Text(', code)
        code = re.sub(r'Tex\s*\(', 'Text(', code)
        
        # Remove any LaTeX-specific formatting in strings
        code = code.replace('\\frac', '/')
        code = code.replace('\\sum', 'sum')
        code = code.replace('\\int', 'integral')
        code = code.replace('\\alpha', 'alpha')
        code = code.replace('\\beta', 'beta')
        code = code.replace('\\gamma', 'gamma')
        
        return code.strip()
    
    async def generate_full_animation_code(
        self,
        title: str,
        segments: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a complete Manim animation for all segments combined
        
        Args:
            title: Paper title
            segments: List of all segments
        
        Returns:
            Complete Manim code for full animation
        """
        # Create a summary of all segments with visualization hints
        visualization_hints = {
            'background': 'ANIMATED SCENE with moving particles, timeline, or interconnected nodes',
            'problem_statement': 'VISUAL PROBLEM: broken chain, X marks, gaps, RED highlights',
            'motivation': 'IMPACT DIAGRAM: domino effect, ripples, growth animation',
            'related_work': 'COMPARISON: side-by-side boxes with VS, checkmarks/X marks',
            'approach': 'PIPELINE FLOWCHART: boxes with animated data flow (moving dots)',
            'contributions': 'ACHIEVEMENT SHOWCASE: numbered badges, stars, checkmark animations',
            'outline': 'ROADMAP: connected milestones with curved paths',
            'general': 'CONCEPT WEB: central node with radiating connections'
        }
        
        segment_summary = "\n\n".join([
            f"SEGMENT {i+1}: {s.get('topic', 'Topic')}\n"
            f"Category: {s.get('topic_category', 'general')}\n"
            f"Visualization: {visualization_hints.get(s.get('topic_category', 'general'), 'concept map')}\n"
            f"Key Concepts: {', '.join(s.get('key_concepts', []))}"
            for i, s in enumerate(segments[:5])  # Limit to 5 segments
        ])
        
        system_prompt = f'''You are an expert Manim animator creating CINEMATIC, GRAPHICALLY RICH animations.

=== CORE PHILOSOPHY ===
Create MOTION GRAPHICS like a professional video! Use shapes, colors, animations!
Each segment needs VISUAL IMPACT. Viewers should be IMPRESSED and UNDERSTAND.

=== CRITICAL: PREVENT TEXT OVERLAP ===
Before EVERY new segment:
  self.play(*[FadeOut(m) for m in self.mobjects])

This is MANDATORY to clear the screen between sections.

=== GRAPHICAL TECHNIQUES TO USE ===
1. PARTICLE EFFECTS: Background dots that float/pulse
2. ANIMATED CONNECTIONS: Arrows that grow, dots that flow along paths
3. PULSING EMPHASIS: shape.animate.scale(1.2) then back to 1
4. COLOR TRANSITIONS: shape.animate.set_color(NEW_COLOR)
5. STAGGERED REVEALS: Elements appear one by one with delays
6. LAYERED COMPOSITION: Background decorations + main content

=== STRUCTURE ===
1. TITLE SLIDE: Paper title with animated decorative lines
2. Each segment gets:
   - Segment title (2 words max) with underline animation
   - ONE rich diagram visualization (minimum 5 shapes)
   - Motion/pulse effects on key elements
   - Clear screen before next
3. BRANDING: Animated "Animation by Xe-Bot"

=== VISUALIZATION TYPES ===
- background -> Floating particles + context nodes
- problem_statement -> Visual breakdown with RED X marks, cracks
- approach -> Pipeline with ANIMATED data flow (moving dots)
- contributions -> Trophy/star icons with glow effects
- For ML/AI -> Neural network with signal propagation animation

=== REQUIREMENTS ===
1. from manim import *
2. Single Scene class
3. ONLY Text() - NO MathTex, Tex, LaTeX
4. ASCII only
5. Duration: 45-90 seconds total
6. MINIMUM 5 shapes per segment (not counting text)
7. At least ONE motion effect per segment (scale, shift, color change)

=== ORDER OF OPERATIONS (EVERY SEGMENT) ===
1. FadeOut all existing: self.play(*[FadeOut(m) for m in self.mobjects])
2. Create segment title with decoration
3. Create shapes (circles, boxes, stars, lines)
4. Position shapes with .shift()
5. Add MOTION (pulsing, color change, movement)
6. Create labels AFTER positioning
7. Create arrows with GrowArrow
8. Wait 2-3 seconds
9. FadeOut before next segment

=== LAYOUT ===
- Title: .to_edge(UP, buff=0.5), font_size=36
- Shapes: varied sizes for visual interest
- Positions: LEFT*3, ORIGIN, RIGHT*3
- Labels: font_size=18-20, 1-3 words only
- Frame: x=-7 to 7, y=-4 to 4

=== ADVANCED EXAMPLE ===
# Background particle effect
particles = VGroup()
for _ in range(15):
    p = Dot(radius=0.05, color=BLUE, fill_opacity=0.3)
    p.move_to([np.random.uniform(-6, 6), np.random.uniform(-3, 3), 0])
    particles.add(p)
self.add(particles)
self.play(*[p.animate.shift(UP*0.3) for p in particles], run_time=2)

# Pulsing node emphasis
node = Circle(radius=0.5, color=GREEN, fill_opacity=0.8)
self.play(node.animate.scale(1.3), run_time=0.3)
self.play(node.animate.scale(1/1.3), run_time=0.3)

# Animated data flow
path = Line(LEFT*3, RIGHT*3)
dot = Dot(color=YELLOW).move_to(path.get_start())
self.play(MoveAlongPath(dot, path), run_time=2)
layers = []
for i, (size, color) in enumerate([(3, RED), (4, BLUE), (2, GREEN)]):
    layer = VGroup()
    for j in range(size):
        node = Circle(radius=0.2, color=color, fill_opacity=0.6)
        node.move_to([i*3 - 3, j*0.8 - size*0.4, 0])
        layer.add(node)
    layers.append(layer)
    self.play(*[GrowFromCenter(n) for n in layer])

=== EXAMPLE STRUCTURE ===
from manim import *

class PaperAnimation(Scene):
    def construct(self):
        # Title slide
        title = Text("Paper Title", font_size=40, color=BLUE)
        self.play(Write(title))
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])
        
        # Segment 1: Background (context diagram)
        seg1_title = Text("Background", font_size=36, color=GREEN)
        seg1_title.to_edge(UP, buff=0.5)
        self.play(Write(seg1_title))
        
        # Create positioned shapes for diagram
        box1 = RoundedRectangle(width=2.5, height=1, corner_radius=0.1, color=RED, fill_opacity=0.3)
        box2 = RoundedRectangle(width=2.5, height=1, corner_radius=0.1, color=GREEN, fill_opacity=0.3)
        box1.shift(LEFT*3)
        box2.shift(RIGHT*3)
        
        lbl1 = Text("Concept A", font_size=18)
        lbl1.move_to(box1)
        lbl2 = Text("Concept B", font_size=18)
        lbl2.move_to(box2)
        
        arrow = Arrow(box1.get_right(), box2.get_left(), buff=0.1, color=WHITE)
        
        self.play(Create(box1), Write(lbl1))
        self.play(GrowArrow(arrow))
        self.play(Create(box2), Write(lbl2))
        self.wait(2)
        
        # CLEAR before next segment
        self.play(*[FadeOut(m) for m in self.mobjects])
        
        # ... more segments ...
        
        # Branding
        brand = Text("Animation by Xe-Bot", font_size=40, color=BLUE)
        self.play(FadeIn(brand))
        self.wait(2)
        self.play(FadeOut(brand))

Return ONLY Python code. No markdown, no explanations.'''
        
        user_prompt = f'''Create a CINEMATIC, GRAPHICALLY RICH Manim animation for this research paper.

Paper Title: {title[:80]}

SEGMENTS TO VISUALIZE:
{segment_summary}

=== YOUR MISSION ===
Create a VISUALLY STUNNING animation that looks like a professional motion graphic!

MANDATORY REQUIREMENTS:
1. FadeOut ALL before each new segment: self.play(*[FadeOut(m) for m in self.mobjects])
2. Each segment: MINIMUM 5 animated shapes (circles, boxes, arrows, stars)
3. Include MOTION EFFECTS: pulsing (.animate.scale), color transitions, moving elements
4. Add VISUAL FLAIR: background particles, decorative lines, glows
5. Labels: 1-3 words MAXIMUM
6. Position shapes FIRST, then create labels
7. End with animated "Animation by Xe-Bot" branding

MAKE IT IMPRESSIVE - like a professional explainer video!

Generate the complete Manim code:'''
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.chat_completion(messages, temperature=0.5, max_tokens=8000)
        
        code = self._clean_code_response(response.content)
        
        return code


# Global client instance
openrouter_client = OpenRouterClient()

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
        system_prompt = (
            "You are an expert Manim animator creating VISUAL EXPLANATIONS of concepts.\n\n"
            "=== CORE PHILOSOPHY ===\n"
            "VISUALIZE concepts through animations and diagrams - NOT walls of text!\n"
            "- Show HOW things work with moving shapes, arrows, and transformations\n"
            "- Use diagrams, flowcharts, and visual metaphors to explain ideas\n"
            "- Minimal text: only short labels (1-3 words) inside shapes\n"
            "- Let the ANIMATION tell the story, not paragraphs of text\n\n"
            "=== ABSOLUTE REQUIREMENTS ===\n"
            "1. Generate ONLY valid Manim Community Edition Python code\n"
            "2. Use Scene class as base\n"
            "3. Include: from manim import *\n"
            "4. NEVER use MathTex, Tex, or LaTeX - ONLY use Text()\n"
            "5. Use only ASCII characters\n"
            "6. Duration: 15-40 seconds\n\n"
            "=== VISUALIZATION TECHNIQUES ===\n"
            "Use these to explain concepts visually:\n"
            "- FLOWCHARTS: boxes with arrows showing process/data flow\n"
            "- DIAGRAMS: shapes representing components and their relationships\n"
            "- ANIMATIONS: Transform(), MoveToTarget(), GrowArrow() to show change\n"
            "- COLOR CODING: different colors for different concepts\n"
            "- HIGHLIGHTING: Indicate() or Circumscribe() to draw attention\n"
            "- GROWTH: shapes growing/shrinking to show importance/scale\n"
            "- CONNECTIONS: arrows/lines showing relationships\n"
            "- LAYERING: build up complex diagrams piece by piece\n\n"
            "=== WHAT TO AVOID ===\n"
            "- NO long sentences or paragraphs of text\n"
            "- NO bullet point lists displayed as text\n"
            "- NO text dumps - if you need to explain, use a diagram\n"
            "- Labels should be 1-3 words MAX inside shapes\n\n"
            "=== GOLDEN RULE: ORDER OF OPERATIONS ===\n"
            "1. CREATE all shapes\n"
            "2. POSITION shapes using .shift() or .move_to()\n"
            "3. CREATE labels and use .move_to(shape) to place inside\n"
            "4. CREATE arrows using positioned shapes' .get_right()/.get_left()\n"
            "5. ANIMATE everything\n"
            "6. FADEOUT everything before next section\n\n"
            "=== ARROW POSITIONING ===\n"
            "WRONG: Create arrow before positioning shapes (arrow points to origin)\n"
            "CORRECT: Position shapes FIRST, then create arrow\n"
            "Example:\n"
            "  box1 = Rectangle(width=2, height=1, color=BLUE, fill_opacity=0.3)\n"
            "  box2 = Rectangle(width=2, height=1, color=GREEN, fill_opacity=0.3)\n"
            "  box1.shift(LEFT*3)  # Position FIRST\n"
            "  box2.shift(RIGHT*3)\n"
            "  arrow = Arrow(box1.get_right(), box2.get_left(), buff=0.1)  # THEN arrow\n\n"
            "=== LABEL POSITIONING ===\n"
            "WRONG: label.move_to(box) before box is positioned\n"
            "CORRECT: Position box first, then label.move_to(box)\n"
            "Example:\n"
            "  box.shift(LEFT*3)  # Position FIRST\n"
            "  label = Text('Name', font_size=20)\n"
            "  label.move_to(box)  # NOW label inside box\n\n"
            "=== NO TEXT OVERLAP ===\n"
            "EVERY section MUST end with:\n"
            "  self.play(*[FadeOut(m) for m in self.mobjects])\n\n"
            "=== SCREEN LAYOUT ===\n"
            "- Frame: x from -7 to 7, y from -4 to 4\n"
            "- Title: .to_edge(UP, buff=0.5)\n"
            "- Main content: shift DOWN*0.5 to leave room for title\n"
            "- Shapes: width 2-3, height 1-1.5\n"
            "- Spacing between shapes: 3-4 units\n"
            "- Labels: font_size 18-22\n\n"
            "=== COMPLETE FLOWCHART EXAMPLE ===\n"
            "from manim import *\n\n"
            "class FlowchartScene(Scene):\n"
            "    def construct(self):\n"
            "        title = Text('Process Flow', font_size=40, color=BLUE)\n"
            "        title.to_edge(UP, buff=0.5)\n"
            "        self.play(Write(title))\n\n"
            "        # Create shapes\n"
            "        box1 = RoundedRectangle(width=2.5, height=1, corner_radius=0.1, color=RED, fill_opacity=0.3)\n"
            "        box2 = RoundedRectangle(width=2.5, height=1, corner_radius=0.1, color=BLUE, fill_opacity=0.3)\n"
            "        box3 = RoundedRectangle(width=2.5, height=1, corner_radius=0.1, color=GREEN, fill_opacity=0.3)\n\n"
            "        # Position shapes FIRST\n"
            "        box1.shift(LEFT*4)\n"
            "        # box2 at center\n"
            "        box3.shift(RIGHT*4)\n\n"
            "        # Labels AFTER positioning\n"
            "        label1 = Text('Input', font_size=20)\n"
            "        label1.move_to(box1)\n"
            "        label2 = Text('Process', font_size=20)\n"
            "        label2.move_to(box2)\n"
            "        label3 = Text('Output', font_size=20)\n"
            "        label3.move_to(box3)\n\n"
            "        # Arrows AFTER positioning\n"
            "        arrow1 = Arrow(box1.get_right(), box2.get_left(), buff=0.1, color=WHITE)\n"
            "        arrow2 = Arrow(box2.get_right(), box3.get_left(), buff=0.1, color=WHITE)\n\n"
            "        # Animate\n"
            "        self.play(Create(box1), Write(label1))\n"
            "        self.play(GrowArrow(arrow1))\n"
            "        self.play(Create(box2), Write(label2))\n"
            "        self.play(GrowArrow(arrow2))\n"
            "        self.play(Create(box3), Write(label3))\n"
            "        self.wait(2)\n\n"
            "        # Clear screen\n"
            "        self.play(*[FadeOut(m) for m in self.mobjects])\n\n"
            "        # Branding\n"
            "        brand = Text('Animation by Xe-Bot', font_size=36, color=BLUE)\n"
            "        self.play(FadeIn(brand))\n"
            "        self.wait(2)\n"
            "        self.play(FadeOut(brand))\n\n"
            "Return ONLY Python code. No markdown, no explanations."
        )
        
        user_prompt = (
            f"Create a VISUAL animation that EXPLAINS this concept through diagrams and motion.\n\n"
            f"GOAL: Make viewers UNDERSTAND the concept by SEEING it, not reading about it.\n\n"
            f"VISUALIZATION IDEAS for this topic:\n"
            f"- If it's a PROCESS: show flowchart with arrows between steps\n"
            f"- If it's COMPONENTS: show boxes/circles with connections\n"
            f"- If it's COMPARISON: show side-by-side with visual differences\n"
            f"- If it's TRANSFORMATION: animate the change happening\n"
            f"- If it's HIERARCHY: show tree or layered structure\n\n"
            f"CRITICAL ORDER:\n"
            f"1. Create shapes\n"
            f"2. Position shapes with .shift() or .move_to()\n"
            f"3. Create SHORT labels (1-3 words) and .move_to(shape)\n"
            f"4. Create arrows using positioned shapes' .get_right()/.get_left()\n"
            f"5. Animate with meaningful motion (show flow, transformation, relationships)\n"
            f"6. FadeOut everything before next section\n\n"
            f"Topic: {segment.get('topic', 'Research Concept')}\n"
            f"Category: {segment.get('topic_category', 'general')}\n"
            f"Key Concepts to VISUALIZE: {', '.join(segment.get('key_concepts', []))}\n\n"
            f"Content (extract the CONCEPT to visualize, don't display this as text):\n{segment.get('content', '')}\n\n"
            f"Style: {animation_style}\n\n"
            f"Remember: SHOW the concept with shapes and motion, don't TELL with text walls.\n"
            f"End with 'Animation by Xe-Bot' branding.\n\n"
            f"Generate the code:"
        )
        
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
        # Create a summary of all segments
        segment_summary = "\n\n".join([
            f"Segment {i+1}: {s.get('topic', 'Topic')}\n"
            f"Category: {s.get('topic_category', 'general')}\n"
            f"Key Concepts: {', '.join(s.get('key_concepts', []))}\n"
            f"Content: {s.get('content', '')[:500]}..."
            for i, s in enumerate(segments)
        ])
        
        system_prompt = (
            "You are an expert Manim animator creating VISUAL EXPLANATIONS of research concepts.\n\n"
            "=== CORE PHILOSOPHY ===\n"
            "VISUALIZE concepts through animations and diagrams - NOT walls of text!\n"
            "- Show HOW things work with moving shapes, arrows, and transformations\n"
            "- Use diagrams, flowcharts, and visual metaphors to explain ideas\n"
            "- Minimal text: only short labels (1-3 words) inside shapes\n"
            "- Let the ANIMATION tell the story, not paragraphs of text\n"
            "- Each segment should have at least ONE diagram or visual representation\n\n"
            "=== VISUALIZATION TECHNIQUES ===\n"
            "- FLOWCHARTS: boxes with arrows showing process/data flow\n"
            "- ARCHITECTURE DIAGRAMS: components and their connections\n"
            "- NEURAL NETWORK VISUALS: layers, nodes, connections\n"
            "- COMPARISON: side-by-side visuals showing differences\n"
            "- TRANSFORMATION: animate changes (e.g., input -> output)\n"
            "- HIGHLIGHTING: Indicate(), Circumscribe() for emphasis\n"
            "- COLOR CODING: different colors = different concepts\n"
            "- BUILDING UP: complex diagrams piece by piece\n\n"
            "=== REQUIREMENTS ===\n"
            "1. Generate ONLY valid Manim Community Edition Python code\n"
            "2. Single Scene class for entire animation\n"
            "3. Include: from manim import *\n"
            "4. NEVER use MathTex, Tex, or LaTeX - ONLY use Text()\n"
            "5. Use only ASCII characters\n"
            "6. Total duration: 30-90 seconds\n"
            "7. EVERY segment must have a VISUAL (diagram, flowchart, etc.)\n\n"
            "=== GOLDEN RULE: ORDER OF OPERATIONS ===\n"
            "1. CREATE all shapes\n"
            "2. POSITION shapes using .shift()\n"
            "3. CREATE labels and .move_to(shape)\n"
            "4. CREATE arrows using positioned shapes\n"
            "5. ANIMATE everything\n"
            "6. FADEOUT everything before next section\n\n"
            "=== ARROW POSITIONING ===\n"
            "WRONG: Create arrow before positioning shapes\n"
            "CORRECT: Position shapes FIRST, then create arrow\n"
            "Example:\n"
            "  box1 = Rectangle(width=2, height=1, color=BLUE, fill_opacity=0.3)\n"
            "  box2 = Rectangle(width=2, height=1, color=GREEN, fill_opacity=0.3)\n"
            "  box1.shift(LEFT*3)  # Position FIRST\n"
            "  box2.shift(RIGHT*3)\n"
            "  arrow = Arrow(box1.get_right(), box2.get_left(), buff=0.1)  # THEN arrow\n\n"
            "=== LABEL POSITIONING ===\n"
            "WRONG: label.move_to(box) before box is positioned\n"
            "CORRECT: Position box first, then create label and move_to\n"
            "Example:\n"
            "  box.shift(LEFT*3)  # Position FIRST\n"
            "  label = Text('Name', font_size=20)\n"
            "  label.move_to(box)  # NOW label inside box\n\n"
            "=== NO TEXT OVERLAP ===\n"
            "EVERY segment MUST end with:\n"
            "  self.play(*[FadeOut(m) for m in self.mobjects])\n\n"
            "=== SCREEN LAYOUT ===\n"
            "- Frame: x from -7 to 7, y from -4 to 4\n"
            "- Title: .to_edge(UP, buff=0.5)\n"
            "- Shapes: width 2-3, height 1-1.5\n"
            "- Spacing: LEFT*4, ORIGIN, RIGHT*4\n\n"
            "=== COMPLETE EXAMPLE ===\n"
            "from manim import *\n\n"
            "class PaperIntro(Scene):\n"
            "    def construct(self):\n"
            "        # Title\n"
            "        title = Text('Paper Title', font_size=44, color=BLUE)\n"
            "        self.play(Write(title))\n"
            "        self.wait(2)\n"
            "        self.play(FadeOut(title))\n\n"
            "        # Segment with diagram\n"
            "        seg_title = Text('Background', font_size=36, color=GREEN)\n"
            "        seg_title.to_edge(UP, buff=0.5)\n"
            "        self.play(Write(seg_title))\n\n"
            "        # Create and position shapes\n"
            "        box1 = RoundedRectangle(width=2.5, height=1, corner_radius=0.1, color=RED, fill_opacity=0.3)\n"
            "        box2 = RoundedRectangle(width=2.5, height=1, corner_radius=0.1, color=GREEN, fill_opacity=0.3)\n"
            "        box1.shift(LEFT*3)\n"
            "        box2.shift(RIGHT*3)\n\n"
            "        # Labels AFTER positioning\n"
            "        lbl1 = Text('Input', font_size=20)\n"
            "        lbl1.move_to(box1)\n"
            "        lbl2 = Text('Output', font_size=20)\n"
            "        lbl2.move_to(box2)\n\n"
            "        # Arrow AFTER positioning\n"
            "        arrow = Arrow(box1.get_right(), box2.get_left(), buff=0.1, color=WHITE)\n\n"
            "        # Animate\n"
            "        self.play(Create(box1), Write(lbl1))\n"
            "        self.play(GrowArrow(arrow))\n"
            "        self.play(Create(box2), Write(lbl2))\n"
            "        self.wait(2)\n\n"
            "        # Clear before next\n"
            "        self.play(*[FadeOut(m) for m in self.mobjects])\n\n"
            "        # Branding\n"
            "        brand = Text('Animation by Xe-Bot', font_size=40, color=BLUE)\n"
            "        self.play(FadeIn(brand))\n"
            "        self.wait(2)\n"
            "        self.play(FadeOut(brand))\n\n"
            "Return ONLY Python code. No markdown, no explanations."
        )
        
        user_prompt = (
            f"Create a complete Manim animation that VISUALLY EXPLAINS this research paper.\n\n"
            f"GOAL: Viewers should UNDERSTAND the concepts by SEEING diagrams and animations,\n"
            f"not by reading walls of text. Each segment needs a VISUAL representation.\n\n"
            f"FOR EACH SEGMENT, create one of these visuals:\n"
            f"- Background/Problem: diagram showing the challenge or current state\n"
            f"- Approach/Method: flowchart showing the process or architecture\n"
            f"- Components: boxes with arrows showing how parts connect\n"
            f"- Results: visual comparison or transformation\n\n"
            f"CRITICAL ORDER for each visual:\n"
            f"1. Create shapes (boxes, circles, etc.)\n"
            f"2. Position with .shift()\n"
            f"3. Create SHORT labels (1-3 words) and .move_to(shape)\n"
            f"4. Create arrows AFTER positioning\n"
            f"5. Animate with meaningful motion\n"
            f"6. FadeOut ALL before next segment\n\n"
            f"Paper Title: {title}\n\n"
            f"Segments to VISUALIZE (don't just display this text, CREATE DIAGRAMS for each):\n{segment_summary}\n\n"
            f"Remember: SHOW concepts with visuals, don't TELL with text dumps.\n"
            f"End with 'Animation by Xe-Bot' branding.\n\n"
            f"Generate the complete Manim code:"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.chat_completion(messages, temperature=0.5, max_tokens=8000)
        
        code = self._clean_code_response(response.content)
        
        return code


# Global client instance
openrouter_client = OpenRouterClient()

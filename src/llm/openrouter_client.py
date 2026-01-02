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
        Segment the introduction into logical parts with deep concept understanding
        
        Args:
            introduction: The introduction text
        
        Returns:
            List of segments with conceptual understanding and visual metaphors (3-5 segments)
        """
        messages = [
            {
                "role": "system",
                "content": """You are an expert at UNDERSTANDING and VISUALIZING research concepts.
Your task is to deeply understand a research paper and extract the CORE IDEAS that can be ANIMATED.

=== YOUR MISSION ===
Don't just extract text - UNDERSTAND the concepts and think about how to VISUALIZE them.
Imagine you're a 3Blue1Brown animator trying to explain this paper through visual metaphors.

=== CRITICAL REQUIREMENT ===
Create 3-5 segments. Each segment should represent a CORE IDEA that can be animated visually.

=== FOR EACH SEGMENT, THINK DEEPLY ===

1. **CONCEPT UNDERSTANDING**: What is the core idea? Not the words, but the MEANING.
   - Is it about combining things? (show merging/fusion)
   - Is it about transformation? (show morphing)
   - Is it about flow/process? (show particles moving through stages)
   - Is it about comparison? (show side-by-side with differences highlighted)
   - Is it about structure? (show hierarchical/network layouts)
   - Is it about growth/improvement? (show expansion, bars rising)
   - Is it about breaking/fixing? (show degradation then repair)

2. **VISUAL METAPHOR**: What real-world phenomenon represents this concept?
   - Neural networks → brain with firing neurons
   - Optimization → climbing a mountain, finding lowest valley
   - Data flow → water/particles streaming through pipes
   - Classification → sorting objects into buckets
   - Attention mechanism → spotlight focusing on parts
   - Encryption → lock and key, scrambled puzzle
   - Compression → squeezing large object into small space
   - Training → repeated cycles of adjustment, tuning dials
   - Inference → input goes in, output comes out through black box
   - Ensemble → multiple experts voting together

3. **ANIMATION APPROACH**: How should this concept be shown in motion?
   - What STARTS the animation? (initial state)
   - What TRANSFORMS? (the action/process)
   - What is the RESULT? (final state)

=== OUTPUT FORMAT ===
For each segment provide:
1. concept_summary: The CORE IDEA in 1-2 sentences (what the reader should UNDERSTAND)
2. visual_metaphor: A concrete visual representation (e.g., "particles flowing through a funnel")
3. topic: Short title (2-4 words)
4. topic_category: One of [background, problem_statement, motivation, related_work, approach, contributions, outline]
5. key_concepts: 2-3 key technical terms
6. animation_description: Describe the animation step-by-step:
   - SCENE: What objects appear (circles, boxes, particles, etc.)
   - ACTION: What motion happens (merge, split, flow, transform, pulse)
   - INSIGHT: What moment shows the "aha" understanding
7. content: Original text excerpt (brief - for reference only)

=== EXAMPLE ===
For a paper about "attention mechanisms in transformers":

{
  "concept_summary": "The model learns to focus on relevant parts of the input, ignoring irrelevant parts, like a spotlight on a stage",
  "visual_metaphor": "A spotlight sweeping across words, brightening important ones while dimming others",
  "topic": "Attention Mechanism",
  "topic_category": "approach",
  "key_concepts": ["attention weights", "query-key-value", "self-attention"],
  "animation_description": {
    "scene": "A row of words (boxes) with a glowing orb (attention head) above them",
    "action": "The orb sends beams down to each word, beams vary in brightness based on attention weight. High-attention words glow and rise slightly.",
    "insight": "Show the weighted sum - beams converge into a single output, with brightest contributions most visible"
  },
  "content": "The attention mechanism allows the model to..."
}

Return a JSON object with a "segments" array containing 3-5 segments."""
            },
            {
                "role": "user",
                "content": f"Deeply understand this research introduction and extract the CORE IDEAS that can be visualized:\n\n{introduction}"
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
        
        # Choose visualization type based on category - 3BLUE1BROWN STYLE
        visualization_hints = {
            'background': '''3B1B-STYLE CONTEXT VISUALIZATION:
- Create a CONSTELLATION of floating particles representing the field
- Use ORBIT animations for interconnected concepts
- Show WAVE propagation for spreading influence
- Build a NETWORK with nodes appearing and connecting with animated lines
- Add SUBTLE MOTION: particles drifting, gentle pulsing of nodes''',
            'problem_statement': '''3B1B-STYLE PROBLEM VISUALIZATION:
- Show a WORKING SYSTEM first, then BREAK it (crack appears, pieces separate)
- Use MORPHING: good shape transforms into broken/corrupted version
- Create VISUAL TENSION: two opposing forces pulling apart
- Show MISSING PIECE with glowing outline where something should be
- Animate DEGRADATION: color fading from GREEN to RED, structure collapsing''',
            'motivation': '''3B1B-STYLE CAUSE-EFFECT ANIMATION:
- DOMINO EFFECT: one event triggers cascading animations
- RIPPLE PROPAGATION: impact spreads outward in concentric waves
- GROWTH VISUALIZATION: small seed expands into full structure
- BRANCHING TREE: single root splits and multiplies
- ENERGY TRANSFER: glowing particles flow from source to destination''',
            'related_work': '''3B1B-STYLE COMPARISON/EVOLUTION:
- MORPHING between different approaches (shape A transforms to shape B)
- TIMELINE with animated progression of dots along a path
- SIDE-BY-SIDE with connecting bridges showing relationships
- VENN DIAGRAM building with overlapping circles animating
- EVOLUTION: primitive form gradually transforms into advanced form''',
            'approach': '''3B1B-STYLE PIPELINE/PROCESS:
- DATA FLOW: glowing particles streaming through connected nodes
- TRANSFORMATION STAGES: object changes form at each step
- FUNNEL visualization with elements combining and refining
- ASSEMBLY LINE: components coming together piece by piece
- SIGNAL PROPAGATION through neural-network-style layers''',
            'contributions': '''3B1B-STYLE ACHIEVEMENT REVEAL:
- STARS/GEMS appearing with sparkle effects
- BUILDING BLOCKS stacking to form complete structure
- SPOTLIGHT effect illuminating each contribution
- UNLOCK animation: locked shapes opening to reveal contents
- CELEBRATION: particles exploding outward in burst pattern''',
            'outline': '''3B1B-STYLE JOURNEY/ROADMAP:
- ANIMATED PATH with a dot traveling through milestones
- MAP REVEAL: regions lighting up as journey progresses
- SCROLL UNFURLING to show upcoming content
- STEPPING STONES appearing one by one across a gap
- CONSTELLATION connecting to form a complete picture''',
            'general': '''3B1B-STYLE CONCEPT VISUALIZATION:
- CENTRAL IDEA with orbiting related concepts
- MIND MAP growing organically from center outward
- MAGNETIC ATTRACTION: related elements pulling together
- PUZZLE PIECES assembling into complete picture
- EMERGENCE: many small particles forming larger coherent shape''',
            # === QUANTUM PHYSICS SPECIALIZED VISUALIZATIONS ===
            'quantum_entanglement': '''QUANTUM ENTANGLEMENT VISUALIZATION:
- TWO PARTICLES with connecting dashed line (entanglement link)
- CORRELATED SPIN ARROWS: when one flips, the other flips instantly
- GLOWING AURA around particles showing quantum state
- DISTANCE INDICATOR showing particles far apart
- MEASUREMENT FLASH: one particle measured, both states revealed
- BELL STATE visualization with correlated outcomes
- Use PURPLE/BLUE for particle A, RED/ORANGE for particle B
- Show NON-LOCAL correlation with simultaneous state changes''',
            'quantum_superposition': '''QUANTUM SUPERPOSITION VISUALIZATION:
- PROBABILITY CLOUD: fuzzy circle with multiple semi-transparent states inside
- OSCILLATING STATES: multiple positions pulsing in/out of visibility
- WAVE FUNCTION as undulating sine wave across screen
- MEASUREMENT COLLAPSE: cloud shrinks to single definite point with flash
- Use PURPLE for superposition, GREEN for collapsed definite state
- Show BOTH states existing simultaneously with overlapping circles
- Animate INTERFERENCE between probability amplitudes''',
            'quantum_measurement': '''QUANTUM MEASUREMENT PROBLEM:
- BEFORE: blurry probability cloud with multiple ghost images
- DETECTOR/APPARATUS: rectangle representing measurement device
- COLLAPSE ANIMATION: flash of light, cloud concentrates to single point
- AFTER: single definite state with solid color
- Show WAVE FUNCTION as continuous curve before, delta spike after
- Illustrate OBSERVER EFFECT with eye symbol triggering collapse''',
            'quantum_tunneling': '''QUANTUM TUNNELING VISUALIZATION:
- POTENTIAL BARRIER: tall rectangle representing forbidden region
- WAVE PACKET: oscillating blob approaching barrier
- EXPONENTIAL DECAY inside barrier shown with fading amplitude
- TRANSMITTED WAVE: smaller wave emerging on other side
- PROBABILITY DENSITY: area under wave showing tunneling probability
- Classical REFLECTION contrasted with quantum TRANSMISSION
- Use BLUE for wave, RED for barrier, YELLOW for tunneled portion''',
            'wave_function': '''WAVE FUNCTION VISUALIZATION:
- COMPLEX AMPLITUDE shown as rotating phasor arrow
- PROBABILITY DENSITY as squared magnitude (shaded area under curve)
- TIME EVOLUTION: wave propagating and changing shape
- GAUSSIAN WAVE PACKET spreading over time
- INTERFERENCE PATTERNS from overlapping waves
- NORMALIZATION: total area always equals 1
- Use color gradient (BLUE to RED) to show phase''',
            'quantum_interference': '''QUANTUM INTERFERENCE (DOUBLE-SLIT):
- DOUBLE SLIT BARRIER with two narrow gaps
- WAVE FRONTS emanating from each slit as concentric arcs
- CONSTRUCTIVE INTERFERENCE: bright bands where waves align
- DESTRUCTIVE INTERFERENCE: dark bands where waves cancel
- DETECTION SCREEN showing pattern building up particle by particle
- Single particle going through BOTH slits (superposition)
- Use BLUE for waves, GREEN for constructive, RED for destructive''',
            'quantum_computing': '''QUANTUM COMPUTING/QUBIT VISUALIZATION:
- BLOCH SPHERE: sphere representing single qubit state
- STATE VECTOR: arrow from center pointing to state on sphere
- QUANTUM GATES: rotations of the state vector (X, Y, Z, Hadamard)
- MULTIPLE QUBITS: tensor product visualization
- ENTANGLING GATES: two qubits becoming correlated (CNOT)
- QUANTUM CIRCUIT: boxes and lines showing gate sequence
- Use consistent colors: |0> at top (BLUE), |1> at bottom (RED)''',
            'decoherence': '''QUANTUM DECOHERENCE VISUALIZATION:
- COHERENT STATE: clean wave function with definite phase
- ENVIRONMENT PARTICLES: small dots approaching from outside
- PHASE SCRAMBLING: orderly wave becoming noisy/random
- ENTANGLEMENT WITH ENVIRONMENT: threads connecting to surroundings
- CLASSICAL MIXTURE: superposition fading into statistical mixture
- TIMESCALE: show rapid loss of quantum properties
- Color transition from PURPLE (quantum) to GRAY (classical)''',
            'bell_inequality': '''BELL INEQUALITY TEST VISUALIZATION:
- SOURCE emitting entangled particle pairs
- TWO DETECTORS at different angles (adjustable polarizer angles)
- CORRELATION GRAPH: plotting measurement correlations
- CLASSICAL BOUND: line showing maximum classical correlation
- QUANTUM VIOLATION: data points exceeding classical limit
- STATISTICAL BARS growing as more measurements are made
- Highlight NON-LOCAL correlations exceeding classical physics'''
        }
        
        # Detect quantum physics topics from content
        quantum_keywords = ['entanglement', 'entangled', 'superposition', 'qubit', 'quantum', 
                          'wave function', 'collapse', 'measurement', 'decoherence', 'tunneling',
                          'interference', 'bell', 'epr', 'teleportation', 'spin', 'coherence']
        
        content_lower = segment.get('content', '').lower() + ' ' + segment.get('topic', '').lower()
        
        # Check for quantum topics and override visualization hint
        if any(kw in content_lower for kw in ['entangle', 'bell', 'epr', 'non-local', 'correlated spin']):
            viz_hint = visualization_hints['quantum_entanglement']
        elif any(kw in content_lower for kw in ['superposition', 'both states', 'probability amplitude']):
            viz_hint = visualization_hints['quantum_superposition']
        elif any(kw in content_lower for kw in ['measurement', 'collapse', 'observer']):
            viz_hint = visualization_hints['quantum_measurement']
        elif any(kw in content_lower for kw in ['tunnel', 'barrier', 'forbidden']):
            viz_hint = visualization_hints['quantum_tunneling']
        elif any(kw in content_lower for kw in ['wave function', 'schrodinger', 'psi']):
            viz_hint = visualization_hints['wave_function']
        elif any(kw in content_lower for kw in ['interference', 'double.slit', 'two.slit', 'fringe']):
            viz_hint = visualization_hints['quantum_interference']
        elif any(kw in content_lower for kw in ['qubit', 'bloch', 'quantum gate', 'quantum comput']):
            viz_hint = visualization_hints['quantum_computing']
        elif any(kw in content_lower for kw in ['decoherence', 'environment', 'classical limit']):
            viz_hint = visualization_hints['decoherence']
        else:
            viz_hint = visualization_hints.get(topic_category, visualization_hints['general'])
        
        system_prompt = f'''You are a 3Blue1Brown-style animator creating STUNNING VISUAL EXPLANATIONS.

=== 3BLUE1BROWN PHILOSOPHY ===
Every concept should be shown through VISUAL INTUITION:
- Complex ideas become ANIMATED METAPHORS
- Abstract math becomes GEOMETRIC TRANSFORMATIONS  
- Relationships are shown as MOVING PARTICLES and FLOWS
- Understanding comes from WATCHING, not reading

=== CINEMATIC VISUAL TECHNIQUES ===

**PARTICLE SYSTEMS (for data, information, energy):**
particles = VGroup(*[Dot(color=BLUE, fill_opacity=0.8).scale(0.3) for _ in range(20)])
particles.arrange_in_grid(rows=4, cols=5, buff=0.2)
# Animate particles flowing along a path
for p in particles:
    self.play(p.animate.move_to(target), run_time=0.1)

**MORPHING (one shape transforms into another):**
circle = Circle(color=BLUE, fill_opacity=0.5)
square = Square(color=RED, fill_opacity=0.5)
self.play(Transform(circle, square))  # Circle becomes square!

**WAVE ANIMATIONS (for signals, energy, propagation):**
wave = FunctionGraph(lambda x: np.sin(x), x_range=[-3, 3], color=BLUE)
self.play(Create(wave))
self.play(wave.animate.shift(RIGHT*2))  # Wave propagates

**ZOOM AND PAN (focus attention):**
self.play(group.animate.scale(2).move_to(ORIGIN))  # Zoom into detail
self.play(self.camera.frame.animate.move_to(point))  # Pan camera

**ORBIT ANIMATIONS (for atoms, electrons, systems):**
electron = Dot(color=YELLOW).move_to(RIGHT*2)
orbit = Circle(radius=2, color=WHITE, stroke_opacity=0.3)
self.play(Rotate(electron, about_point=ORIGIN, angle=2*PI), run_time=2)

**FIELD VISUALIZATIONS (for forces, gradients):**
arrows = VGroup()
for x in range(-3, 4):
    for y in range(-2, 3):
        arr = Arrow(ORIGIN, UP*0.5, buff=0, stroke_width=2, color=BLUE)
        arr.move_to([x, y, 0])
        arrows.add(arr)
self.play(Create(arrows))

**MOLECULAR/ATOM VISUALIZATIONS:**
# Nucleus (protons + neutrons clustered)
nucleus = VGroup(*[Circle(radius=0.15, color=RED if i%2==0 else BLUE, fill_opacity=1).shift(
    np.array([0.1*np.cos(i*0.8), 0.1*np.sin(i*0.8), 0])
) for i in range(6)])

# Electron cloud (fuzzy probability)
cloud = Circle(radius=1.5, color=BLUE, fill_opacity=0.1, stroke_opacity=0.5)
electrons = VGroup(*[Dot(color=BLUE).scale(0.5).move_to(1.2*np.array([np.cos(a), np.sin(a), 0])) for a in [0, 2.1, 4.2]])

**FUSION VISUALIZATION (two atoms merging):**
atom1 = Circle(radius=0.5, color=BLUE, fill_opacity=0.7).shift(LEFT*3)
atom2 = Circle(radius=0.5, color=RED, fill_opacity=0.7).shift(RIGHT*3)
# Atoms approach
self.play(atom1.animate.shift(RIGHT*2.5), atom2.animate.shift(LEFT*2.5), run_time=2)
# Merge and flash
merged = Circle(radius=0.8, color=YELLOW, fill_opacity=1).move_to(ORIGIN)
self.play(Transform(atom1, merged), FadeOut(atom2), Flash(ORIGIN, color=WHITE))
# Energy release - particles explode outward
particles = VGroup(*[Dot(color=YELLOW).scale(0.3).move_to(ORIGIN) for _ in range(12)])
self.play(*[p.animate.shift(2*np.array([np.cos(i*PI/6), np.sin(i*PI/6), 0])) for i, p in enumerate(particles)])

**NEURAL NETWORK VISUALIZATION:**
# Layer of neurons
def create_layer(n, x_pos, color):
    layer = VGroup(*[Circle(radius=0.2, color=color, fill_opacity=0.8) for _ in range(n)])
    layer.arrange(DOWN, buff=0.3).shift(RIGHT*x_pos)
    return layer

input_layer = create_layer(4, -3, BLUE)
hidden_layer = create_layer(5, 0, GREEN)  
output_layer = create_layer(2, 3, RED)

# Connections with signal propagation
for n1 in input_layer:
    for n2 in hidden_layer:
        line = Line(n1.get_right(), n2.get_left(), stroke_opacity=0.3)
        self.add(line)
        # Signal pulse
        pulse = Dot(color=YELLOW, radius=0.05).move_to(n1)
        self.play(pulse.animate.move_to(n2), run_time=0.1)

**GRAPH/CHART ANIMATIONS:**
# Bar chart rising
bars = VGroup()
heights = [2, 3, 1.5, 4, 2.5]
for i, h in enumerate(heights):
    bar = Rectangle(width=0.5, height=0.1, color=BLUE, fill_opacity=0.8).shift(RIGHT*(i-2))
    bar.align_to(DOWN*2, DOWN)
    bars.add(bar)
    self.play(bar.animate.stretch_to_fit_height(h), run_time=0.3)

=== QUANTUM PHYSICS ANIMATION TECHNIQUES ===

**QUANTUM ENTANGLEMENT (correlated particles):**
# Create entangled particle pair
particle_a = VGroup(
    Circle(radius=0.5, color=BLUE, fill_opacity=0.2),  # glow
    Circle(radius=0.3, color=BLUE, fill_opacity=0.8)   # core
).shift(LEFT * 3)
particle_b = VGroup(
    Circle(radius=0.5, color=RED, fill_opacity=0.2),
    Circle(radius=0.3, color=RED, fill_opacity=0.8)
).shift(RIGHT * 3)

# Entanglement connection line
entangle_link = DashedLine(particle_a.get_center(), particle_b.get_center(), 
                           color=YELLOW, dash_length=0.2)

# Spin arrows showing correlation
spin_a = Arrow(ORIGIN, UP * 0.5, color=WHITE, stroke_width=4).move_to(particle_a)
spin_b = Arrow(ORIGIN, DOWN * 0.5, color=WHITE, stroke_width=4).move_to(particle_b)

# Measurement causes instant correlation
self.play(Flash(particle_a.get_center(), color=WHITE))
self.play(
    Rotate(spin_a, PI, about_point=particle_a.get_center()),
    Rotate(spin_b, PI, about_point=particle_b.get_center()),  # Both flip together!
    run_time=0.3
)

**QUANTUM SUPERPOSITION (multiple states):**
# Probability cloud visualization
prob_cloud = Circle(radius=1.5, color=PURPLE, fill_opacity=0.15, stroke_opacity=0.3)

# Multiple overlapping states
states = VGroup()
for i in range(5):
    angle = i * 2*PI/5
    r = 0.7
    state = Circle(radius=0.2, color=PURPLE, fill_opacity=0.5)
    state.move_to(r * np.array([np.cos(angle), np.sin(angle), 0]))
    states.add(state)

# Oscillating superposition
for state in states:
    self.play(state.animate.scale(1.3).set_opacity(0.8), run_time=0.1)
    self.play(state.animate.scale(1/1.3).set_opacity(0.5), run_time=0.1)

# Measurement collapse - all states merge to one
flash = Circle(radius=0.1, color=WHITE).move_to(states[0])
self.play(
    flash.animate.scale(15).set_opacity(0),
    *[FadeOut(s) for s in states[1:]],
    states[0].animate.set_color(GREEN).set_opacity(1),
    FadeOut(prob_cloud),
    run_time=0.5
)

**WAVE FUNCTION (probability amplitude):**
axes = Axes(x_range=[-4, 4, 1], y_range=[-1.5, 1.5, 0.5], x_length=8, y_length=3)

# Gaussian wave packet
def wave_func(x): return np.exp(-(x)**2/2) * np.cos(4*x)
wave = axes.plot(wave_func, color=PURPLE, stroke_width=3)

# Probability density (|psi|^2)
prob_density = axes.plot(lambda x: np.exp(-x**2), color=BLUE, fill_opacity=0.3)

# Wave function collapse to delta spike
spike = Line(axes.c2p(1, 0), axes.c2p(1, 1), color=GREEN, stroke_width=4)
self.play(Transform(wave, spike), FadeOut(prob_density), run_time=0.5)

**QUANTUM TUNNELING (through barrier):**
barrier = Rectangle(width=1, height=3, color=RED, fill_opacity=0.3, stroke_width=3)

# Incoming wave packet
wave_packet = Circle(radius=0.3, color=BLUE, fill_opacity=0.6).shift(LEFT * 4)

# Wave hits barrier, splits into reflected + transmitted
reflected = wave_packet.copy().set_color(GREEN)
transmitted = wave_packet.copy().set_opacity(0.3).set_color(PURPLE)

self.play(
    reflected.animate.move_to(LEFT * 4),   # Bounces back
    transmitted.animate.move_to(RIGHT * 3), # Tunnels through!
    run_time=1.5
)

**BELL STATE / EPR CORRELATION:**
# Source emitting entangled pairs
source = Circle(radius=0.3, color=YELLOW, fill_opacity=0.8)

# Two detectors at angles
detector_a = Rectangle(width=1, height=0.6, color=BLUE, fill_opacity=0.3).shift(LEFT * 4)
detector_b = Rectangle(width=1, height=0.6, color=RED, fill_opacity=0.3).shift(RIGHT * 4)

# Angle settings
angle_a = Arc(radius=0.3, angle=PI/6, color=BLUE).next_to(detector_a, DOWN)
angle_b = Arc(radius=0.3, angle=PI/4, color=RED).next_to(detector_b, DOWN)

# Emit correlated photons
for _ in range(3):
    photon_a = Dot(color=BLUE, radius=0.1).move_to(source)
    photon_b = Dot(color=RED, radius=0.1).move_to(source)
    self.play(
        photon_a.animate.move_to(detector_a),
        photon_b.animate.move_to(detector_b),
        run_time=0.3
    )
    self.play(FadeOut(photon_a), FadeOut(photon_b), run_time=0.1)

**DECOHERENCE (quantum to classical):**
# Coherent state with clean phase
coherent = Circle(radius=0.6, color=PURPLE, fill_opacity=0.6)
phase_indicator = Arrow(ORIGIN, RIGHT * 0.5, color=WHITE).move_to(coherent)

# Environment particles approaching
env_particles = VGroup(*[
    Dot(color=GRAY, radius=0.05).move_to(2.5 * np.array([np.cos(i*PI/4), np.sin(i*PI/4), 0]))
    for i in range(8)
])

# Particles interact, phase scrambles
self.play(*[p.animate.move_to(0.8 * p.get_center() / np.linalg.norm(p.get_center())) for p in env_particles])
self.play(
    coherent.animate.set_color(GRAY).set_opacity(0.3),
    Rotate(phase_indicator, 3*PI, about_point=coherent.get_center()),  # Phase randomizes
    run_time=1
)

**CRITICAL: NO TEXT OVERLAP ===
EVERY section MUST start fresh. Before ANY new content:
  self.play(*[FadeOut(m) for m in self.mobjects])

=== VISUALIZATION STYLE FOR THIS SEGMENT ===
{viz_hint}

=== TEXT GUIDELINES FOR CLARITY ===
Add MINIMAL text to enhance understanding:

1. **TITLE** (required): 2-4 words, font_size=36, at top
   title = Text("Core Concept", font_size=36, color=BLUE).to_edge(UP)

2. **LABELS** (2-3 max): 1-2 words each, font_size=18-20, attached to shapes
   label = Text("Input", font_size=18, color=WHITE)
   label.next_to(shape, DOWN, buff=0.2)

3. **INSIGHT TEXT** (optional): Brief "aha" moment, font_size=24
   insight = Text("Key: A leads to B", font_size=24, color=YELLOW)
   insight.to_edge(DOWN, buff=0.5)
   self.play(FadeIn(insight, shift=UP))

TEXT PLACEMENT RULES:
- Title: .to_edge(UP, buff=0.5)
- Shape labels: .next_to(shape, DOWN/UP, buff=0.2) or .move_to(shape) if inside
- Insight/summary: .to_edge(DOWN, buff=0.5)
- Never put text IN the animation area (center of screen)
- Text should SUPPORT visuals, not replace them

=== ABSOLUTE REQUIREMENTS ===
1. Use ONLY: from manim import *
2. import numpy as np (for math operations)
3. Scene class as base
4. NEVER use MathTex, Tex, or LaTeX - ONLY Text()
5. ASCII characters only (no unicode bullets, arrows)
6. Duration: 20-40 seconds
7. Minimum 8-12 animated shapes/objects
8. Use at least 4 different colors
9. Include motion effects (particles, transforms, rotations)
10. ALWAYS clear with FadeOut before new sections
11. Include 1 title + 2-3 labels for clarity

=== GOLDEN RULES ===
1. SHOW concepts through MOTION, supported by minimal text
2. Use METAPHORS viewers can understand visually
3. Every abstract concept needs a CONCRETE visual
4. Labels identify WHAT things are, animation shows HOW they work
5. Build complexity GRADUALLY
6. End with satisfying RESOLUTION

Return ONLY Python code. No markdown, no explanations.'''
        
        # Extract first line of viz_hint for the required visual type
        viz_type = viz_hint.split('\n')[0].split(':')[0].strip() if '\n' in viz_hint else viz_hint.split(':')[0].strip()
        
        # Get conceptual understanding from segment (new fields from enhanced segmentation)
        concept_summary = segment.get('concept_summary', segment.get('content', '')[:200])
        visual_metaphor = segment.get('visual_metaphor', '')
        animation_desc = segment.get('animation_description', {})
        
        # Build animation guidance from conceptual understanding
        animation_guidance = ""
        if animation_desc:
            if isinstance(animation_desc, dict):
                animation_guidance = f"""
=== PRE-DEFINED ANIMATION PLAN ===
SCENE SETUP: {animation_desc.get('scene', 'Create appropriate visual objects')}
ACTION/MOTION: {animation_desc.get('action', 'Animate the core concept')}
KEY INSIGHT: {animation_desc.get('insight', 'Highlight the main understanding')}
"""
            else:
                animation_guidance = f"\n=== ANIMATION APPROACH ===\n{animation_desc}\n"
        
        user_prompt = f'''Create a 3BLUE1BROWN-STYLE visual explanation for this research CONCEPT.

=== THE CORE IDEA TO VISUALIZE ===
{concept_summary}

=== VISUAL METAPHOR TO USE ===
{visual_metaphor if visual_metaphor else "Choose an appropriate visual metaphor based on the concept"}

Topic: {segment.get('topic', 'Research Concept')}
Category: {topic_category}
Key Terms: {', '.join(segment.get('key_concepts', []))}
{animation_guidance}

=== YOUR MISSION ===
You are NOT displaying text - you are EXPLAINING an IDEA through ANIMATION.

Think: "How would 3Blue1Brown explain this concept?"
- What SHAPES represent the key elements?
- What MOTION shows the relationship/process?
- What TRANSFORMATION reveals the insight?

=== CONCEPT-TO-VISUAL MAPPING ===
Based on the concept, choose the right visualization:

IF the concept is about COMBINING/INTEGRATION:
→ Show separate objects MERGING into one (particles converging, circles overlapping)

IF the concept is about TRANSFORMATION/CHANGE:
→ Show MORPHING (shape A smoothly becomes shape B)

IF the concept is about PROCESS/FLOW:
→ Show PARTICLES/DATA flowing through stages (dots moving along paths)

IF the concept is about COMPARISON:
→ Show SIDE-BY-SIDE with visual differences (size, color, position)

IF the concept is about HIERARCHY/STRUCTURE:
→ Show TREE or NETWORK with connections appearing

IF the concept is about PROBLEM→SOLUTION:
→ Show BROKEN state first, then REPAIR/FIX animation

IF the concept is about IMPROVEMENT/OPTIMIZATION:
→ Show GROWTH (expanding circles, rising bars, climbing path)

IF the concept is about ATTENTION/FOCUS:
→ Show SPOTLIGHT effect (beam highlighting relevant parts)

IF the concept is about LEARNING/TRAINING:
→ Show ITERATIVE REFINEMENT (repeated adjustments, dial tuning)

=== QUANTUM PHYSICS CONCEPT MAPPINGS ===

IF the concept is about QUANTUM ENTANGLEMENT:
→ Show TWO PARTICLES with glowing auras, connected by dashed line
→ SPIN ARROWS that flip together (when one measured, both change)
→ Use PURPLE/BLUE for particle A, RED for particle B
→ Show INSTANT CORRELATION with simultaneous animations
→ Label as "Particle A", "Particle B", "Entangled"

IF the concept is about SUPERPOSITION:
→ Show PROBABILITY CLOUD (fuzzy circle with multiple ghost states inside)
→ States OSCILLATE in and out of visibility
→ MEASUREMENT causes COLLAPSE: flash, cloud shrinks to single solid point
→ Use PURPLE for superposition, GREEN for collapsed state

IF the concept is about WAVE FUNCTION:
→ Show OSCILLATING WAVE on axes (probability amplitude)
→ SQUARED AMPLITUDE as shaded area (probability density)
→ Wave EVOLVES over time, spreading or changing shape
→ COLLAPSE shown as wave becoming sharp spike

IF the concept is about QUANTUM MEASUREMENT:
→ Show DETECTOR/APPARATUS box
→ BEFORE: blurry cloud with multiple possibilities
→ FLASH/INTERACTION: bright pulse when measured
→ AFTER: single definite state emerges

IF the concept is about QUANTUM TUNNELING:
→ Show BARRIER as tall rectangle (classically forbidden region)
→ WAVE PACKET approaching from left
→ EXPONENTIAL DECAY inside barrier (fading amplitude)
→ TRANSMITTED WAVE emerging on other side
→ Use BLUE for wave, RED for barrier, PURPLE for tunneled part

IF the concept is about DECOHERENCE:
→ Show CLEAN quantum state with definite phase
→ ENVIRONMENT PARTICLES approaching
→ PHASE SCRAMBLES: arrow rotates randomly
→ COLOR fades from PURPLE (quantum) to GRAY (classical)

IF the concept is about BELL INEQUALITY/EPR:
→ Show SOURCE emitting particle pairs
→ TWO DETECTORS at different angles
→ CORRELATION exceeds classical limits
→ Highlight NON-LOCALITY with instant correlations

IF the concept is about QUANTUM INTERFERENCE:
→ Show DOUBLE SLIT with wave fronts from each slit
→ CONSTRUCTIVE (bright) and DESTRUCTIVE (dark) fringes
→ Pattern builds up particle by particle

IF the concept is about QUBIT/QUANTUM COMPUTING:
→ Show BLOCH SPHERE with state vector
→ QUANTUM GATES as rotations of the vector
→ ENTANGLING OPERATIONS correlating multiple qubits

=== TECHNICAL REQUIREMENTS ===
1. 8-15 animated objects (shapes, particles, arrows)
2. Motion MUST convey the concept (not decoration)
3. Colors encode meaning: BLUE=input, GREEN=process, YELLOW=highlight, RED=output
4. Build complexity gradually - start simple
5. Have a clear "AHA moment" where the insight becomes visible

=== TEXT FOR CLARITY ===
Add minimal text to help viewers understand:

1. **TITLE** (required): Short topic name at top
   - Example: Text("Data Flow", font_size=36, color=BLUE).to_edge(UP)

2. **LABELS** (2-4 labels): Identify key elements
   - Example: Text("Input", font_size=18).next_to(input_box, DOWN, buff=0.2)
   - Keep labels SHORT: 1-2 words max

3. **INSIGHT** (optional): One-line takeaway at bottom
   - Example: Text("Result: Faster Processing", font_size=24, color=YELLOW).to_edge(DOWN)

=== STRUCTURE ===
1. Title appears at top (2-4 words)
2. Visual elements appear with small labels
3. Core concept demonstrated through motion
4. Insight text appears at key moment (optional)
5. Resolution (complete picture)
6. Fadeout + Xe-Bot branding

The viewer should UNDERSTAND the concept through WATCHING + minimal text labels!

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
        code = code.replace('\\theta', 'theta')
        code = code.replace('\\delta', 'delta')
        code = code.replace('\\pi', 'pi')
        code = code.replace('\\infty', 'infinity')
        code = code.replace('\\rightarrow', '->')
        code = code.replace('\\leftarrow', '<-')
        code = code.replace('\\times', 'x')
        code = code.replace('\\cdot', '*')
        
        # Fix common issues that cause Manim to crash
        # 1. Remove empty list animations
        code = re.sub(r'self\.play\(\*\[\s*\]\)', '# Empty animation removed', code)
        
        # 2. Fix zero or negative run_time
        code = re.sub(r'run_time\s*=\s*0([,\)])', r'run_time=0.3\1', code)
        code = re.sub(r'run_time\s*=\s*-\d+', 'run_time=0.5', code)
        
        # 3. Fix problematic scale values
        code = re.sub(r'\.scale\(\s*0\s*\)', '.scale(0.01)', code)
        code = re.sub(r'\.scale\(\s*-', '.scale(0.5', code)
        
        # 4. Fix common typos in Manim methods
        code = re.sub(r'\bFadeout\b', 'FadeOut', code)
        code = re.sub(r'\bFadein\b', 'FadeIn', code)
        code = re.sub(r'\bGrowarrow\b', 'GrowArrow', code)
        
        # 5. Replace unicode characters that cause issues
        code = code.replace('→', '->')
        code = code.replace('←', '<-')
        code = code.replace('•', '-')
        code = code.replace('…', '...')
        code = code.replace('"', '"').replace('"', '"')
        code = code.replace(''', "'").replace(''', "'")
        
        # 6. Ensure construct method doesn't have syntax errors
        # Fix missing colons after def construct(self)
        code = re.sub(r'def construct\(self\)\s*\n', 'def construct(self):\n', code)
        
        # 7. Fix potential issues with string literals in Text()
        # Remove any multiline strings in Text() calls
        code = re.sub(r'Text\(["\']([^"\']{100,})["\']', lambda m: f'Text("{m.group(1)[:50]}..."', code)
        
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
        # Create a summary of all segments with conceptual understanding
        visualization_hints = {
            'background': 'CONTEXT: floating particles, interconnected nodes, establishing the field',
            'problem_statement': 'PROBLEM: visual breakdown, cracks appearing, things going wrong',
            'motivation': 'IMPACT: ripple effects, domino chains, showing why this matters',
            'related_work': 'COMPARISON: morphing between approaches, side-by-side differences',
            'approach': 'SOLUTION: pipeline with data flowing, transformation stages',
            'contributions': 'ACHIEVEMENTS: stars appearing, building blocks stacking, unlocking',
            'outline': 'JOURNEY: path with milestones, roadmap revealing',
            'general': 'CONCEPT: central idea with orbiting related concepts'
        }
        
        # Build rich segment descriptions using new conceptual fields
        segment_descriptions = []
        for i, s in enumerate(segments[:5]):
            desc = f"SEGMENT {i+1}: {s.get('topic', 'Topic')}\n"
            
            # Use concept_summary if available (from enhanced segmentation)
            if s.get('concept_summary'):
                desc += f"CORE IDEA: {s.get('concept_summary')}\n"
            
            # Use visual_metaphor if available
            if s.get('visual_metaphor'):
                desc += f"VISUAL METAPHOR: {s.get('visual_metaphor')}\n"
            
            # Use animation_description if available
            anim_desc = s.get('animation_description', {})
            if isinstance(anim_desc, dict) and anim_desc:
                desc += f"SCENE: {anim_desc.get('scene', '')}\n"
                desc += f"ACTION: {anim_desc.get('action', '')}\n"
                desc += f"INSIGHT: {anim_desc.get('insight', '')}\n"
            
            desc += f"Category: {s.get('topic_category', 'general')}\n"
            desc += f"Suggested Visual: {visualization_hints.get(s.get('topic_category', 'general'), 'concept visualization')}\n"
            desc += f"Key Terms: {', '.join(s.get('key_concepts', []))}"
            
            segment_descriptions.append(desc)
        
        segment_summary = "\n\n".join(segment_descriptions)
        
        system_prompt = f'''You are a 3Blue1Brown-style animator creating STUNNING VISUAL EXPLANATIONS.

=== 3BLUE1BROWN PHILOSOPHY ===
Every abstract concept becomes a VISUAL EXPERIENCE:
- Show, don't tell - viewers UNDERSTAND through WATCHING
- Use VISUAL METAPHORS (atoms as orbiting particles, data as flowing streams)
- Build complexity GRADUALLY - start simple, add layers
- MOTION conveys MEANING (merging = combining, expanding = growing, flowing = transferring)

=== CRITICAL: PREVENT TEXT OVERLAP ===
Before EVERY new segment:
  self.play(*[FadeOut(m) for m in self.mobjects])

This is MANDATORY to clear the screen between sections.

=== 3BLUE1BROWN VISUAL TECHNIQUES ===

**PARTICLE SYSTEMS (for data, energy, information):**
# Particles flowing through a system
particles = VGroup(*[Dot(color=BLUE, fill_opacity=0.6).scale(0.4) for _ in range(20)])
for i, p in enumerate(particles):
    p.move_to(LEFT*4 + UP*(i*0.3 - 2))
# Animate flow
self.play(*[p.animate.shift(RIGHT*6) for p in particles], run_time=2)

**MORPHING TRANSFORMATIONS (for change, evolution):**
# Shape A transforms into Shape B
circle = Circle(color=BLUE, fill_opacity=0.6)
square = Square(color=RED, fill_opacity=0.6)
self.play(Transform(circle, square), run_time=2)

**ORBITAL MOTION (for atomic/system concepts):**
# Electron orbiting nucleus
nucleus = Circle(radius=0.3, color=RED, fill_opacity=1)
electron = Dot(color=BLUE).move_to(RIGHT*1.5)
orbit = Circle(radius=1.5, color=WHITE, stroke_opacity=0.3)
self.play(Rotate(electron, about_point=ORIGIN, angle=2*PI), run_time=3)

**WAVE PROPAGATION (for signals, communication):**
# Ripple effect from center
for i in range(3):
    ring = Circle(radius=0.5+i, color=BLUE, fill_opacity=0, stroke_opacity=1-i*0.3)
    self.play(Create(ring), run_time=0.5)

**MERGING/FUSION (when things combine):**
obj1 = Circle(radius=0.5, color=BLUE, fill_opacity=0.7).shift(LEFT*2)
obj2 = Circle(radius=0.5, color=RED, fill_opacity=0.7).shift(RIGHT*2)
self.play(obj1.animate.shift(RIGHT*2), obj2.animate.shift(LEFT*2), run_time=1.5)
merged = Circle(radius=0.8, color=PURPLE, fill_opacity=1)
self.play(Transform(obj1, merged), FadeOut(obj2), Flash(ORIGIN))

**NEURAL SIGNAL PROPAGATION:**
# Create layers
layers = []
for x_pos, count, color in [(-3, 4, BLUE), (0, 5, GREEN), (3, 3, RED)]:
    layer = VGroup(*[Circle(radius=0.2, color=color, fill_opacity=0.7).shift(UP*(i-count/2)*0.6) for i in range(count)])
    layer.shift(RIGHT*x_pos)
    layers.append(layer)

# Animate signal passing through
signal = Dot(color=YELLOW, radius=0.1)
for i, layer in enumerate(layers):
    for node in layer:
        signal.move_to(node)
        self.play(node.animate.scale(1.3).set_color(YELLOW), run_time=0.1)
        self.play(node.animate.scale(1/1.3).set_color(layer[0].get_color()), run_time=0.1)

**FIELD/GRADIENT VISUALIZATION:**
# Arrow field showing force/direction
arrows = VGroup()
for x in range(-4, 5, 2):
    for y in range(-2, 3, 1):
        arr = Arrow(ORIGIN, UP*0.4, buff=0, stroke_width=2, color=BLUE)
        arr.move_to([x, y, 0])
        arrows.add(arr)
self.play(Create(arrows), run_time=1)

=== VISUALIZATION TYPES BY CATEGORY ===
- background -> Floating context particles + interconnected concept nodes
- problem_statement -> VISUAL breakdown (cracks appearing, RED X marks, broken chains)
- motivation -> RIPPLE effects showing impact, domino animations
- approach -> PIPELINE with glowing data packets flowing through
- contributions -> STAR icons revealing with glow, achievement badges appearing
- For ML/AI -> NEURAL NETWORK with animated signal propagation

=== QUANTUM PHYSICS VISUALIZATIONS ===
For quantum entanglement topics:
- TWO PARTICLES (circles) with glowing auras, connected by dashed line
- SPIN ARROWS inside particles that flip together (instant correlation)
- Use PURPLE/BLUE for particle A, RED for particle B
- MEASUREMENT flash causes both to change state simultaneously

For superposition topics:
- PROBABILITY CLOUD (fuzzy circle, fill_opacity=0.15)
- Multiple GHOST STATES inside, semi-transparent, oscillating
- COLLAPSE: flash + all states merge to one solid circle (GREEN)

For wave function topics:
- Plot WAVE on axes (sine-like oscillation)
- PROBABILITY DENSITY as shaded area under squared wave
- COLLAPSE: wave becomes sharp spike at measurement point

For quantum tunneling:
- BARRIER rectangle (RED, fill_opacity=0.3)
- WAVE PACKET approaching, hitting barrier
- TRANSMITTED wave emerging on other side (smaller amplitude)
- Show exponential decay inside barrier

For decoherence:
- CLEAN STATE with definite phase indicator (arrow)
- ENVIRONMENT PARTICLES approaching
- Phase scrambles (arrow rotates), color fades PURPLE->GRAY

For Bell/EPR:
- SOURCE emitting particle pairs
- TWO DETECTORS at angles
- Correlation EXCEEDS classical bound (show graph)

=== TEXT FOR CLARITY ===
Add MINIMAL text to support visual understanding:

1. **SEGMENT TITLE** (required): 2-4 words at top of each segment
   seg_title = Text("Key Concept", font_size=32, color=GREEN).to_edge(UP)

2. **ELEMENT LABELS** (2-4 per segment): Identify key shapes
   label = Text("Input", font_size=18).next_to(shape, DOWN, buff=0.2)
   
3. **INSIGHT TEXT** (1 per segment): Key takeaway at bottom
   insight = Text("Result: Better Performance", font_size=22, color=YELLOW).to_edge(DOWN)

TEXT RULES:
- Labels: 1-2 words max, font_size=16-20
- Titles: 2-4 words, font_size=28-36
- Insights: Short phrase, font_size=20-24
- Never clutter the animation area
- Text SUPPORTS visuals, doesn't replace them

=== REQUIREMENTS ===
1. from manim import * and import numpy as np
2. Single Scene class
3. ONLY Text() - NO MathTex, Tex, LaTeX
4. ASCII only
5. Duration: 60-120 seconds total
6. MINIMUM 8 shapes per segment (not counting text)
7. Each segment MUST have MOTION (particles, transforms, pulses)
8. Colors convey meaning: BLUE=input/start, GREEN=process, RED=output/end, YELLOW=highlight
9. Each segment needs: title + 2-4 labels + optional insight

=== ORDER OF OPERATIONS (EVERY SEGMENT) ===
1. FadeOut all existing: self.play(*[FadeOut(m) for m in self.mobjects])
2. Create segment title at top (2-4 words)
3. Build visual metaphor with labeled elements
4. Add MOTION and ANIMATION
5. Show insight text at key moment
6. Wait 2-3 seconds
7. FadeOut before next segment

=== EXAMPLE ===
from manim import *
import numpy as np

class PaperAnimation(Scene):
    def construct(self):
        # Title with animated underline
        title = Text("Research Topic", font_size=42, color=BLUE)
        underline = Line(LEFT*3, RIGHT*3, color=BLUE).next_to(title, DOWN, buff=0.1)
        self.play(Write(title))
        self.play(Create(underline))
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])
        
        # Segment: Show concept with labeled elements
        seg_title = Text("Key Concept", font_size=32, color=GREEN).to_edge(UP)
        self.play(Write(seg_title))
        
        # Create shapes with labels
        input_box = Circle(radius=0.5, color=BLUE, fill_opacity=0.6).shift(LEFT*3)
        input_label = Text("Input", font_size=18).next_to(input_box, DOWN, buff=0.2)
        
        output_box = Circle(radius=0.5, color=RED, fill_opacity=0.6).shift(RIGHT*3)
        output_label = Text("Output", font_size=18).next_to(output_box, DOWN, buff=0.2)
        
        self.play(Create(input_box), Write(input_label))
        
        # Animate the concept
        arrow = Arrow(input_box.get_right(), output_box.get_left(), color=WHITE)
        self.play(GrowArrow(arrow))
        self.play(Create(output_box), Write(output_label))
        
        # Insight text
        insight = Text("Data transforms through processing", font_size=22, color=YELLOW)
        insight.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(insight, shift=UP))
        
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])
        seg_title.to_edge(UP)
        self.play(Write(seg_title))
        
        # Visual metaphor: particles converging
        particles = VGroup(*[Dot(color=BLUE, fill_opacity=0.6).move_to(
            4*np.array([np.cos(i*PI/5), np.sin(i*PI/5), 0])
        ) for i in range(10)])
        self.play(*[FadeIn(p) for p in particles])
        self.play(*[p.animate.move_to(ORIGIN) for p in particles], run_time=2)
        
        # Merge into unified concept
        result = Circle(radius=0.8, color=YELLOW, fill_opacity=1)
        self.play(*[Transform(particles[0], result)] + [FadeOut(p) for p in particles[1:]], Flash(ORIGIN))
        self.wait(2)
        
        self.play(*[FadeOut(m) for m in self.mobjects])
        
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

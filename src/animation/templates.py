"""
Pre-built Animation Templates
Reusable animation components for research paper visualization
Enhanced with proper diagrams, graphs, neural networks, and visual explanations
Includes specialized quantum physics and entanglement animations
"""
from typing import List, Dict, Any

# Import quantum templates
from src.animation.quantum_templates import QuantumAnimationTemplates, quantum_templates


class AnimationTemplates:
    """Collection of pre-built Manim animation templates with enhanced visualizations"""
    
    @staticmethod
    def title_slide(title: str, authors: List[str] = None) -> str:
        """Generate title slide animation with visual flair"""
        authors_str = str(authors or [])
        title = title.replace('"', '\\"')
        
        return f'''from manim import *

class TitleSlide(Scene):
    def construct(self):
        # Animated background particles
        particles = VGroup()
        for _ in range(20):
            dot = Dot(
                point=[np.random.uniform(-7, 7), np.random.uniform(-4, 4), 0],
                radius=np.random.uniform(0.02, 0.08),
                color=BLUE,
                fill_opacity=0.3
            )
            particles.add(dot)
        self.add(particles)
        
        # Main title with gradient effect
        title_text = "{title}"
        
        # Split long titles
        if len(title_text) > 50:
            words = title_text.split()
            mid = len(words) // 2
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:])
            title = VGroup(
                Text(line1, font_size=36, color=WHITE),
                Text(line2, font_size=36, color=WHITE)
            )
            title.arrange(DOWN, buff=0.3)
        else:
            title = Text(title_text, font_size=40, color=WHITE)
        
        # Decorative lines
        line_left = Line(LEFT * 4, LEFT * 1, color=BLUE, stroke_width=2)
        line_right = Line(RIGHT * 1, RIGHT * 4, color=BLUE, stroke_width=2)
        line_left.next_to(title, LEFT, buff=0.5)
        line_right.next_to(title, RIGHT, buff=0.5)
        
        # Animate
        self.play(
            *[dot.animate.shift(UP * np.random.uniform(-0.5, 0.5)) for dot in particles],
            run_time=1
        )
        self.play(Write(title), run_time=2)
        self.play(Create(line_left), Create(line_right))
        self.wait(1)
        
        # Authors
        authors = {authors_str}
        if authors:
            author_text = Text(
                ", ".join(authors[:3]) + ("..." if len(authors) > 3 else ""),
                font_size=22,
                color=GRAY_B
            )
            author_text.next_to(title, DOWN, buff=0.8)
            self.play(FadeIn(author_text, shift=UP))
            self.wait(1)
        
        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects])
'''

    @staticmethod
    def bullet_points(title: str, points: List[str], color: str = "BLUE") -> str:
        """Generate bullet points with visual icons instead of plain text"""
        points_str = str(points)
        title = title.replace('"', '\\"')
        
        return f'''from manim import *

class BulletPointsAnimation(Scene):
    def construct(self):
        # Title with underline
        title = Text("{title}", font_size=38, color={color})
        title.to_edge(UP, buff=0.5)
        underline = Line(title.get_left(), title.get_right(), color={color}, stroke_width=2)
        underline.next_to(title, DOWN, buff=0.1)
        
        self.play(Write(title))
        self.play(Create(underline))
        
        # Bullet points with icons
        points = {points_str}
        bullets = VGroup()
        icons = [Circle, Square, Triangle, Star, RegularPolygon]
        
        for i, point in enumerate(points[:5]):
            # Create icon
            icon_class = icons[i % len(icons)]
            if icon_class == RegularPolygon:
                icon = icon_class(n=6, radius=0.15, color={color}, fill_opacity=0.5)
            elif icon_class == Star:
                icon = icon_class(n=5, outer_radius=0.15, inner_radius=0.08, color=YELLOW, fill_opacity=0.5)
            else:
                icon = icon_class(radius=0.15, color={color}, fill_opacity=0.5) if hasattr(icon_class, 'radius') else icon_class(side_length=0.25, color={color}, fill_opacity=0.5)
            
            text = Text(point[:50], font_size=24)
            row = VGroup(icon, text).arrange(RIGHT, buff=0.3)
            bullets.add(row)
        
        bullets.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        bullets.next_to(underline, DOWN, buff=0.6)
        bullets.to_edge(LEFT, buff=1)
        
        # Animate bullets one by one with icons
        for bullet in bullets:
            self.play(
                GrowFromCenter(bullet[0]),
                FadeIn(bullet[1], shift=RIGHT),
                run_time=0.6
            )
            self.wait(0.3)
        
        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects])
'''

    @staticmethod
    def flow_diagram(steps: List[str], title: str = "Process Flow") -> str:
        """Generate an enhanced flow diagram with animated data flow"""
        steps_str = str(steps)
        title = title.replace('"', '\\"')
        
        return f'''from manim import *

class FlowDiagramAnimation(Scene):
    def construct(self):
        title = Text("{title}", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))
        
        steps = {steps_str}
        
        # Create boxes for each step
        boxes = VGroup()
        labels = VGroup()
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        
        for i, step in enumerate(steps[:6]):
            box = RoundedRectangle(
                corner_radius=0.15,
                width=2.2,
                height=0.9,
                fill_color=colors[i % len(colors)],
                fill_opacity=0.3,
                stroke_color=colors[i % len(colors)],
                stroke_width=2
            )
            boxes.add(box)
            
        # Arrange in single row or two rows
        if len(boxes) <= 3:
            boxes.arrange(RIGHT, buff=1.2)
        else:
            top_row = VGroup(*boxes[:3])
            bottom_row = VGroup(*boxes[3:])
            top_row.arrange(RIGHT, buff=1.2)
            bottom_row.arrange(RIGHT, buff=1.2)
            VGroup(top_row, bottom_row).arrange(DOWN, buff=1.2)
        
        boxes.next_to(title, DOWN, buff=0.8)
        
        # Add labels AFTER positioning boxes
        for i, (box, step) in enumerate(zip(boxes, steps[:6])):
            label = Text(step[:15], font_size=18)
            label.move_to(box)
            labels.add(label)
        
        # Animate boxes appearing
        for box, label in zip(boxes, labels):
            self.play(DrawBorderThenFill(box), Write(label), run_time=0.4)
        
        # Add arrows between boxes
        arrows = VGroup()
        for i in range(len(boxes) - 1):
            if i < 2 or (i >= 3 and i < 5):
                arrow = Arrow(
                    boxes[i].get_right(),
                    boxes[i+1].get_left(),
                    buff=0.1,
                    color=WHITE,
                    stroke_width=3
                )
            else:
                # Arrow going down for row transition
                arrow = CurvedArrow(
                    boxes[2].get_bottom(),
                    boxes[3].get_top() if len(boxes) > 3 else boxes[2].get_bottom(),
                    color=WHITE,
                    angle=-TAU/4
                )
            arrows.add(arrow)
            self.play(GrowArrow(arrow), run_time=0.25)
        
        self.wait(1)
        
        # Animated data flow dot
        if len(boxes) > 0:
            dot = Dot(color=YELLOW, radius=0.12)
            dot.move_to(boxes[0].get_center())
            self.play(FadeIn(dot))
            
            for box in boxes:
                self.play(
                    dot.animate.move_to(box.get_center()),
                    box.animate.set_fill(YELLOW, opacity=0.5),
                    run_time=0.3
                )
                self.play(
                    box.animate.set_fill(box.get_stroke_color(), opacity=0.3),
                    run_time=0.2
                )
            
            self.play(FadeOut(dot))
        
        self.wait(1)
        self.play(*[FadeOut(mob) for mob in self.mobjects])
'''

    @staticmethod
    def highlight_text(text: str, highlights: List[str], title: str = "Key Points") -> str:
        """Generate animation that highlights specific words"""
        text = text.replace('"', '\\"').replace('\n', ' ')[:200]
        highlights_str = str(highlights)
        title = title.replace('"', '\\"')
        
        return f'''from manim import *

class HighlightTextAnimation(Scene):
    def construct(self):
        title = Text("{title}", font_size=36, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))
        
        # Main text
        full_text = "{text}"
        highlights = {highlights_str}
        
        # Create text - split into lines
        words = full_text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > 50:
                lines.append(" ".join(current_line[:-1]))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
        
        text_group = VGroup()
        for line in lines[:5]:
            text_mob = Text(line, font_size=24)
            text_group.add(text_mob)
        
        text_group.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        text_group.center()
        
        self.play(Write(text_group), run_time=2)
        self.wait(1)
        
        # Highlight keywords
        for highlight in highlights:
            highlight_box = SurroundingRectangle(
                text_group,
                color=YELLOW,
                buff=0.1
            )
            highlight_text = Text(highlight, font_size=28, color=YELLOW)
            highlight_text.to_edge(DOWN, buff=1)
            
            self.play(
                Create(highlight_box),
                Write(highlight_text),
                run_time=0.5
            )
            self.wait(1)
            self.play(
                FadeOut(highlight_box),
                FadeOut(highlight_text),
                run_time=0.3
            )
        
        self.wait(1)
        self.play(FadeOut(text_group), FadeOut(title))
'''

    @staticmethod
    def comparison(left_items: List[str], right_items: List[str], 
                   left_title: str = "Before", right_title: str = "After") -> str:
        """Generate a comparison animation"""
        left_str = str(left_items)
        right_str = str(right_items)
        
        return f'''from manim import *

class ComparisonAnimation(Scene):
    def construct(self):
        # Titles
        left_title = Text("{left_title}", font_size=32, color=RED)
        right_title = Text("{right_title}", font_size=32, color=GREEN)
        
        left_title.to_edge(UP).shift(LEFT * 3)
        right_title.to_edge(UP).shift(RIGHT * 3)
        
        # Divider
        divider = Line(UP * 3, DOWN * 3, color=GRAY)
        
        self.play(Write(left_title), Write(right_title))
        self.play(Create(divider))
        
        # Left items
        left_items = {left_str}
        left_group = VGroup()
        for item in left_items[:4]:
            text = Text(f"• {{item[:25]}}", font_size=22, color=RED_B)
            left_group.add(text)
        left_group.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        left_group.next_to(left_title, DOWN, buff=0.8)
        
        # Right items
        right_items = {right_str}
        right_group = VGroup()
        for item in right_items[:4]:
            text = Text(f"• {{item[:25]}}", font_size=22, color=GREEN_B)
            right_group.add(text)
        right_group.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        right_group.next_to(right_title, DOWN, buff=0.8)
        
        # Animate
        for left, right in zip(left_group, right_group):
            self.play(
                FadeIn(left, shift=RIGHT),
                FadeIn(right, shift=LEFT),
                run_time=0.5
            )
            self.wait(0.3)
        
        self.wait(2)
        
        # Transform arrow
        arrow = Arrow(LEFT * 2, RIGHT * 2, color=YELLOW, buff=0)
        arrow.shift(DOWN * 2)
        self.play(Create(arrow))
        
        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects])
'''

    @staticmethod  
    def timeline(events: List[Dict[str, str]], title: str = "Timeline") -> str:
        """Generate a timeline animation"""
        events_str = str(events)
        title = title.replace('"', '\\"')
        
        return f'''from manim import *

class TimelineAnimation(Scene):
    def construct(self):
        title = Text("{title}", font_size=36, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))
        
        # Timeline line
        timeline = Line(LEFT * 6, RIGHT * 6, color=WHITE)
        timeline.shift(DOWN * 0.5)
        self.play(Create(timeline))
        
        events = {events_str}
        
        positions = [LEFT * 4, LEFT * 1.5, RIGHT * 1.5, RIGHT * 4]
        colors = [RED, ORANGE, GREEN, BLUE]
        
        for i, event in enumerate(events[:4]):
            pos = positions[i]
            color = colors[i]
            
            # Dot on timeline
            dot = Dot(point=pos + DOWN * 0.5, color=color, radius=0.15)
            
            # Event label
            label = event.get("label", f"Event {{i+1}}")
            desc = event.get("description", "")
            
            label_text = Text(label[:15], font_size=20, color=color)
            desc_text = Text(desc[:30], font_size=16, color=GRAY)
            
            if i % 2 == 0:
                label_text.next_to(dot, UP, buff=0.3)
                desc_text.next_to(label_text, UP, buff=0.2)
            else:
                label_text.next_to(dot, DOWN, buff=0.3)
                desc_text.next_to(label_text, DOWN, buff=0.2)
            
            self.play(
                Create(dot),
                Write(label_text),
                run_time=0.5
            )
            self.play(FadeIn(desc_text), run_time=0.3)
            self.wait(0.5)
        
        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects])
'''

    @staticmethod
    def conclusion(main_point: str, sub_points: List[str] = None) -> str:
        """Generate conclusion slide animation"""
        main_point = main_point.replace('"', '\\"')
        sub_points_str = str(sub_points or [])
        
        return f'''from manim import *

class ConclusionAnimation(Scene):
    def construct(self):
        # Conclusion title
        title = Text("Summary", font_size=48, color=GOLD)
        title.to_edge(UP)
        
        self.play(Write(title))
        self.wait(0.5)
        
        # Main point
        main_point = "{main_point}"
        
        main_text = Text(main_point[:100], font_size=32, color=WHITE)
        main_text.next_to(title, DOWN, buff=1)
        
        # Box around main point
        box = SurroundingRectangle(main_text, color=GOLD, buff=0.3)
        
        self.play(Write(main_text))
        self.play(Create(box))
        self.wait(1)
        
        # Sub points
        sub_points = {sub_points_str}
        
        if sub_points:
            sub_group = VGroup()
            for point in sub_points[:3]:
                text = Text(f"→ {{point[:50]}}", font_size=24, color=BLUE_B)
                sub_group.add(text)
            
            sub_group.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
            sub_group.next_to(box, DOWN, buff=0.8)
            
            for sub in sub_group:
                self.play(FadeIn(sub, shift=RIGHT), run_time=0.4)
                self.wait(0.3)
        
        self.wait(2)
        
        # Final animation
        all_content = VGroup(*[mob for mob in self.mobjects])
        self.play(all_content.animate.scale(0.8).shift(UP * 0.5))
        
        thanks = Text("Thank You!", font_size=40, color=YELLOW)
        thanks.to_edge(DOWN, buff=1)
        self.play(Write(thanks))
        
        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects])
'''

    @staticmethod
    def architecture_diagram(components: List[Dict[str, str]], title: str = "System Architecture") -> str:
        """Generate an architecture/block diagram animation"""
        components_str = str(components)
        title = title.replace('"', '\\"')
        
        return f'''from manim import *

class ArchitectureDiagramAnimation(Scene):
    def construct(self):
        # Title
        title = Text("{title}", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))
        
        components = {components_str}
        
        # Create main container
        main_box = Rectangle(width=12, height=5, color=WHITE, stroke_opacity=0.5)
        main_box.next_to(title, DOWN, buff=0.5)
        self.play(Create(main_box))
        
        # Create component boxes
        boxes = VGroup()
        labels = VGroup()
        colors = [BLUE, GREEN, ORANGE, RED, PURPLE, YELLOW]
        
        for i, comp in enumerate(components[:6]):
            name = comp.get("name", f"Component {{i+1}}")[:15]
            box = RoundedRectangle(
                width=3, height=1.2, corner_radius=0.15,
                color=colors[i % len(colors)], fill_opacity=0.3
            )
            label = Text(name, font_size=20, color=colors[i % len(colors)])
            label.move_to(box)
            boxes.add(box)
            labels.add(label)
        
        # Arrange in grid
        if len(boxes) <= 3:
            boxes.arrange(RIGHT, buff=0.8)
            for label, box in zip(labels, boxes):
                label.move_to(box)
        else:
            top_row = VGroup(*boxes[:3])
            bottom_row = VGroup(*boxes[3:])
            top_row.arrange(RIGHT, buff=0.8)
            bottom_row.arrange(RIGHT, buff=0.8)
            VGroup(top_row, bottom_row).arrange(DOWN, buff=0.8)
            for label, box in zip(labels, boxes):
                label.move_to(box)
        
        boxes.move_to(main_box)
        labels.move_to(main_box)
        
        # Animate components appearing
        for box, label in zip(boxes, labels):
            self.play(
                GrowFromCenter(box),
                Write(label),
                run_time=0.5
            )
        
        # Add connections
        arrows = VGroup()
        if len(boxes) >= 2:
            for i in range(min(len(boxes)-1, 2)):
                arrow = Arrow(
                    boxes[i].get_right(), boxes[i+1].get_left(),
                    buff=0.1, color=WHITE, stroke_width=2
                )
                arrows.add(arrow)
                self.play(Create(arrow), run_time=0.3)
        
        self.wait(2)
        
        # Highlight each component
        for box in boxes:
            self.play(
                box.animate.set_stroke(YELLOW, width=4),
                rate_func=there_and_back,
                run_time=0.4
            )
        
        self.wait(1)
        self.play(*[FadeOut(mob) for mob in self.mobjects])
'''

    @staticmethod
    def neural_network_diagram(layers: List[int] = None, title: str = "Neural Network") -> str:
        """Generate an enhanced neural network diagram with signal propagation"""
        layers = layers or [3, 4, 4, 2]
        layers_str = str(layers)
        title = title.replace('"', '\\"')
        
        return f'''from manim import *
import numpy as np

class NeuralNetworkAnimation(Scene):
    def construct(self):
        # Title
        title = Text("{title}", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))
        
        layer_sizes = {layers_str}
        
        # Calculate positions
        num_layers = len(layer_sizes)
        layer_spacing = 10 / (num_layers - 1) if num_layers > 1 else 0
        start_x = -5
        
        all_nodes = VGroup()
        all_edges = VGroup()
        layers_list = []
        
        layer_colors = [RED, BLUE, BLUE, GREEN]
        layer_names = ["Input", "Hidden 1", "Hidden 2", "Output"]
        
        # Create nodes
        for layer_idx, size in enumerate(layer_sizes):
            layer = VGroup()
            x_pos = start_x + layer_idx * layer_spacing
            color = layer_colors[layer_idx % len(layer_colors)]
            
            for i in range(min(size, 6)):  # Max 6 nodes per layer for visibility
                y_pos = (i - (min(size, 6) - 1) / 2) * 0.8
                node = Circle(radius=0.22, color=color, fill_opacity=0.7, stroke_width=2)
                node.move_to([x_pos, y_pos - 0.3, 0])
                layer.add(node)
            
            layers_list.append(layer)
            all_nodes.add(*layer)
        
        # Animate nodes appearing layer by layer
        for i, layer in enumerate(layers_list):
            self.play(
                *[GrowFromCenter(node) for node in layer],
                run_time=0.4
            )
            # Add layer label
            label = Text(layer_names[i] if i < len(layer_names) else f"Layer {{i+1}}", font_size=16, color=WHITE)
            label.next_to(layer, DOWN, buff=0.2)
            self.play(FadeIn(label), run_time=0.2)
        
        # Create and animate edges
        for i in range(len(layers_list) - 1):
            layer_edges = VGroup()
            for node1 in layers_list[i]:
                for node2 in layers_list[i + 1]:
                    edge = Line(
                        node1.get_center(), node2.get_center(),
                        color=GRAY, stroke_opacity=0.4, stroke_width=1.5
                    )
                    layer_edges.add(edge)
            all_edges.add(layer_edges)
            self.play(Create(layer_edges), run_time=0.3)
        
        self.wait(0.5)
        
        # Signal propagation animation
        signal_colors = [YELLOW, ORANGE, RED]
        for wave in range(2):
            for i, layer in enumerate(layers_list):
                self.play(
                    *[node.animate.set_fill(signal_colors[wave % len(signal_colors)], opacity=0.9) for node in layer],
                    run_time=0.2
                )
                self.play(
                    *[node.animate.set_fill(layer_colors[i % len(layer_colors)], opacity=0.7) for node in layer],
                    run_time=0.15
                )
        
        self.wait(1)
        self.play(*[FadeOut(mob) for mob in self.mobjects])
'''

    @staticmethod
    def graph_chart(data_points: List[Dict[str, float]] = None, title: str = "Data Visualization") -> str:
        """Generate an animated bar/line chart visualization"""
        title = title.replace('"', '\\"')
        
        return f'''from manim import *
import numpy as np

class GraphChartAnimation(Scene):
    def construct(self):
        # Title
        title = Text("{title}", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))
        
        # Create axes
        axes = Axes(
            x_range=[0, 6, 1],
            y_range=[0, 10, 2],
            x_length=8,
            y_length=4,
            axis_config={{"color": WHITE, "stroke_width": 2}},
            tips=False
        )
        axes.shift(DOWN * 0.5)
        
        # Axis labels
        x_label = Text("Category", font_size=18).next_to(axes.x_axis, DOWN, buff=0.3)
        y_label = Text("Value", font_size=18).next_to(axes.y_axis, LEFT, buff=0.3).rotate(90 * DEGREES)
        
        self.play(Create(axes), Write(x_label), Write(y_label))
        
        # Sample data
        values = [3, 7, 5, 9, 4, 6]
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        bar_width = 0.6
        
        bars = VGroup()
        labels = VGroup()
        
        for i, (val, color) in enumerate(zip(values, colors)):
            # Create bar
            bar = Rectangle(
                width=bar_width,
                height=val * 0.4,  # Scale to fit
                fill_color=color,
                fill_opacity=0.7,
                stroke_color=color,
                stroke_width=2
            )
            bar.move_to(axes.c2p(i + 0.5, 0) + UP * val * 0.2)
            bars.add(bar)
            
            # Value label
            label = Text(str(val), font_size=16, color=WHITE)
            label.next_to(bar, UP, buff=0.1)
            labels.add(label)
        
        # Animate bars growing from bottom
        for bar, label in zip(bars, labels):
            bar.save_state()
            bar.stretch(0.01, 1, about_edge=DOWN)
            self.play(
                Restore(bar),
                FadeIn(label),
                run_time=0.3
            )
        
        self.wait(1)
        
        # Highlight max value
        max_idx = values.index(max(values))
        highlight = SurroundingRectangle(bars[max_idx], color=YELLOW, buff=0.1)
        max_text = Text("Maximum", font_size=18, color=YELLOW)
        max_text.next_to(highlight, UP, buff=0.3)
        
        self.play(Create(highlight), Write(max_text))
        self.wait(1)
        
        # Line graph overlay
        points = [axes.c2p(i + 0.5, val) for i, val in enumerate(values)]
        line_graph = VGroup()
        
        for i in range(len(points) - 1):
            line = Line(points[i], points[i + 1], color=WHITE, stroke_width=3)
            line_graph.add(line)
        
        dots = VGroup(*[Dot(p, color=WHITE, radius=0.08) for p in points])
        
        self.play(Create(line_graph), *[GrowFromCenter(d) for d in dots])
        
        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects])
'''

    @staticmethod
    def tree_diagram(nodes: List[Dict[str, Any]] = None, title: str = "Hierarchical Structure") -> str:
        """Generate a tree/hierarchy diagram"""
        title = title.replace('"', '\\"')
        
        return f'''from manim import *

class TreeDiagramAnimation(Scene):
    def construct(self):
        # Title
        title = Text("{title}", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        
        # Root node
        root = Circle(radius=0.35, color=GOLD, fill_opacity=0.7)
        root.shift(UP * 1.5)
        root_label = Text("Root", font_size=18)
        root_label.move_to(root)
        
        self.play(GrowFromCenter(root), Write(root_label))
        
        # Level 1 - 3 children
        level1 = VGroup()
        level1_labels = VGroup()
        l1_names = ["A", "B", "C"]
        l1_colors = [RED, GREEN, BLUE]
        
        for i, (name, color) in enumerate(zip(l1_names, l1_colors)):
            node = Circle(radius=0.3, color=color, fill_opacity=0.6)
            node.shift(DOWN * 0.3 + LEFT * (3 - i * 3))
            label = Text(name, font_size=16)
            label.move_to(node)
            level1.add(node)
            level1_labels.add(label)
        
        # Connect root to level 1
        l1_edges = VGroup()
        for node in level1:
            edge = Line(root.get_bottom(), node.get_top(), color=GRAY, stroke_width=2)
            l1_edges.add(edge)
        
        self.play(*[Create(e) for e in l1_edges])
        self.play(
            *[GrowFromCenter(n) for n in level1],
            *[Write(l) for l in level1_labels],
            run_time=0.5
        )
        
        # Level 2 - 2 children per Level 1 node
        level2 = VGroup()
        level2_labels = VGroup()
        l2_edges = VGroup()
        l2_idx = 1
        
        for parent in level1[:2]:  # Only first 2 parents to avoid clutter
            for j in range(2):
                node = Circle(radius=0.25, color=PURPLE, fill_opacity=0.5)
                offset = LEFT * 0.8 if j == 0 else RIGHT * 0.8
                node.next_to(parent, DOWN, buff=0.8).shift(offset * 0.6)
                label = Text(str(l2_idx), font_size=14)
                label.move_to(node)
                
                edge = Line(parent.get_bottom(), node.get_top(), color=GRAY, stroke_width=1.5)
                
                level2.add(node)
                level2_labels.add(label)
                l2_edges.add(edge)
                l2_idx += 1
        
        self.play(*[Create(e) for e in l2_edges], run_time=0.4)
        self.play(
            *[GrowFromCenter(n) for n in level2],
            *[Write(l) for l in level2_labels],
            run_time=0.4
        )
        
        self.wait(1)
        
        # Highlight a path
        path_nodes = [root, level1[0], level2[0]]
        for node in path_nodes:
            self.play(
                node.animate.set_stroke(YELLOW, width=4),
                run_time=0.2
            )
        
        self.wait(1)
        self.play(*[FadeOut(mob) for mob in self.mobjects])
'''

    @staticmethod
    def venn_diagram(sets: List[str] = None, title: str = "Concept Relationships") -> str:
        """Generate a Venn diagram showing overlapping concepts"""
        sets = sets or ["Set A", "Set B", "Set C"]
        title = title.replace('"', '\\"')
        
        return f'''from manim import *

class VennDiagramAnimation(Scene):
    def construct(self):
        # Title
        title = Text("{title}", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))
        
        # Create circles
        radius = 1.5
        circle_a = Circle(radius=radius, color=RED, fill_opacity=0.3, stroke_width=3)
        circle_b = Circle(radius=radius, color=BLUE, fill_opacity=0.3, stroke_width=3)
        circle_c = Circle(radius=radius, color=GREEN, fill_opacity=0.3, stroke_width=3)
        
        # Position circles
        circle_a.shift(LEFT * 1 + UP * 0.5)
        circle_b.shift(RIGHT * 1 + UP * 0.5)
        circle_c.shift(DOWN * 0.8)
        
        # Labels
        label_a = Text("Concept A", font_size=20, color=RED)
        label_b = Text("Concept B", font_size=20, color=BLUE)
        label_c = Text("Concept C", font_size=20, color=GREEN)
        
        label_a.next_to(circle_a, UP + LEFT, buff=0.1)
        label_b.next_to(circle_b, UP + RIGHT, buff=0.1)
        label_c.next_to(circle_c, DOWN, buff=0.1)
        
        # Animate circles appearing
        self.play(
            GrowFromCenter(circle_a),
            Write(label_a),
            run_time=0.6
        )
        self.play(
            GrowFromCenter(circle_b),
            Write(label_b),
            run_time=0.6
        )
        self.play(
            GrowFromCenter(circle_c),
            Write(label_c),
            run_time=0.6
        )
        
        self.wait(0.5)
        
        # Highlight intersection
        intersection = Intersection(circle_a, circle_b, color=PURPLE, fill_opacity=0.5)
        inter_label = Text("A+B", font_size=16, color=PURPLE)
        inter_label.move_to(UP * 0.5)
        
        self.play(DrawBorderThenFill(intersection), Write(inter_label))
        self.wait(0.5)
        
        # Center intersection (all three)
        center_dot = Dot(color=YELLOW, radius=0.15)
        center_dot.move_to(DOWN * 0.1)
        center_label = Text("Core", font_size=14, color=YELLOW)
        center_label.next_to(center_dot, DOWN, buff=0.1)
        
        self.play(GrowFromCenter(center_dot), Write(center_label))
        
        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects])
'''

    @staticmethod
    def state_machine(states: List[str] = None, title: str = "State Transitions") -> str:
        """Generate a state machine/automaton diagram"""
        states = states or ["Start", "Process", "Validate", "End"]
        states_str = str(states)
        title = title.replace('"', '\\"')
        
        return f'''from manim import *

class StateMachineAnimation(Scene):
    def construct(self):
        # Title
        title = Text("{title}", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))
        
        states = {states_str}
        
        # Create state circles
        circles = VGroup()
        labels = VGroup()
        colors = [GREEN, BLUE, ORANGE, RED]
        
        for i, state in enumerate(states[:4]):
            circle = Circle(radius=0.5, color=colors[i], fill_opacity=0.4, stroke_width=3)
            label = Text(state[:8], font_size=16)
            circles.add(circle)
            labels.add(label)
        
        # Arrange in a square pattern
        circles[0].shift(LEFT * 2.5 + UP * 1)
        circles[1].shift(RIGHT * 2.5 + UP * 1) if len(circles) > 1 else None
        circles[2].shift(RIGHT * 2.5 + DOWN * 1.5) if len(circles) > 2 else None
        circles[3].shift(LEFT * 2.5 + DOWN * 1.5) if len(circles) > 3 else None
        
        for label, circle in zip(labels, circles):
            label.move_to(circle)
        
        # Animate states
        for circle, label in zip(circles, labels):
            self.play(GrowFromCenter(circle), Write(label), run_time=0.4)
        
        # Create transition arrows
        arrows = VGroup()
        if len(circles) >= 2:
            arr1 = Arrow(circles[0].get_right(), circles[1].get_left(), buff=0.1, color=WHITE)
            arrows.add(arr1)
        if len(circles) >= 3:
            arr2 = Arrow(circles[1].get_bottom(), circles[2].get_top(), buff=0.1, color=WHITE)
            arrows.add(arr2)
        if len(circles) >= 4:
            arr3 = Arrow(circles[2].get_left(), circles[3].get_right(), buff=0.1, color=WHITE)
            arrows.add(arr3)
            arr4 = CurvedArrow(circles[3].get_top(), circles[0].get_bottom(), angle=-TAU/4, color=YELLOW)
            arrows.add(arr4)
        
        for arrow in arrows:
            self.play(GrowArrow(arrow), run_time=0.3)
        
        self.wait(0.5)
        
        # Animate state transition
        highlight = Circle(radius=0.6, color=YELLOW, stroke_width=4)
        for i, circle in enumerate(circles):
            highlight.move_to(circle)
            self.play(Create(highlight), run_time=0.2)
            self.play(
                circle.animate.set_fill(YELLOW, opacity=0.6),
                run_time=0.2
            )
            self.play(
                circle.animate.set_fill(colors[i], opacity=0.4),
                FadeOut(highlight),
                run_time=0.2
            )
        
        self.wait(1)
        self.play(*[FadeOut(mob) for mob in self.mobjects])
'''

    @staticmethod
    def process_pipeline(stages: List[str], title: str = "Processing Pipeline") -> str:
        """Generate a horizontal process pipeline diagram"""
        stages_str = str(stages)
        title = title.replace('"', '\\"')
        
        return f'''from manim import *

class ProcessPipelineAnimation(Scene):
    def construct(self):
        # Title
        title = Text("{title}", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))
        
        stages = {stages_str}
        
        # Create stage boxes
        boxes = VGroup()
        labels = VGroup()
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        
        for i, stage in enumerate(stages[:6]):
            box = RoundedRectangle(
                width=2, height=1.2, corner_radius=0.1,
                color=colors[i % len(colors)], fill_opacity=0.4
            )
            label = Text(stage[:12], font_size=18)
            label.move_to(box)
            boxes.add(box)
            labels.add(label)
        
        # Arrange horizontally
        boxes.arrange(RIGHT, buff=0.6)
        boxes.move_to(ORIGIN)
        
        for label, box in zip(labels, boxes):
            label.move_to(box)
        
        # Animate boxes appearing
        for box, label in zip(boxes, labels):
            self.play(
                DrawBorderThenFill(box),
                Write(label),
                run_time=0.4
            )
        
        # Add arrows
        arrows = VGroup()
        for i in range(len(boxes) - 1):
            arrow = Arrow(
                boxes[i].get_right(), boxes[i+1].get_left(),
                buff=0.1, color=WHITE, stroke_width=3
            )
            arrows.add(arrow)
            self.play(GrowArrow(arrow), run_time=0.2)
        
        self.wait(1)
        
        # Data flow animation
        dot = Dot(color=YELLOW, radius=0.15)
        dot.move_to(boxes[0].get_left() + LEFT*0.5)
        self.play(FadeIn(dot))
        
        for box in boxes:
            self.play(
                dot.animate.move_to(box.get_center()),
                box.animate.set_fill(YELLOW, opacity=0.6),
                run_time=0.4
            )
            self.play(
                box.animate.set_fill(box.get_color(), opacity=0.4),
                run_time=0.2
            )
        
        self.play(
            dot.animate.move_to(boxes[-1].get_right() + RIGHT*0.5),
            run_time=0.3
        )
        self.play(FadeOut(dot))
        
        self.wait(1)
        self.play(*[FadeOut(mob) for mob in self.mobjects])
'''

    # === QUANTUM PHYSICS TEMPLATES ===
    # These are delegated to the specialized quantum templates module
    
    @staticmethod
    def quantum_entanglement(title: str = "Quantum Entanglement", particles: int = 2) -> str:
        """Generate animation showing quantum entanglement between particles."""
        return quantum_templates.quantum_entanglement(title, particles)
    
    @staticmethod
    def superposition_state(title: str = "Quantum Superposition") -> str:
        """Generate animation showing quantum superposition."""
        return quantum_templates.superposition_state(title)
    
    @staticmethod
    def wave_function_collapse(title: str = "Wave Function Collapse") -> str:
        """Generate animation showing wave function collapse upon measurement."""
        return quantum_templates.wave_function_collapse(title)
    
    @staticmethod
    def bell_inequality(title: str = "Bell's Inequality Test") -> str:
        """Generate animation explaining Bell's inequality and quantum non-locality."""
        return quantum_templates.bell_inequality(title)
    
    @staticmethod
    def quantum_teleportation(title: str = "Quantum Teleportation") -> str:
        """Generate animation showing quantum teleportation protocol."""
        return quantum_templates.quantum_teleportation(title)
    
    @staticmethod
    def quantum_decoherence(title: str = "Quantum Decoherence") -> str:
        """Generate animation showing decoherence effects."""
        return quantum_templates.quantum_decoherence(title)
    
    @staticmethod
    def quantum_tunneling(title: str = "Quantum Tunneling") -> str:
        """Generate animation showing quantum tunneling through a barrier."""
        return quantum_templates.quantum_tunneling(title)
    
    @staticmethod
    def quantum_interference(title: str = "Quantum Interference") -> str:
        """Generate animation showing double-slit quantum interference."""
        return quantum_templates.quantum_interference(title)
    
    @staticmethod
    def bloch_sphere(title: str = "Bloch Sphere - Qubit State") -> str:
        """Generate animation showing Bloch sphere representation of a qubit."""
        return quantum_templates.bloch_sphere(title)
    
    @staticmethod
    def epr_paradox(title: str = "EPR Paradox") -> str:
        """Generate animation explaining the Einstein-Podolsky-Rosen paradox."""
        return quantum_templates.epr_paradox(title)
    
    @staticmethod
    def quantum_measurement(title: str = "Quantum Measurement Problem") -> str:
        """Generate animation explaining the measurement problem."""
        return quantum_templates.quantum_measurement(title)


# Export templates
templates = AnimationTemplates()

"""
Pre-built Animation Templates
Reusable animation components for research paper visualization
"""
from typing import List, Dict, Any


class AnimationTemplates:
    """Collection of pre-built Manim animation templates"""
    
    @staticmethod
    def title_slide(title: str, authors: List[str] = None) -> str:
        """Generate title slide animation"""
        authors_str = str(authors or [])
        title = title.replace('"', '\\"')
        
        return f'''from manim import *

class TitleSlide(Scene):
    def construct(self):
        # Background gradient effect
        background = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color=[BLUE_E, BLACK],
            fill_opacity=1
        )
        self.add(background)
        
        # Main title
        title_text = "{title}"
        
        # Split long titles
        if len(title_text) > 50:
            words = title_text.split()
            mid = len(words) // 2
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:])
            title = VGroup(
                Text(line1, font_size=38, color=WHITE),
                Text(line2, font_size=38, color=WHITE)
            )
            title.arrange(DOWN, buff=0.3)
        else:
            title = Text(title_text, font_size=42, color=WHITE)
        
        # Animate title
        self.play(Write(title), run_time=2)
        self.wait(1)
        
        # Authors
        authors = {authors_str}
        if authors:
            author_text = Text(
                ", ".join(authors[:3]) + ("..." if len(authors) > 3 else ""),
                font_size=24,
                color=GRAY_B
            )
            author_text.next_to(title, DOWN, buff=0.8)
            self.play(FadeIn(author_text, shift=UP))
            self.wait(1)
        
        # Subtitle
        subtitle = Text("Introduction Overview", font_size=28, color=BLUE_B)
        subtitle.to_edge(DOWN, buff=1)
        self.play(Write(subtitle))
        
        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects if mob != background])
'''

    @staticmethod
    def bullet_points(title: str, points: List[str], color: str = "BLUE") -> str:
        """Generate bullet points animation"""
        points_str = str(points)
        title = title.replace('"', '\\"')
        
        return f'''from manim import *

class BulletPointsAnimation(Scene):
    def construct(self):
        # Title
        title = Text("{title}", font_size=40, color={color})
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        # Bullet points
        points = {points_str}
        bullets = VGroup()
        
        for point in points:
            bullet = Text(f"• {{point[:60]}}", font_size=26)
            bullets.add(bullet)
        
        bullets.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        bullets.next_to(title, DOWN, buff=0.8)
        bullets.to_edge(LEFT, buff=1)
        
        # Animate bullets one by one
        for bullet in bullets:
            self.play(FadeIn(bullet, shift=RIGHT), run_time=0.5)
            self.wait(0.5)
        
        self.wait(2)
        
        # Highlight effect
        for bullet in bullets:
            self.play(
                bullet.animate.set_color(YELLOW),
                rate_func=there_and_back,
                run_time=0.3
            )
        
        self.wait(1)
        self.play(FadeOut(title), FadeOut(bullets))
'''

    @staticmethod
    def flow_diagram(steps: List[str], title: str = "Process Flow") -> str:
        """Generate a flow diagram animation"""
        steps_str = str(steps)
        title = title.replace('"', '\\"')
        
        return f'''from manim import *

class FlowDiagramAnimation(Scene):
    def construct(self):
        title = Text("{title}", font_size=36, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))
        
        steps = {steps_str}
        
        # Create boxes for each step
        boxes = VGroup()
        arrows = VGroup()
        
        colors = [BLUE, GREEN, YELLOW, ORANGE, RED, PURPLE]
        
        for i, step in enumerate(steps[:6]):  # Max 6 steps
            box = RoundedRectangle(
                corner_radius=0.2,
                width=2.5,
                height=1,
                fill_color=colors[i % len(colors)],
                fill_opacity=0.3,
                stroke_color=colors[i % len(colors)]
            )
            
            text = Text(step[:20], font_size=18)
            text.move_to(box)
            
            group = VGroup(box, text)
            boxes.add(group)
        
        # Arrange boxes
        if len(boxes) <= 3:
            boxes.arrange(RIGHT, buff=1)
        else:
            top_row = VGroup(*boxes[:3])
            bottom_row = VGroup(*boxes[3:])
            top_row.arrange(RIGHT, buff=1)
            bottom_row.arrange(RIGHT, buff=1)
            VGroup(top_row, bottom_row).arrange(DOWN, buff=1)
        
        boxes.next_to(title, DOWN, buff=1)
        
        # Animate boxes appearing
        for box in boxes:
            self.play(Create(box[0]), Write(box[1]), run_time=0.5)
        
        # Add arrows between boxes
        for i in range(len(boxes) - 1):
            if i < 2 or (i >= 3 and i < 5):
                arrow = Arrow(
                    boxes[i].get_right(),
                    boxes[i+1].get_left(),
                    buff=0.1,
                    color=WHITE
                )
            else:
                arrow = Arrow(
                    boxes[i].get_bottom(),
                    boxes[i+1].get_top(),
                    buff=0.1,
                    color=WHITE
                )
            arrows.add(arrow)
            self.play(Create(arrow), run_time=0.3)
        
        self.wait(3)
        self.play(FadeOut(boxes), FadeOut(arrows), FadeOut(title))
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
        """Generate a neural network diagram animation"""
        layers = layers or [3, 4, 4, 2]
        layers_str = str(layers)
        title = title.replace('"', '\\"')
        
        return f'''from manim import *

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
        
        # Create nodes
        for layer_idx, size in enumerate(layer_sizes):
            layer = VGroup()
            x_pos = start_x + layer_idx * layer_spacing
            color = layer_colors[layer_idx % len(layer_colors)]
            
            for i in range(size):
                y_pos = (i - (size - 1) / 2) * 0.9
                node = Circle(radius=0.25, color=color, fill_opacity=0.6)
                node.move_to([x_pos, y_pos - 0.5, 0])
                layer.add(node)
            
            layers_list.append(layer)
            all_nodes.add(*layer)
        
        # Animate nodes appearing layer by layer
        for layer in layers_list:
            self.play(
                *[GrowFromCenter(node) for node in layer],
                run_time=0.5
            )
        
        # Create and animate edges
        for i in range(len(layers_list) - 1):
            layer_edges = VGroup()
            for node1 in layers_list[i]:
                for node2 in layers_list[i + 1]:
                    edge = Line(
                        node1.get_center(), node2.get_center(),
                        color=GRAY, stroke_opacity=0.4, stroke_width=1
                    )
                    layer_edges.add(edge)
            all_edges.add(layer_edges)
            self.play(Create(layer_edges), run_time=0.4)
        
        self.wait(1)
        
        # Add layer labels
        layer_names = ["Input", "Hidden", "Hidden", "Output"]
        for i, (layer, name) in enumerate(zip(layers_list, layer_names[:len(layers_list)])):
            label = Text(name, font_size=18, color=WHITE)
            label.next_to(layer, DOWN, buff=0.3)
            self.play(FadeIn(label), run_time=0.3)
        
        self.wait(2)
        
        # Signal flow animation
        for i in range(len(layers_list) - 1):
            self.play(
                *[node.animate.set_fill(YELLOW, opacity=0.8) for node in layers_list[i]],
                run_time=0.3
            )
            self.play(
                *[node.animate.set_fill(layers_list[i][0].get_color(), opacity=0.6) for node in layers_list[i]],
                run_time=0.3
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


# Export templates
templates = AnimationTemplates()

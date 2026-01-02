"""
Quantum Physics Animation Templates
Specialized templates for quantum entanglement, superposition, and related quantum phenomena
"""
from typing import List, Dict, Any


def _sanitize_title(title: str, default: str = "Quantum Animation") -> str:
    """Sanitize title for safe string embedding in generated code."""
    if not title:
        return default
    # Remove problematic characters and limit length
    title = title.replace('"', "'").replace('\\', '').replace('\n', ' ')
    title = ''.join(c for c in title if ord(c) < 128)  # ASCII only
    title = title.strip()[:50]
    return title if title else default


class QuantumAnimationTemplates:
    """Collection of quantum physics-specific Manim animation templates"""
    
    @staticmethod
    def quantum_entanglement(title: str = "Quantum Entanglement", particles: int = 2) -> str:
        """
        Generate animation showing quantum entanglement between particles.
        Shows correlated spins/states of entangled particles.
        """
        # Sanitize title for safe string embedding
        title = title.replace('"', "'").replace('\\', '')[:50]
        if not title:
            title = "Quantum Entanglement"
        
        return f'''from manim import *
import numpy as np

class QuantumEntanglementAnimation(Scene):
    def construct(self):
        # Title
        title_text = Text("{title}", font_size=32, color=BLUE)
        title_text.to_edge(UP, buff=0.4)
        self.play(Write(title_text), run_time=1)
        
        # Create two entangled particles
        particle_a = VGroup()
        nucleus_a = Circle(radius=0.3, color=BLUE, fill_opacity=0.8)
        glow_a = Circle(radius=0.5, color=BLUE, fill_opacity=0.2)
        particle_a.add(glow_a, nucleus_a)
        particle_a.shift(LEFT * 3)
        
        particle_b = VGroup()
        nucleus_b = Circle(radius=0.3, color=RED, fill_opacity=0.8)
        glow_b = Circle(radius=0.5, color=RED, fill_opacity=0.2)
        particle_b.add(glow_b, nucleus_b)
        particle_b.shift(RIGHT * 3)
        
        # Labels
        label_a = Text("Particle A", font_size=18, color=BLUE)
        label_a.next_to(particle_a, DOWN, buff=0.3)
        label_b = Text("Particle B", font_size=18, color=RED)
        label_b.next_to(particle_b, DOWN, buff=0.3)
        
        self.play(
            GrowFromCenter(particle_a),
            GrowFromCenter(particle_b),
            run_time=1
        )
        self.play(Write(label_a), Write(label_b), run_time=0.5)
        
        # Show entanglement connection
        entangle_line = DashedLine(
            particle_a.get_center(), 
            particle_b.get_center(),
            color=YELLOW,
            dash_length=0.2
        )
        entangle_text = Text("Entangled", font_size=18, color=YELLOW)
        entangle_text.move_to(ORIGIN).shift(UP * 0.5)
        
        self.play(Create(entangle_line), Write(entangle_text), run_time=1)
        
        # Animate spin states - create spin arrows
        spin_a = Arrow(
            start=particle_a.get_center() + DOWN * 0.3,
            end=particle_a.get_center() + UP * 0.3,
            color=WHITE, stroke_width=4, buff=0
        )
        spin_b = Arrow(
            start=particle_b.get_center() + UP * 0.3,
            end=particle_b.get_center() + DOWN * 0.3,
            color=WHITE, stroke_width=4, buff=0
        )
        
        self.play(GrowArrow(spin_a), GrowArrow(spin_b), run_time=0.5)
        
        # Add state labels
        state_a = Text("Up", font_size=14, color=GREEN)
        state_a.next_to(particle_a, UP, buff=0.6)
        state_b = Text("Down", font_size=14, color=GREEN)
        state_b.next_to(particle_b, UP, buff=0.6)
        
        self.play(FadeIn(state_a), FadeIn(state_b), run_time=0.5)
        self.wait(0.5)
        
        # Show correlated flip - when one changes, other changes too
        flip_text = Text("Measuring Particle A...", font_size=20, color=YELLOW)
        flip_text.to_edge(DOWN, buff=0.8)
        self.play(Write(flip_text), run_time=0.5)
        
        # Measurement flash on particle A
        flash_a = Circle(radius=0.8, color=WHITE, stroke_width=2)
        flash_a.move_to(particle_a)
        self.play(
            Create(flash_a),
            flash_a.animate.scale(2).set_stroke(opacity=0),
            run_time=0.5
        )
        self.remove(flash_a)
        
        # Both spins flip instantaneously - simpler animation
        new_spin_a = Arrow(
            start=particle_a.get_center() + UP * 0.3,
            end=particle_a.get_center() + DOWN * 0.3,
            color=WHITE, stroke_width=4, buff=0
        )
        new_spin_b = Arrow(
            start=particle_b.get_center() + DOWN * 0.3,
            end=particle_b.get_center() + UP * 0.3,
            color=WHITE, stroke_width=4, buff=0
        )
        
        new_state_a = Text("Down", font_size=14, color=GREEN)
        new_state_a.next_to(particle_a, UP, buff=0.6)
        new_state_b = Text("Up", font_size=14, color=GREEN)
        new_state_b.next_to(particle_b, UP, buff=0.6)
        
        self.play(
            Transform(spin_a, new_spin_a),
            Transform(spin_b, new_spin_b),
            Transform(state_a, new_state_a),
            Transform(state_b, new_state_b),
            run_time=0.5
        )
        
        # Highlight instant correlation
        correlation_text = Text("Instant Correlation!", font_size=22, color=YELLOW)
        correlation_text.to_edge(DOWN, buff=0.8)
        self.play(Transform(flip_text, correlation_text), run_time=0.5)
        
        # Pulsing effect to show connection
        for _ in range(2):
            self.play(
                particle_a.animate.scale(1.15),
                particle_b.animate.scale(1.15),
                run_time=0.25
            )
            self.play(
                particle_a.animate.scale(1/1.15),
                particle_b.animate.scale(1/1.15),
                run_time=0.25
            )
        
        self.wait(0.5)
        
        # Clean exit
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not None], run_time=0.8)
'''

    @staticmethod
    def superposition_state(title: str = "Quantum Superposition") -> str:
        """
        Generate animation showing quantum superposition - particle existing in multiple states.
        """
        # Sanitize title
        title = title.replace('"', "'").replace('\\', '')[:50]
        if not title:
            title = "Quantum Superposition"
        
        return f'''from manim import *
import numpy as np

class SuperpositionAnimation(Scene):
    def construct(self):
        # Title
        title_text = Text("{title}", font_size=32, color=BLUE)
        title_text.to_edge(UP, buff=0.4)
        self.play(Write(title_text), run_time=1)
        
        # Classical state - single definite position
        classical_label = Text("Classical:", font_size=24, color=WHITE)
        classical_label.shift(LEFT * 4 + UP * 1.5)
        
        classical_particle = Circle(radius=0.3, color=GREEN, fill_opacity=0.8)
        classical_particle.next_to(classical_label, DOWN, buff=0.5)
        
        self.play(Write(classical_label), GrowFromCenter(classical_particle))
        
        # Quantum state - superposition cloud
        quantum_label = Text("Quantum:", font_size=24, color=WHITE)
        quantum_label.shift(RIGHT * 2 + UP * 1.5)
        
        self.play(Write(quantum_label))
        
        # Create probability cloud
        quantum_states = VGroup()
        positions = [RIGHT * 2 + UP * 0.3, RIGHT * 2.5 + DOWN * 0.5, RIGHT * 1.5 + DOWN * 0.3, 
                     RIGHT * 2.3 + UP * 0.1, RIGHT * 1.8 + DOWN * 0.1]
        opacities = [0.7, 0.5, 0.4, 0.6, 0.3]
        
        for pos, opacity in zip(positions, opacities):
            state = Circle(radius=0.25, color=PURPLE, fill_opacity=opacity, stroke_opacity=0.5)
            state.move_to(pos)
            quantum_states.add(state)
        
        # Surrounding probability cloud
        cloud = Circle(radius=1.2, color=PURPLE, fill_opacity=0.1, stroke_opacity=0.3)
        cloud.move_to(RIGHT * 2)
        
        self.play(FadeIn(cloud))
        self.play(LaggedStart(*[GrowFromCenter(s) for s in quantum_states], lag_ratio=0.1))
        
        # Animate the superposition - states oscillating
        state_label = Text("Multiple states simultaneously", font_size=18, color=YELLOW)
        state_label.next_to(cloud, DOWN, buff=0.3)
        self.play(Write(state_label))
        
        # Oscillation animation
        for _ in range(2):
            for state in quantum_states:
                self.play(
                    state.animate.scale(1.3).set_opacity(0.9),
                    run_time=0.15
                )
                self.play(
                    state.animate.scale(1/1.3).set_opacity(state.get_fill_opacity()),
                    run_time=0.15
                )
        
        # Measurement - collapse to single state
        measure_text = Text("Measurement", font_size=24, color=RED)
        measure_text.to_edge(DOWN, buff=0.8)
        self.play(Write(measure_text))
        
        # Flash and collapse
        flash = Circle(radius=0.1, color=WHITE, fill_opacity=1)
        flash.move_to(quantum_states[0])
        
        self.play(
            flash.animate.scale(15).set_opacity(0),
            *[FadeOut(s) for s in quantum_states[1:]],
            quantum_states[0].animate.set_color(GREEN).set_opacity(1),
            FadeOut(cloud),
            run_time=0.8
        )
        
        collapse_text = Text("Collapsed to definite state", font_size=18, color=GREEN)
        collapse_text.next_to(quantum_states[0], DOWN, buff=0.3)
        self.play(Transform(state_label, collapse_text))
        
        self.wait(1)
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not None], run_time=0.8)
'''

    @staticmethod
    def wave_function_collapse(title: str = "Wave Function Collapse") -> str:
        """
        Generate animation showing wave function and its collapse upon measurement.
        """
        title = _sanitize_title(title, "Wave Function Collapse")
        
        return f'''from manim import *
import numpy as np

class WaveFunctionCollapseAnimation(Scene):
    def construct(self):
        # Title
        title_text = Text("{title}", font_size=32, color=BLUE)
        title_text.to_edge(UP, buff=0.4)
        self.play(Write(title_text), run_time=1)
        
        # Create wave function visualization
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-1.5, 1.5, 0.5],
            x_length=8,
            y_length=3,
            axis_config={{"color": GRAY, "stroke_width": 1}},
            tips=False
        )
        axes.shift(DOWN * 0.5)
        
        # Wave function (Gaussian wave packet)
        def wave_func(x, t=0):
            return np.exp(-(x)**2 / 2) * np.cos(4*x - t)
        
        wave = axes.plot(lambda x: wave_func(x), color=PURPLE, stroke_width=3)
        
        # Probability density (square of wave function)
        prob = axes.plot(lambda x: np.exp(-x**2), color=BLUE, fill_opacity=0.3, stroke_width=2)
        
        self.play(Create(axes))
        
        # Labels
        psi_label = Text("Wave Function", font_size=18, color=PURPLE)
        psi_label.next_to(wave, UP, buff=0.1).shift(RIGHT)
        prob_label = Text("Probability", font_size=18, color=BLUE)
        prob_label.next_to(prob, DOWN, buff=0.1)
        
        self.play(Create(wave), Write(psi_label))
        self.wait(0.5)
        self.play(Create(prob), Write(prob_label))
        
        # Animate wave oscillation
        for t in [1, 2, 3]:
            new_wave = axes.plot(lambda x, t=t: wave_func(x, t), color=PURPLE, stroke_width=3)
            self.play(Transform(wave, new_wave), run_time=0.3)
        
        # Measurement
        measure_line = DashedLine(
            axes.c2p(1, -1.5),
            axes.c2p(1, 1.5),
            color=RED,
            dash_length=0.1
        )
        measure_text = Text("Measurement", font_size=20, color=RED)
        measure_text.next_to(measure_line, UP, buff=0.1)
        
        self.play(Create(measure_line), Write(measure_text))
        
        # Wave function collapse - becomes delta function at measurement point
        collapsed_wave = VGroup()
        spike = Line(
            axes.c2p(1, 0),
            axes.c2p(1, 1),
            color=GREEN,
            stroke_width=4
        )
        point = Dot(axes.c2p(1, 1), color=GREEN, radius=0.1)
        collapsed_wave.add(spike, point)
        
        # Flash effect
        flash = Circle(radius=0.1, color=WHITE).move_to(axes.c2p(1, 0))
        
        self.play(
            flash.animate.scale(20).set_opacity(0),
            FadeOut(wave),
            FadeOut(prob),
            run_time=0.5
        )
        
        self.play(
            Create(spike),
            GrowFromCenter(point),
            run_time=0.5
        )
        
        # Result label
        result_text = Text("Particle found at x=1", font_size=22, color=GREEN)
        result_text.to_edge(DOWN, buff=0.8)
        self.play(Write(result_text))
        
        self.wait(1)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not None], run_time=0.8)
'''

    @staticmethod
    def bell_inequality(title: str = "Bell's Inequality Test") -> str:
        """
        Generate animation explaining Bell's inequality and quantum non-locality.
        """
        title = _sanitize_title(title, "Bell's Inequality Test")
        
        return f'''from manim import *
import numpy as np

class BellInequalityAnimation(Scene):
    def construct(self):
        # Title
        title_text = Text("{title}", font_size=32, color=BLUE)
        title_text.to_edge(UP, buff=0.4)
        self.play(Write(title_text), run_time=1)
        
        # Create source in center
        source = VGroup()
        source_core = Circle(radius=0.3, color=YELLOW, fill_opacity=0.8)
        source_glow = Circle(radius=0.5, color=YELLOW, fill_opacity=0.2)
        source.add(source_glow, source_core)
        source_label = Text("Source", font_size=16).next_to(source, DOWN, buff=0.2)
        
        self.play(GrowFromCenter(source), Write(source_label))
        
        # Create two detectors
        detector_a = VGroup()
        det_a_box = Rectangle(width=1.2, height=0.8, color=BLUE, fill_opacity=0.3)
        det_a_box.shift(LEFT * 4)
        det_a_label = Text("Detector A", font_size=16, color=BLUE)
        det_a_label.next_to(det_a_box, UP, buff=0.2)
        detector_a.add(det_a_box, det_a_label)
        
        detector_b = VGroup()
        det_b_box = Rectangle(width=1.2, height=0.8, color=RED, fill_opacity=0.3)
        det_b_box.shift(RIGHT * 4)
        det_b_label = Text("Detector B", font_size=16, color=RED)
        det_b_label.next_to(det_b_box, UP, buff=0.2)
        detector_b.add(det_b_box, det_b_label)
        
        self.play(Create(detector_a), Create(detector_b))
        
        # Angle settings for detectors
        angle_a = Arc(radius=0.4, angle=PI/6, color=BLUE, stroke_width=3)
        angle_a.move_to(det_a_box.get_center() + DOWN * 0.6)
        angle_b = Arc(radius=0.4, angle=PI/4, color=RED, stroke_width=3)
        angle_b.move_to(det_b_box.get_center() + DOWN * 0.6)
        
        angle_a_label = Text("0 deg", font_size=14, color=BLUE)
        angle_a_label.next_to(angle_a, DOWN, buff=0.1)
        angle_b_label = Text("45 deg", font_size=14, color=RED)
        angle_b_label.next_to(angle_b, DOWN, buff=0.1)
        
        self.play(Create(angle_a), Create(angle_b), Write(angle_a_label), Write(angle_b_label))
        
        # Emit entangled photon pairs
        for trial in range(3):
            photon_a = Dot(color=BLUE, radius=0.1)
            photon_b = Dot(color=RED, radius=0.1)
            photon_a.move_to(source)
            photon_b.move_to(source)
            
            # Wavy path for photons
            self.play(
                photon_a.animate.move_to(det_a_box.get_center()),
                photon_b.animate.move_to(det_b_box.get_center()),
                run_time=0.5
            )
            
            # Detection flash
            flash_a = Circle(radius=0.2, color=BLUE).move_to(det_a_box)
            flash_b = Circle(radius=0.2, color=RED).move_to(det_b_box)
            
            self.play(
                flash_a.animate.scale(3).set_opacity(0),
                flash_b.animate.scale(3).set_opacity(0),
                FadeOut(photon_a),
                FadeOut(photon_b),
                run_time=0.3
            )
        
        # Show correlation results
        results_label = Text("Correlation Results", font_size=22, color=YELLOW)
        results_label.shift(DOWN * 2)
        
        classical_bar = Rectangle(width=2, height=0.3, color=GREEN, fill_opacity=0.6)
        classical_bar.next_to(results_label, DOWN, buff=0.4).shift(LEFT * 2)
        classical_text = Text("Classical: 0.5", font_size=16, color=GREEN)
        classical_text.next_to(classical_bar, RIGHT, buff=0.2)
        
        quantum_bar = Rectangle(width=2.8, height=0.3, color=PURPLE, fill_opacity=0.6)
        quantum_bar.next_to(classical_bar, DOWN, buff=0.2).align_to(classical_bar, LEFT)
        quantum_text = Text("Quantum: 0.7", font_size=16, color=PURPLE)
        quantum_text.next_to(quantum_bar, RIGHT, buff=0.2)
        
        self.play(Write(results_label))
        self.play(
            GrowFromEdge(classical_bar, LEFT), Write(classical_text),
            run_time=0.5
        )
        self.play(
            GrowFromEdge(quantum_bar, LEFT), Write(quantum_text),
            run_time=0.5
        )
        
        # Conclusion
        conclusion = Text("Quantum exceeds classical limit!", font_size=22, color=YELLOW)
        conclusion.to_edge(DOWN, buff=0.4)
        self.play(Write(conclusion))
        
        self.wait(1)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not None], run_time=0.8)
'''

    @staticmethod
    def quantum_teleportation(title: str = "Quantum Teleportation") -> str:
        """
        Generate animation showing the quantum teleportation protocol.
        """
        title = _sanitize_title(title, "Quantum Teleportation")
        
        return f'''from manim import *
import numpy as np

class QuantumTeleportationAnimation(Scene):
    def construct(self):
        # Title
        title_text = Text("{title}", font_size=32, color=BLUE)
        title_text.to_edge(UP, buff=0.4)
        self.play(Write(title_text), run_time=1)
        
        # Three participants
        alice = VGroup()
        alice_circle = Circle(radius=0.4, color=BLUE, fill_opacity=0.5)
        alice_label = Text("Alice", font_size=18, color=BLUE)
        alice_label.next_to(alice_circle, DOWN, buff=0.2)
        alice.add(alice_circle, alice_label)
        alice.shift(LEFT * 4)
        
        bob = VGroup()
        bob_circle = Circle(radius=0.4, color=RED, fill_opacity=0.5)
        bob_label = Text("Bob", font_size=18, color=RED)
        bob_label.next_to(bob_circle, DOWN, buff=0.2)
        bob.add(bob_circle, bob_label)
        bob.shift(RIGHT * 4)
        
        self.play(Create(alice), Create(bob))
        
        # Alice has quantum state to teleport
        quantum_state = VGroup()
        state_circle = Circle(radius=0.2, color=YELLOW, fill_opacity=0.8)
        state_arrow = Arrow(ORIGIN, UP * 0.4, color=WHITE, stroke_width=3, buff=0)
        state_arrow.move_to(state_circle)
        state_label = Text("Unknown State", font_size=14, color=YELLOW)
        state_label.next_to(state_circle, UP, buff=0.3)
        quantum_state.add(state_circle, state_arrow, state_label)
        quantum_state.next_to(alice_circle, UP, buff=0.3)
        
        self.play(GrowFromCenter(quantum_state))
        
        # Entangled pair shared between Alice and Bob
        entangled_a = Circle(radius=0.15, color=PURPLE, fill_opacity=0.8)
        entangled_b = Circle(radius=0.15, color=PURPLE, fill_opacity=0.8)
        entangled_a.move_to(alice_circle.get_center() + DOWN * 1)
        entangled_b.move_to(bob_circle.get_center() + DOWN * 1)
        
        entangle_line = DashedLine(entangled_a, entangled_b, color=PURPLE, dash_length=0.15)
        entangle_label = Text("Entangled Pair", font_size=14, color=PURPLE)
        entangle_label.move_to(ORIGIN + DOWN * 1.5)
        
        self.play(
            GrowFromCenter(entangled_a),
            GrowFromCenter(entangled_b),
            Create(entangle_line),
            Write(entangle_label)
        )
        
        # Step 1: Alice performs Bell measurement
        step1 = Text("Step 1: Bell Measurement", font_size=18, color=GREEN)
        step1.to_edge(LEFT, buff=0.5).shift(DOWN * 2.5)
        self.play(Write(step1))
        
        # Measurement animation
        measurement_ring = Circle(radius=0.5, color=GREEN, stroke_width=3)
        measurement_ring.move_to(alice_circle)
        
        self.play(Create(measurement_ring))
        self.play(
            quantum_state.animate.move_to(entangled_a),
            run_time=0.5
        )
        
        # Flash for measurement
        flash = Circle(radius=0.3, color=WHITE).move_to(entangled_a)
        self.play(flash.animate.scale(5).set_opacity(0), run_time=0.4)
        
        # Step 2: Classical communication
        step2 = Text("Step 2: Classical Channel", font_size=18, color=ORANGE)
        step2.next_to(step1, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(step2))
        
        # Classical message travels
        message = VGroup()
        msg_rect = Rectangle(width=0.4, height=0.2, color=ORANGE, fill_opacity=0.8)
        msg_label = Text("01", font_size=10, color=WHITE)
        msg_label.move_to(msg_rect)
        message.add(msg_rect, msg_label)
        message.move_to(alice_circle)
        
        # Curved path for classical message
        self.play(GrowFromCenter(message))
        self.play(message.animate.move_to(bob_circle), run_time=1)
        self.play(FadeOut(message))
        
        # Step 3: Bob applies correction
        step3 = Text("Step 3: Correction", font_size=18, color=RED)
        step3.next_to(step2, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(step3))
        
        # Bob's particle transforms
        self.play(
            entangled_b.animate.set_color(YELLOW).scale(1.5),
            run_time=0.5
        )
        
        # Teleported state appears at Bob
        teleported_state = VGroup()
        t_circle = Circle(radius=0.2, color=YELLOW, fill_opacity=0.8)
        t_arrow = Arrow(ORIGIN, UP * 0.4, color=WHITE, stroke_width=3, buff=0)
        t_arrow.move_to(t_circle)
        teleported_state.add(t_circle, t_arrow)
        teleported_state.move_to(bob_circle.get_center() + UP * 0.8)
        
        self.play(
            Transform(entangled_b, teleported_state),
            run_time=0.5
        )
        
        # Success label
        success = Text("State Teleported!", font_size=24, color=YELLOW)
        success.to_edge(DOWN, buff=0.4)
        self.play(Write(success))
        
        # Final pulse effect
        pulse = Circle(radius=0.5, color=YELLOW).move_to(teleported_state)
        self.play(pulse.animate.scale(4).set_opacity(0), run_time=0.5)
        
        self.wait(1)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not None], run_time=0.8)
'''

    @staticmethod
    def quantum_decoherence(title: str = "Quantum Decoherence") -> str:
        """
        Generate animation showing decoherence - loss of quantum coherence.
        """
        title = _sanitize_title(title, "Quantum Decoherence")
        
        return f'''from manim import *
import numpy as np

class DecoherenceAnimation(Scene):
    def construct(self):
        # Title
        title_text = Text("{title}", font_size=32, color=BLUE)
        title_text.to_edge(UP, buff=0.4)
        self.play(Write(title_text), run_time=1)
        
        # Create coherent quantum state
        coherent_label = Text("Coherent Superposition", font_size=20, color=PURPLE)
        coherent_label.shift(UP * 2)
        self.play(Write(coherent_label))
        
        # Superposition visualization - two states in phase
        state_0 = Circle(radius=0.4, color=BLUE, fill_opacity=0.6)
        state_1 = Circle(radius=0.4, color=RED, fill_opacity=0.6)
        state_0.shift(LEFT * 1.5)
        state_1.shift(RIGHT * 1.5)
        
        # Phase relationship shown by connecting wave
        phase_wave = ParametricFunction(
            lambda t: np.array([t, 0.3*np.sin(4*t), 0]),
            t_range=[-1.5, 1.5],
            color=YELLOW
        )
        
        self.play(GrowFromCenter(state_0), GrowFromCenter(state_1))
        self.play(Create(phase_wave))
        
        # Labels for states
        label_0 = Text("|0>", font_size=20, color=BLUE)
        label_0.next_to(state_0, DOWN, buff=0.2)
        label_1 = Text("|1>", font_size=20, color=RED)
        label_1.next_to(state_1, DOWN, buff=0.2)
        self.play(Write(label_0), Write(label_1))
        
        # Show coherent oscillation
        for _ in range(2):
            self.play(
                state_0.animate.scale(1.2),
                state_1.animate.scale(0.8),
                run_time=0.3
            )
            self.play(
                state_0.animate.scale(1/1.2),
                state_1.animate.scale(1/0.8),
                run_time=0.3
            )
        
        # Environment interaction
        env_label = Text("Environment Interaction", font_size=18, color=RED)
        env_label.to_edge(DOWN, buff=1.5)
        self.play(Write(env_label))
        
        # Environment particles approaching
        env_particles = VGroup()
        for i in range(8):
            angle = i * PI/4
            particle = Dot(color=GRAY, radius=0.08)
            particle.move_to(3 * np.array([np.cos(angle), np.sin(angle), 0]))
            env_particles.add(particle)
        
        self.play(FadeIn(env_particles))
        self.play(
            *[p.animate.move_to(0.8 * np.array([np.cos(i*PI/4), np.sin(i*PI/4), 0])) 
              for i, p in enumerate(env_particles)],
            run_time=1
        )
        
        # Decoherence - phase relationship breaks down
        decohere_label = Text("Decoherence", font_size=24, color=RED)
        decohere_label.shift(UP * 2)
        
        # Phase wave becomes random/noisy
        noisy_wave = VGroup()
        for i in range(20):
            x = -1.5 + i * 0.15
            segment = Line(
                np.array([x, 0.3*np.random.uniform(-1, 1), 0]),
                np.array([x + 0.15, 0.3*np.random.uniform(-1, 1), 0]),
                color=GRAY,
                stroke_opacity=0.5
            )
            noisy_wave.add(segment)
        
        self.play(
            Transform(coherent_label, decohere_label),
            Transform(phase_wave, noisy_wave),
            state_0.animate.set_opacity(0.3),
            state_1.animate.set_opacity(0.3),
            run_time=1
        )
        
        # Final classical mixture
        mixture_label = Text("Classical Mixture", font_size=20, color=GRAY)
        mixture_label.to_edge(DOWN, buff=0.5)
        
        self.play(
            FadeOut(phase_wave),
            state_0.animate.set_color(GRAY),
            state_1.animate.set_color(GRAY),
            Write(mixture_label),
            run_time=0.5
        )
        
        # OR visualization - classical uncertainty
        or_text = Text("Either |0> OR |1>", font_size=18, color=WHITE)
        or_text.move_to(ORIGIN + DOWN * 0.5)
        self.play(Write(or_text))
        
        self.wait(1)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not None], run_time=0.8)
'''

    @staticmethod
    def quantum_tunneling(title: str = "Quantum Tunneling") -> str:
        """
        Generate animation showing quantum tunneling through a barrier.
        """
        title = _sanitize_title(title, "Quantum Tunneling")
        
        return f'''from manim import *
import numpy as np

class QuantumTunnelingAnimation(Scene):
    def construct(self):
        # Title
        title_text = Text("{title}", font_size=32, color=BLUE)
        title_text.to_edge(UP, buff=0.4)
        self.play(Write(title_text), run_time=1)
        
        # Create potential barrier
        barrier = Rectangle(
            width=1,
            height=3,
            color=RED,
            fill_opacity=0.3,
            stroke_width=3
        )
        barrier_label = Text("Barrier", font_size=18, color=RED)
        barrier_label.next_to(barrier, UP, buff=0.2)
        
        self.play(DrawBorderThenFill(barrier), Write(barrier_label))
        
        # Create incoming wave packet
        wave_group = VGroup()
        
        # Wave function visualization
        axes = Axes(
            x_range=[-6, 6, 1],
            y_range=[-1, 1, 0.5],
            x_length=12,
            y_length=2,
            axis_config={{"stroke_opacity": 0}},
            tips=False
        )
        axes.shift(DOWN * 1)
        
        def wave_packet(x, x0=-4, k=3):
            return np.exp(-(x - x0)**2) * np.cos(k * (x - x0))
        
        # Initial wave packet on the left
        wave = axes.plot(
            lambda x: wave_packet(x, -4),
            x_range=[-6, -1],
            color=BLUE,
            stroke_width=3
        )
        
        # Probability cloud for particle
        particle = Circle(radius=0.3, color=BLUE, fill_opacity=0.6)
        particle.move_to(LEFT * 4)
        particle_label = Text("Quantum Particle", font_size=16, color=BLUE)
        particle_label.next_to(particle, DOWN, buff=0.2)
        
        self.play(Create(wave), GrowFromCenter(particle), Write(particle_label))
        
        # Classical approach - particle bounces
        classical_label = Text("Classically: Reflection", font_size=18, color=GREEN)
        classical_label.shift(DOWN * 2.5 + LEFT * 3)
        
        self.play(Write(classical_label))
        
        # Show particle approaching barrier
        self.play(
            particle.animate.move_to(LEFT * 1.5),
            run_time=1
        )
        
        # Particle hits barrier - partial reflection, partial tunneling
        # Split into reflected and transmitted parts
        reflected = particle.copy()
        transmitted = particle.copy()
        transmitted.set_opacity(0.3)
        
        self.play(
            reflected.animate.move_to(LEFT * 4).set_color(GREEN),
            transmitted.animate.move_to(RIGHT * 3).set_color(PURPLE),
            FadeOut(particle),
            run_time=1.5
        )
        
        # Labels for reflected and transmitted
        ref_label = Text("Reflected", font_size=16, color=GREEN)
        ref_label.next_to(reflected, DOWN, buff=0.2)
        trans_label = Text("Tunneled!", font_size=16, color=PURPLE)
        trans_label.next_to(transmitted, DOWN, buff=0.2)
        
        self.play(Write(ref_label), Write(trans_label))
        
        # Highlight tunneling
        tunnel_text = Text("Non-zero probability through barrier!", font_size=20, color=YELLOW)
        tunnel_text.to_edge(DOWN, buff=0.4)
        self.play(Write(tunnel_text))
        
        # Visualize exponential decay inside barrier
        decay_in_barrier = axes.plot(
            lambda x: 0.5 * np.exp(-2 * abs(x)) if abs(x) < 0.5 else 0,
            x_range=[-0.5, 0.5],
            color=YELLOW,
            stroke_width=2
        )
        
        self.play(Create(decay_in_barrier))
        
        # Pulse effect on tunneled particle
        pulse = Circle(radius=0.5, color=PURPLE).move_to(transmitted)
        self.play(pulse.animate.scale(3).set_opacity(0), run_time=0.5)
        
        self.wait(1)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not None], run_time=0.8)
'''

    @staticmethod
    def quantum_interference(title: str = "Quantum Interference") -> str:
        """
        Generate animation showing double-slit quantum interference pattern.
        """
        title = _sanitize_title(title, "Quantum Interference")
        
        return f'''from manim import *
import numpy as np

class QuantumInterferenceAnimation(Scene):
    def construct(self):
        # Title
        title_text = Text("{title}", font_size=32, color=BLUE)
        title_text.to_edge(UP, buff=0.4)
        self.play(Write(title_text), run_time=1)
        
        # Create double slit apparatus
        barrier_top = Rectangle(width=0.2, height=1.5, color=GRAY, fill_opacity=0.8)
        barrier_mid = Rectangle(width=0.2, height=0.5, color=GRAY, fill_opacity=0.8)
        barrier_bot = Rectangle(width=0.2, height=1.5, color=GRAY, fill_opacity=0.8)
        
        barrier_top.shift(UP * 1.75)
        barrier_bot.shift(DOWN * 1.75)
        
        slit_label = Text("Double Slit", font_size=16, color=GRAY)
        slit_label.next_to(barrier_top, UP, buff=0.2)
        
        slits = VGroup(barrier_top, barrier_mid, barrier_bot)
        
        self.play(Create(slits), Write(slit_label))
        
        # Screen on the right
        screen = Rectangle(width=0.1, height=4, color=WHITE, fill_opacity=0.2)
        screen.shift(RIGHT * 4)
        screen_label = Text("Screen", font_size=16, color=WHITE)
        screen_label.next_to(screen, RIGHT, buff=0.2)
        
        self.play(Create(screen), Write(screen_label))
        
        # Source on the left
        source = Dot(color=YELLOW, radius=0.15)
        source.shift(LEFT * 4)
        source_label = Text("Source", font_size=16, color=YELLOW)
        source_label.next_to(source, LEFT, buff=0.2)
        
        self.play(GrowFromCenter(source), Write(source_label))
        
        # Emit particles through both slits
        particles_detected = []
        
        for trial in range(15):
            particle = Dot(color=BLUE, radius=0.08)
            particle.move_to(source)
            
            # Particle travels to slits
            self.play(particle.animate.move_to(ORIGIN), run_time=0.15)
            
            # Split into two paths (superposition through both slits)
            path1 = particle.copy().set_color(BLUE)
            path2 = particle.copy().set_color(RED)
            
            # Positions through slits
            slit1_pos = UP * 0.75
            slit2_pos = DOWN * 0.75
            
            self.play(
                path1.animate.move_to(slit1_pos),
                path2.animate.move_to(slit2_pos),
                FadeOut(particle),
                run_time=0.1
            )
            
            # Interference pattern - more likely at certain positions
            # Calculate landing position based on interference
            phase_diff = trial * 0.4
            y_pos = 1.5 * np.sin(phase_diff) + np.random.uniform(-0.2, 0.2)
            landing = RIGHT * 4 + UP * y_pos
            
            self.play(
                path1.animate.move_to(landing),
                path2.animate.move_to(landing),
                run_time=0.15
            )
            
            # Combine and deposit on screen
            detection = Dot(color=GREEN, radius=0.05)
            detection.move_to(landing)
            particles_detected.append(detection)
            
            self.play(
                FadeOut(path1),
                FadeOut(path2),
                FadeIn(detection),
                run_time=0.05
            )
        
        # Show interference pattern building up
        pattern_label = Text("Interference Pattern", font_size=20, color=GREEN)
        pattern_label.to_edge(DOWN, buff=0.5)
        self.play(Write(pattern_label))
        
        # Highlight bright and dark fringes
        bright = Text("Bright: Constructive", font_size=14, color=GREEN)
        dark = Text("Dark: Destructive", font_size=14, color=RED)
        bright.next_to(pattern_label, UP, buff=0.2).shift(LEFT * 2)
        dark.next_to(pattern_label, UP, buff=0.2).shift(RIGHT * 2)
        
        self.play(Write(bright), Write(dark))
        
        self.wait(1)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not None], run_time=0.8)
'''

    @staticmethod
    def bloch_sphere(title: str = "Bloch Sphere - Qubit State") -> str:
        """
        Generate animation showing the Bloch sphere representation of a qubit.
        """
        title = _sanitize_title(title, "Bloch Sphere Qubit State")
        
        return f'''from manim import *
import numpy as np

class BlochSphereAnimation(ThreeDScene):
    def construct(self):
        # Title
        title_text = Text("{title}", font_size=32, color=BLUE)
        title_text.to_edge(UP, buff=0.4)
        self.add_fixed_in_frame_mobjects(title_text)
        self.play(Write(title_text), run_time=1)
        
        # Set camera
        self.set_camera_orientation(phi=70*DEGREES, theta=30*DEGREES)
        
        # Create Bloch sphere
        sphere = Sphere(radius=2, resolution=(24, 24))
        sphere.set_color(BLUE)
        sphere.set_opacity(0.2)
        
        # Coordinate axes
        x_axis = Arrow3D(start=ORIGIN, end=RIGHT * 2.5, color=RED)
        y_axis = Arrow3D(start=ORIGIN, end=UP * 2.5, color=GREEN)
        z_axis = Arrow3D(start=ORIGIN, end=OUT * 2.5, color=BLUE)
        
        self.play(Create(sphere))
        self.play(Create(x_axis), Create(y_axis), Create(z_axis))
        
        # Labels for basis states
        state_0 = Dot3D(point=OUT * 2, color=YELLOW, radius=0.1)
        state_1 = Dot3D(point=IN * 2, color=YELLOW, radius=0.1)
        
        self.play(Create(state_0), Create(state_1))
        
        # State vector - starts at |0>
        state_arrow = Arrow3D(start=ORIGIN, end=OUT * 2, color=YELLOW)
        self.play(Create(state_arrow))
        
        # Rotate state - show different superpositions
        self.begin_ambient_camera_rotation(rate=0.2)
        
        # Rotate around X axis (creates |+> and |-> superpositions)
        self.play(Rotate(state_arrow, angle=PI/2, axis=RIGHT, about_point=ORIGIN), run_time=2)
        self.wait(1)
        
        # Rotate around Y axis
        self.play(Rotate(state_arrow, angle=PI/2, axis=UP, about_point=ORIGIN), run_time=2)
        self.wait(1)
        
        # Full rotation
        self.play(Rotate(state_arrow, angle=PI, axis=OUT, about_point=ORIGIN), run_time=2)
        
        self.stop_ambient_camera_rotation()
        self.wait(1)
'''

    @staticmethod
    def epr_paradox(title: str = "EPR Paradox") -> str:
        """
        Generate animation explaining the Einstein-Podolsky-Rosen paradox.
        """
        title = _sanitize_title(title, "EPR Paradox")
        
        return f'''from manim import *
import numpy as np

class EPRParadoxAnimation(Scene):
    def construct(self):
        # Title
        title_text = Text("{title}", font_size=32, color=BLUE)
        title_text.to_edge(UP, buff=0.4)
        self.play(Write(title_text), run_time=1)
        
        # Einstein's concern about "spooky action at a distance"
        quote = Text('"Spooky action at a distance"', font_size=24, color=YELLOW)
        quote.shift(UP * 2)
        einstein_label = Text("- Einstein", font_size=18, color=GRAY)
        einstein_label.next_to(quote, DOWN, buff=0.2)
        
        self.play(Write(quote), Write(einstein_label))
        self.wait(1)
        self.play(FadeOut(quote), FadeOut(einstein_label))
        
        # Setup: Create entangled pair
        source = Circle(radius=0.3, color=YELLOW, fill_opacity=0.8)
        source_label = Text("Entangled Pair Source", font_size=16)
        source_label.next_to(source, DOWN, buff=0.3)
        
        self.play(GrowFromCenter(source), Write(source_label))
        
        # Two particles flying apart
        particle_a = VGroup()
        p_a_circle = Circle(radius=0.2, color=BLUE, fill_opacity=0.8)
        p_a_question = Text("?", font_size=20, color=WHITE)
        p_a_question.move_to(p_a_circle)
        particle_a.add(p_a_circle, p_a_question)
        particle_a.move_to(source)
        
        particle_b = VGroup()
        p_b_circle = Circle(radius=0.2, color=RED, fill_opacity=0.8)
        p_b_question = Text("?", font_size=20, color=WHITE)
        p_b_question.move_to(p_b_circle)
        particle_b.add(p_b_circle, p_b_question)
        particle_b.move_to(source)
        
        self.play(GrowFromCenter(particle_a), GrowFromCenter(particle_b))
        
        # Particles separate to great distance
        self.play(
            particle_a.animate.shift(LEFT * 4),
            particle_b.animate.shift(RIGHT * 4),
            run_time=2
        )
        
        # Distance indicator
        distance_line = DoubleArrow(LEFT * 4, RIGHT * 4, color=GRAY, buff=0.3)
        distance_line.shift(DOWN * 1)
        distance_text = Text("Light years apart", font_size=16, color=GRAY)
        distance_text.next_to(distance_line, DOWN, buff=0.2)
        
        self.play(Create(distance_line), Write(distance_text))
        
        # EPR argument: Measure one, instantly know the other
        measure_label = Text("Measure Particle A", font_size=20, color=BLUE)
        measure_label.shift(UP * 1.5 + LEFT * 4)
        self.play(Write(measure_label))
        
        # Measurement reveals state
        flash_a = Circle(radius=0.5, color=WHITE).move_to(particle_a)
        self.play(flash_a.animate.scale(3).set_opacity(0), run_time=0.5)
        
        # State revealed for A
        state_a = Text("Spin Up", font_size=16, color=GREEN)
        state_a.next_to(particle_a, DOWN, buff=0.3)
        spin_a = Arrow(ORIGIN, UP * 0.4, color=GREEN, buff=0).move_to(particle_a)
        
        self.play(
            Transform(p_a_question, spin_a),
            Write(state_a)
        )
        
        # INSTANTLY know state of B
        instant_line = Arrow(
            particle_a.get_center(),
            particle_b.get_center(),
            color=YELLOW,
            stroke_width=5
        )
        instant_text = Text("Instantly determined!", font_size=18, color=YELLOW)
        instant_text.move_to(ORIGIN + UP * 0.5)
        
        self.play(GrowArrow(instant_line), Write(instant_text), run_time=0.5)
        
        # B's state now known
        state_b = Text("Spin Down", font_size=16, color=GREEN)
        state_b.next_to(particle_b, DOWN, buff=0.3)
        spin_b = Arrow(ORIGIN, DOWN * 0.4, color=GREEN, buff=0).move_to(particle_b)
        
        self.play(
            Transform(p_b_question, spin_b),
            Write(state_b)
        )
        
        # The paradox - how can information travel faster than light?
        paradox_text = Text("Information faster than light?", font_size=24, color=RED)
        paradox_text.to_edge(DOWN, buff=0.5)
        self.play(Write(paradox_text))
        
        # Resolution hint
        resolution = Text("No actual signal transmitted", font_size=18, color=GREEN)
        resolution.next_to(paradox_text, UP, buff=0.3)
        self.play(Write(resolution))
        
        self.wait(1)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not None], run_time=0.8)
'''

    @staticmethod
    def quantum_measurement(title: str = "Quantum Measurement Problem") -> str:
        """
        Generate animation explaining the measurement problem in quantum mechanics.
        """
        title = _sanitize_title(title, "Quantum Measurement Problem")
        
        return f'''from manim import *
import numpy as np

class QuantumMeasurementAnimation(Scene):
    def construct(self):
        # Title
        title_text = Text("{title}", font_size=32, color=BLUE)
        title_text.to_edge(UP, buff=0.4)
        self.play(Write(title_text), run_time=1)
        
        # Before measurement - superposition
        before_label = Text("Before Measurement", font_size=22, color=PURPLE)
        before_label.shift(LEFT * 3.5 + UP * 2)
        
        # Superposition cloud
        superposition = VGroup()
        cloud = Circle(radius=1.2, color=PURPLE, fill_opacity=0.15, stroke_opacity=0.5)
        
        # Multiple possible states
        states = []
        for i in range(5):
            angle = i * 2*PI/5
            r = 0.6
            state = Circle(radius=0.2, color=PURPLE, fill_opacity=0.5)
            state.move_to(r * np.array([np.cos(angle), np.sin(angle), 0]))
            states.append(state)
        
        superposition.add(cloud, *states)
        superposition.shift(LEFT * 3.5)
        
        self.play(Write(before_label))
        self.play(FadeIn(superposition))
        
        # Show states oscillating (quantum uncertainty)
        for _ in range(2):
            for state in states:
                self.play(
                    state.animate.scale(1.3).set_opacity(0.8),
                    run_time=0.1
                )
                self.play(
                    state.animate.scale(1/1.3).set_opacity(0.5),
                    run_time=0.1
                )
        
        # Measurement apparatus
        apparatus = VGroup()
        detector = Rectangle(width=1.5, height=2, color=WHITE, fill_opacity=0.1)
        detector_label = Text("Detector", font_size=16, color=WHITE)
        detector_label.next_to(detector, DOWN, buff=0.2)
        apparatus.add(detector, detector_label)
        
        self.play(Create(apparatus))
        
        # Arrow showing measurement
        measure_arrow = Arrow(LEFT * 2, LEFT * 0.5, color=YELLOW, stroke_width=3)
        self.play(GrowArrow(measure_arrow))
        
        # MEASUREMENT - collapse
        flash = Circle(radius=0.5, color=WHITE).move_to(apparatus)
        self.play(flash.animate.scale(5).set_opacity(0), run_time=0.5)
        
        # After measurement - definite state
        after_label = Text("After Measurement", font_size=22, color=GREEN)
        after_label.shift(RIGHT * 3.5 + UP * 2)
        
        # Single definite state
        definite_state = Circle(radius=0.3, color=GREEN, fill_opacity=0.8)
        definite_state.shift(RIGHT * 3.5)
        state_value = Text("State A", font_size=18, color=GREEN)
        state_value.next_to(definite_state, DOWN, buff=0.3)
        
        self.play(Write(after_label))
        self.play(
            *[FadeOut(s) for s in states[1:]],  # Other states disappear
            Transform(states[0], definite_state),
            FadeOut(cloud),
            Write(state_value)
        )
        
        # The question
        question = Text("What triggers the collapse?", font_size=24, color=YELLOW)
        question.to_edge(DOWN, buff=0.8)
        self.play(Write(question))
        
        # Different interpretations
        interp_group = VGroup()
        copenhagen = Text("Copenhagen: Measurement causes collapse", font_size=14, color=BLUE)
        many_worlds = Text("Many Worlds: All outcomes happen", font_size=14, color=RED)
        pilot_wave = Text("Pilot Wave: Hidden variables guide", font_size=14, color=GREEN)
        
        copenhagen.shift(DOWN * 2 + LEFT * 3)
        many_worlds.next_to(copenhagen, DOWN, buff=0.2, aligned_edge=LEFT)
        pilot_wave.next_to(many_worlds, DOWN, buff=0.2, aligned_edge=LEFT)
        
        interp_group.add(copenhagen, many_worlds, pilot_wave)
        
        self.play(
            FadeOut(question),
            Write(copenhagen),
            Write(many_worlds),
            Write(pilot_wave)
        )
        
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not None], run_time=0.8)
'''


# Export quantum templates
quantum_templates = QuantumAnimationTemplates()

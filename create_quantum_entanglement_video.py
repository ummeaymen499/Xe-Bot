"""
Quantum Entanglement - Full Introduction Animation Generator
Creates an amazing multi-segment video about quantum entanglement
"""
from manim import *
import numpy as np
import subprocess
from pathlib import Path


class QuantumEntanglementIntro(Scene):
    """Segment 1: Introduction to Quantum Entanglement"""
    def construct(self):
        # Dramatic title entrance
        title = Text("Quantum Entanglement", font_size=56, color=BLUE)
        subtitle = Text("The Spooky Action at a Distance", font_size=28, color=YELLOW)
        subtitle.next_to(title, DOWN, buff=0.4)
        
        # Animated particles in background
        particles = VGroup()
        for _ in range(20):
            p = Dot(
                point=np.array([np.random.uniform(-7, 7), np.random.uniform(-4, 4), 0]),
                color=random_bright_color(),
                radius=0.05
            )
            particles.add(p)
        
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in particles], lag_ratio=0.05))
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=1)
        
        self.wait(1)
        
        # Einstein quote
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(particles))
        
        quote = Text('"Spooky action at a distance"', font_size=36, color=WHITE, slant=ITALIC)
        einstein = Text("- Albert Einstein, 1935", font_size=24, color=GRAY)
        einstein.next_to(quote, DOWN, buff=0.3)
        
        self.play(Write(quote), run_time=2)
        self.play(FadeIn(einstein))
        self.wait(1.5)
        
        self.play(FadeOut(quote), FadeOut(einstein))
        
        # Brief explanation
        explanation = VGroup(
            Text("Two particles become connected", font_size=28, color=WHITE),
            Text("in a way that defies classical physics", font_size=28, color=WHITE),
        )
        explanation.arrange(DOWN, buff=0.3)
        
        self.play(Write(explanation[0]), run_time=1)
        self.play(Write(explanation[1]), run_time=1)
        self.wait(1)
        
        self.play(FadeOut(explanation))


class EntangledParticleCreation(Scene):
    """Segment 2: How Entangled Particles are Created"""
    def construct(self):
        # Section title
        title = Text("Creating Entangled Pairs", font_size=40, color=BLUE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        # Photon source
        source = VGroup()
        laser = Rectangle(width=1.5, height=0.8, color=GREEN, fill_opacity=0.3)
        laser_label = Text("Laser", font_size=16, color=GREEN)
        laser_label.next_to(laser, DOWN, buff=0.2)
        source.add(laser, laser_label)
        source.shift(LEFT * 5)
        
        # BBO Crystal (nonlinear crystal for SPDC)
        crystal = VGroup()
        crystal_shape = Polygon(
            [-0.5, -0.6, 0], [0.5, -0.6, 0], [0.7, 0.6, 0], [-0.3, 0.6, 0],
            color=PURPLE, fill_opacity=0.4
        )
        crystal_label = Text("BBO Crystal", font_size=14, color=PURPLE)
        crystal_label.next_to(crystal_shape, DOWN, buff=0.2)
        crystal.add(crystal_shape, crystal_label)
        
        self.play(Create(source), Create(crystal))
        
        # Pump photon
        pump_photon = Dot(color=GREEN, radius=0.15)
        pump_photon.move_to(laser.get_right())
        pump_label = Text("Pump Photon", font_size=12, color=GREEN)
        pump_label.next_to(pump_photon, UP, buff=0.2)
        
        self.play(GrowFromCenter(pump_photon), FadeIn(pump_label))
        
        # Photon travels to crystal
        self.play(
            pump_photon.animate.move_to(crystal_shape.get_center()),
            pump_label.animate.move_to(crystal_shape.get_center() + UP * 0.5),
            run_time=1
        )
        
        # SPDC - Spontaneous Parametric Down Conversion
        spdc_text = Text("Spontaneous Parametric\nDown Conversion", font_size=18, color=YELLOW)
        spdc_text.next_to(crystal, RIGHT, buff=1)
        self.play(FadeIn(spdc_text))
        
        # Flash at crystal
        flash = Circle(radius=0.3, color=WHITE, fill_opacity=0.8)
        flash.move_to(crystal_shape)
        self.play(
            Create(flash),
            flash.animate.scale(3).set_opacity(0),
            FadeOut(pump_photon),
            FadeOut(pump_label),
            run_time=0.5
        )
        
        # Two entangled photons emerge
        photon_signal = Dot(color=BLUE, radius=0.12)
        photon_idler = Dot(color=RED, radius=0.12)
        photon_signal.move_to(crystal_shape)
        photon_idler.move_to(crystal_shape)
        
        # Labels
        signal_label = Text("Signal", font_size=14, color=BLUE)
        idler_label = Text("Idler", font_size=14, color=RED)
        
        self.play(
            GrowFromCenter(photon_signal),
            GrowFromCenter(photon_idler),
        )
        
        # Photons diverge
        final_pos_signal = RIGHT * 4 + UP * 2
        final_pos_idler = RIGHT * 4 + DOWN * 2
        
        signal_label.move_to(final_pos_signal + UP * 0.4)
        idler_label.move_to(final_pos_idler + DOWN * 0.4)
        
        # Create wavy paths
        path_signal = TracedPath(photon_signal.get_center, stroke_color=BLUE, stroke_opacity=0.5)
        path_idler = TracedPath(photon_idler.get_center, stroke_color=RED, stroke_opacity=0.5)
        self.add(path_signal, path_idler)
        
        self.play(
            photon_signal.animate.move_to(final_pos_signal),
            photon_idler.animate.move_to(final_pos_idler),
            run_time=1.5
        )
        self.play(FadeIn(signal_label), FadeIn(idler_label))
        
        # Show entanglement connection
        entangle_line = DashedLine(photon_signal, photon_idler, color=YELLOW, dash_length=0.15)
        entangle_text = Text("Entangled!", font_size=20, color=YELLOW)
        entangle_text.move_to((photon_signal.get_center() + photon_idler.get_center()) / 2)
        
        self.play(Create(entangle_line), Write(entangle_text))
        
        # Conservation labels
        conservation = VGroup(
            Text("Energy conserved", font_size=16, color=GREEN),
            Text("Momentum conserved", font_size=16, color=GREEN),
            Text("Polarization correlated", font_size=16, color=GREEN),
        )
        conservation.arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        conservation.to_edge(DOWN, buff=0.8)
        
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT) for c in conservation], lag_ratio=0.3))
        
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])


class SpinCorrelation(Scene):
    """Segment 3: Spin Correlation Demonstration"""
    def construct(self):
        title = Text("Correlated Spins", font_size=40, color=BLUE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        # Two particles at distance
        particle_a = VGroup()
        p_a_core = Circle(radius=0.4, color=BLUE, fill_opacity=0.8)
        p_a_glow = Circle(radius=0.6, color=BLUE, fill_opacity=0.2)
        particle_a.add(p_a_glow, p_a_core)
        particle_a.shift(LEFT * 4)
        
        particle_b = VGroup()
        p_b_core = Circle(radius=0.4, color=RED, fill_opacity=0.8)
        p_b_glow = Circle(radius=0.6, color=RED, fill_opacity=0.2)
        particle_b.add(p_b_glow, p_b_core)
        particle_b.shift(RIGHT * 4)
        
        label_a = Text("Alice", font_size=20, color=BLUE)
        label_a.next_to(particle_a, DOWN, buff=0.4)
        label_b = Text("Bob", font_size=20, color=RED)
        label_b.next_to(particle_b, DOWN, buff=0.4)
        
        self.play(
            GrowFromCenter(particle_a),
            GrowFromCenter(particle_b),
            Write(label_a),
            Write(label_b)
        )
        
        # Entanglement line
        entangle = DashedLine(particle_a, particle_b, color=YELLOW, dash_length=0.2)
        self.play(Create(entangle))
        
        # Add spin arrows - superposition state (both up and down)
        spin_a_up = Arrow(ORIGIN, UP * 0.5, color=WHITE, buff=0, stroke_width=4)
        spin_a_down = Arrow(ORIGIN, DOWN * 0.5, color=WHITE, buff=0, stroke_width=4, stroke_opacity=0.4)
        spin_a_up.move_to(particle_a)
        spin_a_down.move_to(particle_a)
        
        spin_b_up = Arrow(ORIGIN, UP * 0.5, color=WHITE, buff=0, stroke_width=4, stroke_opacity=0.4)
        spin_b_down = Arrow(ORIGIN, DOWN * 0.5, color=WHITE, buff=0, stroke_width=4)
        spin_b_up.move_to(particle_b)
        spin_b_down.move_to(particle_b)
        
        superposition_text = Text("Superposition: Both spins undefined", font_size=22, color=YELLOW)
        superposition_text.shift(DOWN * 2)
        
        self.play(
            GrowArrow(spin_a_up), GrowArrow(spin_a_down),
            GrowArrow(spin_b_up), GrowArrow(spin_b_down),
            Write(superposition_text)
        )
        
        # Oscillate to show superposition
        for _ in range(3):
            self.play(
                spin_a_up.animate.set_opacity(0.4),
                spin_a_down.animate.set_opacity(1),
                spin_b_up.animate.set_opacity(1),
                spin_b_down.animate.set_opacity(0.4),
                run_time=0.4
            )
            self.play(
                spin_a_up.animate.set_opacity(1),
                spin_a_down.animate.set_opacity(0.4),
                spin_b_up.animate.set_opacity(0.4),
                spin_b_down.animate.set_opacity(1),
                run_time=0.4
            )
        
        # Alice measures
        measure_text = Text("Alice measures her particle...", font_size=22, color=GREEN)
        measure_text.shift(DOWN * 2)
        self.play(Transform(superposition_text, measure_text))
        
        # Measurement effect
        detector = Rectangle(width=0.8, height=1.2, color=GREEN, fill_opacity=0.3)
        detector.next_to(particle_a, LEFT, buff=0.3)
        self.play(Create(detector))
        
        # Flash
        flash = Circle(radius=0.5, color=WHITE).move_to(particle_a)
        self.play(flash.animate.scale(3).set_opacity(0), run_time=0.4)
        
        # Collapse - Alice gets UP
        self.play(
            FadeOut(spin_a_down),
            spin_a_up.animate.set_opacity(1).scale(1.3),
            run_time=0.5
        )
        
        # INSTANTLY Bob's particle collapses to DOWN
        instant_text = Text("INSTANTLY Bob's particle becomes DOWN!", font_size=22, color=YELLOW)
        instant_text.shift(DOWN * 2)
        
        wave_effect = Circle(radius=0.1, color=YELLOW).move_to(particle_a)
        
        self.play(
            Transform(superposition_text, instant_text),
            wave_effect.animate.move_to(particle_b).scale(20).set_opacity(0),
            FadeOut(spin_b_up),
            spin_b_down.animate.set_opacity(1).scale(1.3),
            run_time=0.8
        )
        
        # Result labels
        result_a = Text("UP", font_size=24, color=GREEN)
        result_a.next_to(particle_a, UP, buff=0.8)
        result_b = Text("DOWN", font_size=24, color=GREEN)
        result_b.next_to(particle_b, UP, buff=0.8)
        
        self.play(FadeIn(result_a, scale=1.5), FadeIn(result_b, scale=1.5))
        
        # Always opposite!
        always_text = Text("Always opposite - 100% correlated!", font_size=26, color=YELLOW)
        always_text.to_edge(DOWN, buff=0.5)
        self.play(Write(always_text))
        
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])


class BellInequality(Scene):
    """Segment 4: Bell's Inequality - Proving Quantum Weirdness"""
    def construct(self):
        title = Text("Bell's Inequality", font_size=40, color=BLUE)
        subtitle = Text("Proving Einstein Wrong", font_size=24, color=YELLOW)
        subtitle.next_to(title, DOWN, buff=0.3)
        title_group = VGroup(title, subtitle)
        title_group.to_edge(UP, buff=0.4)
        
        self.play(Write(title), FadeIn(subtitle, shift=UP))
        
        # The question
        question = Text("Could there be 'hidden variables'?", font_size=28, color=WHITE)
        question.shift(UP * 1)
        self.play(Write(question))
        
        # Two hypotheses
        classical = VGroup(
            Text("Classical View", font_size=22, color=GREEN),
            Text("Particles carry hidden", font_size=18, color=WHITE),
            Text("predetermined values", font_size=18, color=WHITE),
        )
        classical.arrange(DOWN, buff=0.2)
        classical.shift(LEFT * 3 + DOWN * 0.5)
        
        quantum = VGroup(
            Text("Quantum View", font_size=22, color=PURPLE),
            Text("Values don't exist", font_size=18, color=WHITE),
            Text("until measured", font_size=18, color=WHITE),
        )
        quantum.arrange(DOWN, buff=0.2)
        quantum.shift(RIGHT * 3 + DOWN * 0.5)
        
        self.play(
            LaggedStart(*[FadeIn(c) for c in classical], lag_ratio=0.2),
            LaggedStart(*[FadeIn(q) for q in quantum], lag_ratio=0.2),
        )
        
        self.wait(1)
        
        # Bell's test setup
        self.play(FadeOut(question), classical.animate.shift(UP * 2), quantum.animate.shift(UP * 2))
        
        setup_text = Text("Bell's Test Setup", font_size=24, color=YELLOW)
        setup_text.shift(UP * 0.5)
        self.play(Write(setup_text))
        
        # Source and detectors
        source = Circle(radius=0.3, color=YELLOW, fill_opacity=0.8)
        source_label = Text("Source", font_size=14)
        source_label.next_to(source, DOWN, buff=0.2)
        
        det_a = VGroup(
            Rectangle(width=1, height=0.6, color=BLUE, fill_opacity=0.3),
            Text("Det A", font_size=12, color=BLUE)
        )
        det_a[1].next_to(det_a[0], DOWN, buff=0.1)
        det_a.shift(LEFT * 4)
        
        det_b = VGroup(
            Rectangle(width=1, height=0.6, color=RED, fill_opacity=0.3),
            Text("Det B", font_size=12, color=RED)
        )
        det_b[1].next_to(det_b[0], DOWN, buff=0.1)
        det_b.shift(RIGHT * 4)
        
        # Angle indicators
        angle_a = Arc(radius=0.4, angle=PI/4, color=BLUE, stroke_width=3)
        angle_a.move_to(det_a[0].get_center() + DOWN * 0.5)
        angle_b = Arc(radius=0.4, angle=PI/3, color=RED, stroke_width=3)
        angle_b.move_to(det_b[0].get_center() + DOWN * 0.5)
        
        self.play(
            GrowFromCenter(source), Write(source_label),
            Create(det_a), Create(det_b),
            Create(angle_a), Create(angle_b)
        )
        
        # Particles fly
        for _ in range(2):
            p1 = Dot(color=BLUE, radius=0.1).move_to(source)
            p2 = Dot(color=RED, radius=0.1).move_to(source)
            self.play(
                p1.animate.move_to(det_a[0]),
                p2.animate.move_to(det_b[0]),
                run_time=0.5
            )
            self.play(FadeOut(p1), FadeOut(p2), run_time=0.2)
        
        # Results
        self.play(FadeOut(setup_text))
        
        result_title = Text("Statistical Results", font_size=24, color=YELLOW)
        result_title.shift(DOWN * 1.5)
        
        # Bell inequality limit
        classical_limit = Rectangle(width=3, height=0.4, color=GREEN, fill_opacity=0.6)
        classical_limit.shift(DOWN * 2.2 + LEFT * 1.5)
        cl_label = Text("Classical Limit: S <= 2", font_size=16, color=GREEN)
        cl_label.next_to(classical_limit, LEFT, buff=0.3)
        
        # Quantum result exceeds!
        quantum_result = Rectangle(width=4.2, height=0.4, color=PURPLE, fill_opacity=0.6)
        quantum_result.shift(DOWN * 2.8 + LEFT * 0.9)
        qr_label = Text("Quantum Result: S = 2.8", font_size=16, color=PURPLE)
        qr_label.next_to(quantum_result, LEFT, buff=0.3)
        
        self.play(Write(result_title))
        self.play(
            GrowFromEdge(classical_limit, LEFT),
            Write(cl_label)
        )
        self.play(
            GrowFromEdge(quantum_result, LEFT),
            Write(qr_label)
        )
        
        # Highlight violation
        violation = Text("VIOLATION! No hidden variables!", font_size=26, color=YELLOW)
        violation.to_edge(DOWN, buff=0.3)
        
        box = SurroundingRectangle(quantum_result, color=YELLOW, buff=0.1)
        self.play(Create(box), Write(violation))
        
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])


class QuantumApplications(Scene):
    """Segment 5: Applications of Quantum Entanglement"""
    def construct(self):
        title = Text("Applications", font_size=44, color=BLUE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        # Application 1: Quantum Computing
        qc_title = Text("Quantum Computing", font_size=28, color=GREEN)
        qc_title.shift(LEFT * 3.5 + UP * 1.5)
        
        # Qubit representation
        qubit = VGroup()
        q_circle = Circle(radius=0.4, color=PURPLE, fill_opacity=0.6)
        q_label = Text("|0> + |1>", font_size=18, color=WHITE)
        q_label.next_to(q_circle, DOWN, buff=0.2)
        qubit.add(q_circle, q_label)
        qubit.next_to(qc_title, DOWN, buff=0.4)
        
        self.play(Write(qc_title), Create(qubit))
        
        # Application 2: Quantum Cryptography
        qcrypto_title = Text("Quantum Cryptography", font_size=28, color=RED)
        qcrypto_title.shift(RIGHT * 3 + UP * 1.5)
        
        # Key distribution visual
        alice_bob = VGroup()
        alice = Circle(radius=0.3, color=BLUE, fill_opacity=0.6)
        bob = Circle(radius=0.3, color=RED, fill_opacity=0.6)
        alice.shift(LEFT * 0.8)
        bob.shift(RIGHT * 0.8)
        key_line = DashedLine(alice, bob, color=YELLOW)
        lock = Text("SECURE", font_size=14, color=GREEN)
        lock.next_to(key_line, DOWN, buff=0.1)
        alice_bob.add(alice, bob, key_line)
        alice_bob.next_to(qcrypto_title, DOWN, buff=0.4)
        
        self.play(Write(qcrypto_title), Create(alice_bob), FadeIn(lock))
        
        # Application 3: Quantum Teleportation
        qtele_title = Text("Quantum Teleportation", font_size=28, color=YELLOW)
        qtele_title.shift(DOWN * 1)
        
        # Teleportation visual
        tele_visual = VGroup()
        start_pos = Dot(color=PURPLE, radius=0.15).shift(LEFT * 2 + DOWN * 2)
        end_pos = Dot(color=PURPLE, radius=0.15, fill_opacity=0.3).shift(RIGHT * 2 + DOWN * 2)
        tele_arrow = CurvedArrow(start_pos.get_center(), end_pos.get_center(), color=PURPLE)
        tele_visual.add(start_pos, end_pos, tele_arrow)
        
        self.play(Write(qtele_title), Create(tele_visual))
        
        # Animate teleportation
        self.play(
            start_pos.animate.set_opacity(0.3),
            end_pos.animate.set_opacity(1),
            run_time=1
        )
        
        # Application 4: Quantum Sensors
        qsensor_title = Text("Quantum Sensors", font_size=28, color=TEAL)
        qsensor_title.shift(DOWN * 1 + RIGHT * 4)
        
        sensor_icon = VGroup()
        s_circle = Circle(radius=0.25, color=TEAL, fill_opacity=0.6)
        s_waves = VGroup(*[
            Arc(radius=0.4 + i*0.15, angle=PI/3, color=TEAL, stroke_opacity=0.8-i*0.2)
            for i in range(3)
        ])
        s_waves.move_to(s_circle.get_right())
        sensor_icon.add(s_circle, s_waves)
        sensor_icon.next_to(qsensor_title, LEFT, buff=0.3)
        
        self.play(Write(qsensor_title), Create(sensor_icon))
        
        # Summary
        summary = Text("Entanglement is a resource!", font_size=32, color=YELLOW)
        summary.to_edge(DOWN, buff=0.5)
        self.play(Write(summary))
        
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])


class QuantumEntanglementConclusion(Scene):
    """Segment 6: Conclusion"""
    def construct(self):
        # Key takeaways
        title = Text("Key Takeaways", font_size=44, color=BLUE)
        title.to_edge(UP, buff=0.6)
        self.play(Write(title))
        
        takeaways = VGroup(
            Text("• Entangled particles share a quantum state", font_size=26, color=WHITE),
            Text("• Measurement of one instantly affects the other", font_size=26, color=WHITE),
            Text("• This correlation is stronger than any classical theory", font_size=26, color=WHITE),
            Text("• Bell tests prove nature is truly quantum", font_size=26, color=WHITE),
            Text("• Entanglement enables new technologies", font_size=26, color=WHITE),
        )
        takeaways.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        takeaways.next_to(title, DOWN, buff=0.8)
        
        for t in takeaways:
            self.play(FadeIn(t, shift=RIGHT * 0.5), run_time=0.6)
            self.wait(0.3)
        
        self.wait(1)
        
        # Final visual - entangled particles
        self.play(FadeOut(takeaways))
        
        # Create beautiful entangled pair visualization
        p1 = VGroup()
        p1_core = Circle(radius=0.5, color=BLUE, fill_opacity=0.9)
        p1_glow = Circle(radius=0.8, color=BLUE, fill_opacity=0.2)
        p1.add(p1_glow, p1_core)
        p1.shift(LEFT * 2.5)
        
        p2 = VGroup()
        p2_core = Circle(radius=0.5, color=RED, fill_opacity=0.9)
        p2_glow = Circle(radius=0.8, color=RED, fill_opacity=0.2)
        p2.add(p2_glow, p2_core)
        p2.shift(RIGHT * 2.5)
        
        # Connection
        connection = VGroup()
        for i in range(5):
            line = Line(
                p1.get_center() + UP * (i - 2) * 0.2,
                p2.get_center() + UP * (i - 2) * 0.2,
                color=YELLOW,
                stroke_opacity=0.3 + 0.1 * (2 - abs(i - 2))
            )
            connection.add(line)
        
        self.play(
            GrowFromCenter(p1),
            GrowFromCenter(p2),
            LaggedStart(*[Create(l) for l in connection], lag_ratio=0.1)
        )
        
        # Pulsing effect
        for _ in range(3):
            self.play(
                p1.animate.scale(1.1),
                p2.animate.scale(1.1),
                connection.animate.set_stroke(opacity=0.8),
                run_time=0.4
            )
            self.play(
                p1.animate.scale(1/1.1),
                p2.animate.scale(1/1.1),
                connection.animate.set_stroke(opacity=0.4),
                run_time=0.4
            )
        
        # Final message
        final_msg = Text("The Universe is Stranger Than We Think", font_size=32, color=YELLOW)
        final_msg.to_edge(DOWN, buff=0.8)
        self.play(Write(final_msg))
        
        self.wait(2)
        
        # Fade to branding
        self.play(*[FadeOut(m) for m in self.mobjects])
        
        branding = Text("Animation by Xe-Bot", font_size=36, color=BLUE)
        self.play(Write(branding))
        self.wait(1.5)
        self.play(FadeOut(branding))


# Main execution
if __name__ == "__main__":
    from pathlib import Path
    import os
    
    # Output directory
    output_dir = Path("output/animations/videos/full_introduction/720p30")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    scenes = [
        "QuantumEntanglementIntro",
        "EntangledParticleCreation", 
        "SpinCorrelation",
        "BellInequality",
        "QuantumApplications",
        "QuantumEntanglementConclusion"
    ]
    
    print("=" * 60)
    print("Quantum Entanglement Animation Generator")
    print("=" * 60)
    
    for scene in scenes:
        print(f"\n▶ Rendering {scene}...")
        cmd = [
            "manim",
            "-qm",  # Medium quality for balance
            "--fps", "30",
            "-o", f"{scene}.mp4",
            "--media_dir", str(output_dir.parent.parent.parent),
            __file__,
            scene
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✓ {scene} rendered successfully!")
        else:
            print(f"  ✗ Error rendering {scene}")
            print(f"    {result.stderr[:200] if result.stderr else 'Unknown error'}")
    
    print("\n" + "=" * 60)
    print("All scenes rendered! Check output/animations/videos/full_introduction/")
    print("=" * 60)

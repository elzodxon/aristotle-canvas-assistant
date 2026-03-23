from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "Elzodxon Sharofaddinov", align="R", new_x="LMARGIN", new_y="NEXT")

    def section(self, title):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body(self, text):
        self.set_font("Helvetica", "", 11)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def bold_line(self, text):
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")

    def answer_box(self, text):
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(230, 245, 230)
        self.multi_cell(0, 7, text, fill=True)
        self.ln(3)

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.add_page()

pdf.set_font("Helvetica", "B", 16)
pdf.cell(0, 12, "PHYSICS - MECHANICS", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 10, "TOPIC: Work and Energy", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 11)
pdf.cell(0, 8, "Week 8 Assignment", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, "Student: Elzodxon Sharofaddinov", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(6)

# Q1
pdf.section("Q1. Worker pushing crate up inclined plane")
pdf.body(
    "Given: Weight W = 93 N, Applied force F = 85 N (horizontal)\n"
    "From the figure: hypotenuse = 5.0 m, height = 3.0 m, base = 4.0 m\n"
    "sin(angle) = 3/5 = 0.6, cos(angle) = 4/5 = 0.8"
)

pdf.bold_line("(a) Work done by the worker:")
pdf.body(
    "The worker pushes horizontally. The horizontal displacement = 4.0 m.\n"
    "W_worker = F x d_horizontal = 85 x 4.0 = 340 J"
)
pdf.answer_box("W_worker = 340 J")

pdf.bold_line("(b) Work done by gravity:")
pdf.body(
    "Gravity acts downward (93 N). The crate moves up by height = 3.0 m.\n"
    "W_gravity = -W x h = -93 x 3.0 = -279 J\n"
    "(Negative because gravity opposes the upward displacement.)"
)
pdf.answer_box("W_gravity = -279 J")

pdf.bold_line("(c) Work done by friction (u = 0.25):")
pdf.body(
    "Normal force: N = W cos(angle) = 93 x 0.8 = 74.4 N\n"
    "Friction force: f = u x N = 0.25 x 74.4 = 18.6 N\n"
    "Friction opposes motion along the 5.0 m ramp:\n"
    "W_friction = -f x d = -18.6 x 5.0 = -93 J"
)
pdf.answer_box("W_friction = -93 J")

# Q2
pdf.section("Q2. Electric motor lifting elevator")
pdf.body(
    "Given: P = 65 kW = 65,000 W, d = 17.5 m, t = 35 s\n\n"
    "Velocity of elevator: v = d/t = 17.5/35 = 0.5 m/s\n\n"
    "Power = Force x velocity\n"
    "F = P/v = 65,000 / 0.5 = 130,000 N"
)
pdf.answer_box("F = 1.3 x 10^5 N")

# Q3
pdf.section("Q3. Block on spring (frictionless surface)")
pdf.body(
    "Given: m = 1.6 kg, k = 1000 N/m, x = 4 cm = 0.04 m\n\n"
    "Using conservation of energy:\n"
    "(1/2)kx^2 = (1/2)mv^2\n\n"
    "v = x * sqrt(k/m) = 0.04 x sqrt(1000/1.6)\n"
    "v = 0.04 x sqrt(625) = 0.04 x 25 = 1 m/s"
)
pdf.answer_box("v = 1 m/s")

# Q4
pdf.section("Q4. Escalator at Ocean Park")
pdf.body(
    "Given: m = 52 kg, L = 225 m, angle = 30 degrees, g = 10.0 m/s^2\n\n"
    "Height gained: h = L sin(30) = 225 x 0.5 = 112.5 m\n\n"
    "Work done by escalator = mgh = 52 x 10.0 x 112.5 = 58,500 J"
)
pdf.answer_box("W = 58,500 J")

# Q5
pdf.section("Q5. Dragging crate with rope at 60 degrees")
pdf.body("Given: Horizontal force needed = 800 N, rope angle = 60 degrees")

pdf.bold_line("(a) Force exerted on the rope:")
pdf.body(
    "The horizontal component of the rope force must equal 800 N:\n"
    "F cos(60) = 800\n"
    "F = 800 / cos(60) = 800 / 0.5 = 1600 N"
)
pdf.answer_box("F = 1600 N")

pdf.bold_line("(b) Work done moving crate 22 m:")
pdf.body("Work = horizontal force x distance = 800 x 22 = 17,600 J")
pdf.answer_box("W = 17,600 J")

pdf.bold_line("(c) Power developed in 8.0 s:")
pdf.body("P = W/t = 17,600 / 8.0 = 2,200 W = 2.2 kW")
pdf.answer_box("P = 2.2 kW")

# Q6
pdf.section("Q6. Boy pulling sled")
pdf.body(
    "Given: F = 42 N, angle = 60.0 degrees, d = 16 m, t = 3.0 s\n\n"
    "Work done: W = F cos(angle) x d = 42 x cos(60) x 16\n"
    "W = 42 x 0.5 x 16 = 336 J\n\n"
    "Power: P = W/t = 336 / 3.0 = 112 W"
)
pdf.answer_box("P = 112 W")

# Q7
pdf.section("Q7. Box on inclined plane with friction")
pdf.body(
    "Given: m = 3 kg, v_i = 10 m/s, v_B = 4 m/s, h = 2 m (from figure)\n\n"
    "Using the work-energy theorem:\n"
    "W_net = Delta KE = (1/2)mv_B^2 - (1/2)mv_i^2\n\n"
    "The box moves up the incline to height h = 2 m:\n"
    "W_gravity = -mgh = -3 x 10 x 2 = -60 J\n\n"
    "Delta KE = (1/2)(3)(4^2) - (1/2)(3)(10^2) = 24 - 150 = -126 J\n\n"
    "W_net = W_gravity + W_friction\n"
    "W_friction = Delta KE - W_gravity = -126 - (-60) = -66 J"
)
pdf.answer_box("|W_friction| = 66 J")

# Q8
pdf.section("Q8. Ball launched by spring")
pdf.body(
    "Given: m = 0.12 kg, F_avg = 2.8 N, d = 15 cm = 0.15 m\n\n"
    "Work done by spring: W = F x d = 2.8 x 0.15 = 0.42 J\n\n"
    "At maximum height, all kinetic energy converts to potential energy:\n"
    "mgh = W\n"
    "h = W/(mg) = 0.42 / (0.12 x 10) = 0.42 / 1.2 = 0.35 m"
)
pdf.answer_box("h = 0.35 m")

# Q9
pdf.section("Q9. Model plane")
pdf.body("Given: m = 15.0 kg, v = 10.0 m/s")

pdf.bold_line("(a) Kinetic energy:")
pdf.body("KE = (1/2)mv^2 = (1/2) x 15.0 x (10.0)^2 = (1/2) x 15.0 x 100 = 750 J")
pdf.answer_box("KE = 750 J")

pdf.bold_line("(b) Potential energy lost during 20.0 m dive:")
pdf.body("Delta PE = mgh = 15.0 x 10.0 x 20.0 = 3,000 J = 3 kJ")
pdf.answer_box("Delta PE = 3 kJ")

# Q10
pdf.section("Q10. Accelerating car")
pdf.body(
    "Given: m = 1200 kg, v_i = 0, v_f = 72 km/h = 20 m/s, t = 20.0 s, f = 450 N"
)

pdf.bold_line("(a) Net work done on the car:")
pdf.body(
    "By the work-energy theorem:\n"
    "W_net = Delta KE = (1/2)mv_f^2 - (1/2)mv_i^2\n"
    "W_net = (1/2) x 1200 x (20)^2 - 0 = 240,000 J = 240 kJ"
)
pdf.answer_box("W_net = 240 kJ")

pdf.bold_line("(b) Distance traveled:")
pdf.body(
    "Average velocity: v_avg = (v_i + v_f)/2 = (0 + 20)/2 = 10 m/s\n"
    "Distance: d = v_avg x t = 10 x 20 = 200 m"
)
pdf.answer_box("d = 200 m")

pdf.bold_line("(c) Net force on the car:")
pdf.body("F_net = W_net / d = 240,000 / 200 = 1,200 N")
pdf.answer_box("F_net = 1200 N")

# Q11
pdf.section("Q11. Cart on inclined plane at constant speed")
pdf.body(
    "Given: F = 7.5 N, m = 1.5 kg, constant speed (net force = 0)\n\n"
    "At constant speed along the incline, the applied force balances\n"
    "the component of gravity along the plane:\n"
    "F = mg sin(angle)\n\n"
    "sin(angle) = F/(mg) = 7.5 / (1.5 x 10) = 7.5 / 15 = 0.5\n\n"
    "angle = arcsin(0.5) = 30 degrees"
)
pdf.answer_box("angle = 30 degrees")

output = "/root/aristotle-canvas-assistant/Elzodxon-Sharofaddinov-Physics-assignment_8.pdf"
pdf.output(output)
print(f"PDF saved to: {output}")

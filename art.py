import streamlit as st
import streamlit.components.v1 as components
import random

# Page config
st.set_page_config(page_title="El Lienzo del Caos", layout="wide")
st.title("El Lienzo del Caos")

# Sidebar – UI Controls
st.sidebar.header("Ajustes del Lienzo")

num_shapes = st.sidebar.slider("Cantidad de Círculos", 5, 100, 25)
num_walls = st.sidebar.slider("Cantidad de Paredes", 0, 40, 10)
speed = st.sidebar.slider("Velocidad Inicial", 0.5, 10.0, 3.5, 0.1)

st.sidebar.markdown("**Colores Círculos**")
num_colors = st.sidebar.slider("Número de Colores", 1, 8, 3)

default_palette = ["#F1C715", "#F9980D", "#AF6F15", "#FFD93D", "#C34A36", "#8E44AD", "#3498DB", "#E67E22"]
colors = [st.sidebar.color_picker(f" Color {i+1}", default_palette[i]) for i in range(num_colors)]

wall_color = st.sidebar.color_picker("Color de Paredes", "#33AD59")
bg_color = st.sidebar.color_picker("Color de Fondo", "#ABE2BE")

# Store settings
if "settings" not in st.session_state:
    st.session_state.settings = {
        "seed": random.randint(0, 999_999),
        "num_shapes": num_shapes,
        "num_walls": num_walls,
        "speed": speed,
        "colors": colors,
        "wall_color": wall_color,
        "bg_color": bg_color,
    }

# Regenerate button
if st.button("Regenerar Lienzo"):
    st.session_state.settings = {
        "seed": random.randint(0, 999_999),
        "num_shapes": num_shapes,
        "num_walls": num_walls,
        "speed": speed,
        "colors": colors,
        "wall_color": wall_color,
        "bg_color": bg_color,
    }

# Extract config
cfg = st.session_state.settings
colors_js = "[" + ",".join(f'"{c}"' for c in cfg["colors"]) + "]"

# HTML + JS
html_code = f"""
<div id="canvasContainer" style="position: relative; width: 100%; max-width: 1200px; aspect-ratio: 16/9; margin: 30px auto;">
  <canvas id="artCanvas"
      style="border-radius: 25px; border: 3px solid #8884; background: {cfg['bg_color']}; width: 100%; height: 100%; box-shadow: 0 0 20px rgba(0,0,0,0.2); display: block; position: absolute; top: 0; left: 0;">
  </canvas>

  <style>
    #fsBtn {{
        position: absolute;
        bottom: 12px;
        right: 12px;
        background: transparent;
        border: none;
        font-size: 18px;
        color: #666;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.3s ease;
        padding: 4px 6px;
    }}
    #canvasContainer:hover #fsBtn {{
        opacity: 1;
    }}
    #fsBtn:hover {{
        color: #000;
        transform: scale(1.1);
    }}
  </style>

  <button id="fsBtn" title="Fullscreen">🔲</button>
</div>

<script>
const seed = {cfg["seed"]};
let randIndex = 0;
function seededRandom(s) {{
    let x = Math.sin(s) * 10000;
    return x - Math.floor(x);
}}
function rand() {{
    return seededRandom(seed + randIndex++);
}}

const canvas = document.getElementById("artCanvas");
const container = document.getElementById("canvasContainer");

function resizeCanvas() {{
    const rect = container.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
}}
resizeCanvas();
window.addEventListener("resize", resizeCanvas);

const ctx = canvas.getContext("2d");
const COLORS = {colors_js};
const NUM_SHAPES = {cfg["num_shapes"]};
const NUM_WALLS = {cfg["num_walls"]};
const SPEED = {cfg["speed"]};
const SHAPES = [];
const WALLS = [];

class Shape {{
    constructor() {{
        this.radius = 8 + rand() * 20;
        this.x = this.radius + rand() * (canvas.width - 2 * this.radius);
        this.y = this.radius + rand() * (canvas.height - 2 * this.radius);
        const angle = rand() * 2 * Math.PI;
        this.dx = Math.cos(angle) * SPEED;
        this.dy = Math.sin(angle) * SPEED;
        this.color = COLORS[Math.floor(rand() * COLORS.length)];
    }}
    draw() {{
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
        ctx.fillStyle = this.color;
        ctx.shadowBlur = 10;
        ctx.shadowColor = this.color + "88";
        ctx.fill();
        ctx.closePath();
        ctx.shadowBlur = 0;
    }}
    update() {{
        this.x += this.dx;
        this.y += this.dy;

        if (this.x - this.radius < 0) {{
            this.x = this.radius;
            this.dx *= -1;
        }} else if (this.x + this.radius > canvas.width) {{
            this.x = canvas.width - this.radius;
            this.dx *= -1;
        }}
        if (this.y - this.radius < 0) {{
            this.y = this.radius;
            this.dy *= -1;
        }} else if (this.y + this.radius > canvas.height) {{
            this.y = canvas.height - this.radius;
            this.dy *= -1;
        }}

        for (let wall of WALLS) {{
            if (
                this.x + this.radius > wall.x &&
                this.x - this.radius < wall.x + wall.w &&
                this.y + this.radius > wall.y &&
                this.y - this.radius < wall.y + wall.h
            ) {{
                const overlapX = Math.min(this.x + this.radius - wall.x, wall.x + wall.w - (this.x - this.radius));
                const overlapY = Math.min(this.y + this.radius - wall.y, wall.y + wall.h - (this.y - this.radius));
                if (overlapX < overlapY) {{
                    this.dx *= -1;
                    if (this.x < wall.x) this.x = wall.x - this.radius;
                    else this.x = wall.x + wall.w + this.radius;
                }} else {{
                    this.dy *= -1;
                    if (this.y < wall.y) this.y = wall.y - this.radius;
                    else this.y = wall.y + wall.h + this.radius;
                }}
            }}
        }}
    }}
}}

class Wall {{
    constructor() {{
        this.w = 50 + rand() * 120;
        this.h = 20 + rand() * 80;
        this.x = rand() * (canvas.width - this.w);
        this.y = rand() * (canvas.height - this.h);
    }}
    draw() {{
        ctx.fillStyle = "{cfg['wall_color']}";
        ctx.strokeStyle = "#2228";
        ctx.lineWidth = 1;
        ctx.fillRect(this.x, this.y, this.w, this.h);
        ctx.strokeRect(this.x, this.y, this.w, this.h);
    }}
}}

function detectCollisions() {{
    for (let i = 0; i < SHAPES.length; i++) {{
        for (let j = i + 1; j < SHAPES.length; j++) {{
            const a = SHAPES[i], b = SHAPES[j];
            const dx = a.x - b.x;
            const dy = a.y - b.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            const minDist = a.radius + b.radius;
            if (dist < minDist) {{
                const nx = dx / dist;
                const ny = dy / dist;
                const overlap = 0.5 * (minDist - dist + 1);
                a.x += nx * overlap;
                a.y += ny * overlap;
                b.x -= nx * overlap;
                b.y -= ny * overlap;

                const p = 2 * (a.dx * nx + a.dy * ny - b.dx * nx - b.dy * ny) / 2;
                a.dx -= p * nx;
                a.dy -= p * ny;
                b.dx += p * nx;
                b.dy += p * ny;
            }}
        }}
    }}
}}

function animate() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let wall of WALLS) wall.draw();
    for (let shape of SHAPES) {{
        shape.update();
        shape.draw();
    }}
    detectCollisions();
    requestAnimationFrame(animate);
}}

function init() {{
    for (let i = 0; i < NUM_SHAPES; i++) SHAPES.push(new Shape());
    for (let i = 0; i < NUM_WALLS; i++) WALLS.push(new Wall());
    animate();
}}

init();

// Fullscreen toggle
const fsBtn = document.getElementById("fsBtn");
fsBtn.addEventListener("click", () => {{
    if (!document.fullscreenElement) {{
        container.requestFullscreen().catch(err => alert(`Error attempting to enable fullscreen: ${{err.message}}`));
    }} else {{
        document.exitFullscreen();
    }}
}});
</script>
"""

components.html(html_code, height=750)

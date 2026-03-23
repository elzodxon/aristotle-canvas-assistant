"""
Convert a clean PDF into a handwritten-and-scanned look.

Pipeline:
  1. Render each PDF page to a high-res image (PyMuPDF)
  2. Replace typed text with handwriting font (Pillow)
  3. Add scan artifacts: paper texture, slight rotation, noise, uneven lighting
"""

import fitz  # PyMuPDF
import random
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
import os

# ── Config ──────────────────────────────────────────────────────────────
FONT_PATH = os.path.join(os.path.dirname(__file__), "Caveat.ttf")
INPUT_PDF = os.path.join(os.path.dirname(__file__),
                         "Elzodxon-Sharofaddinov-Physics-assignment_8.pdf")
OUTPUT_PDF = os.path.join(os.path.dirname(__file__),
                          "Elzodxon-Sharofaddinov-Physics-assignment_8-handwritten.pdf")

# Page size in pixels (letter-ish at 150 DPI for realistic scan)
DPI = 150
PAGE_W = int(8.5 * DPI)
PAGE_H = int(11  * DPI)

MARGIN_L = int(0.9 * DPI)
MARGIN_R = int(0.7 * DPI)
MARGIN_T = int(0.8 * DPI)

INK_COLOR = (20, 20, 75)        # dark blue-black ink
TITLE_COLOR = (15, 15, 65)
ANSWER_COLOR = (20, 20, 75)     # same ink color, no green
PAPER_COLOR = (245, 242, 235)   # off-white / aged paper


def load_fonts():
    return {
        "title":  48,
        "heading": 40,
        "bold":   36,
        "body":   33,
        "small":  28,
    }

# Cache fonts at different sizes to avoid re-loading constantly
_font_cache = {}

def get_font(base_size):
    """Return a font with slight random size variation (+/- 1px)."""
    size = base_size + random.choice([-1, 0, 0, 0, 0, 1])
    if size not in _font_cache:
        _font_cache[size] = ImageFont.truetype(FONT_PATH, size)
    return _font_cache[size]


def jitter(base, mag=2):
    """Random offset to simulate hand wobble."""
    return base + random.uniform(-mag, mag)


def paper_background(w, h):
    """Create a realistic aged-paper background."""
    img = Image.new("RGB", (w, h), PAPER_COLOR)
    pixels = np.array(img, dtype=np.int16)
    # fine grain noise
    noise = np.random.normal(0, 3, pixels.shape).astype(np.int16)
    pixels = np.clip(pixels + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(pixels)
    # slight uneven lighting (vignette)
    overlay = Image.new("L", (w, h), 255)
    draw_ov = ImageDraw.Draw(overlay)
    cx, cy = w // 2, h // 2
    for r in range(max(w, h), 0, -4):
        brightness = max(0, 255 - int((max(w, h) - r) * 0.06))
        draw_ov.ellipse([cx - r, cy - r, cx + r, cy + r], fill=brightness)
    img = Image.composite(img, Image.new("RGB", (w, h), (200, 195, 185)), overlay)
    return img


def wrap_text(text, font_size, max_width, draw):
    """Word-wrap text to fit within max_width."""
    font = get_font(font_size)  # use base size for measuring wrap
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        words = paragraph.split()
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_width and current:
                lines.append(current)
                current = word
            else:
                current = test
        if current:
            lines.append(current)
    return lines


def draw_handwritten_line(draw, x, y, text, font_size, color, img=None):
    """Draw a line word-by-word for natural spacing, with per-word variation."""
    cx = x
    baseline_drift = 0
    drift_speed = random.uniform(-0.06, 0.06)
    words = text.split(" ")
    for wi, word in enumerate(words):
        if not word:
            cx += font_size * 0.3
            continue
        # each word gets a slightly different font size
        word_font = get_font(font_size)
        dy = random.uniform(-0.6, 0.6) + baseline_drift
        # ink pressure variation per word
        r, g, b = color
        shade = random.randint(-8, 5)
        w_color = (max(0, min(255, r + shade)),
                   max(0, min(255, g + shade)),
                   max(0, min(255, b + shade)))

        bbox = draw.textbbox((0, 0), word, font=word_font)
        ww = bbox[2] - bbox[0]
        wh = bbox[3] - bbox[1]

        # ~20% of words get a very slight tilt
        if img and random.random() < 0.2 and len(word) > 1:
            angle = random.uniform(-1.2, 1.2)
            pad = 4
            tmp = Image.new("RGBA", (ww + pad * 2, wh + pad * 2), (0, 0, 0, 0))
            tmp_d = ImageDraw.Draw(tmp)
            tmp_d.text((pad, pad), word, font=word_font, fill=(*w_color, 255))
            tmp = tmp.rotate(angle, resample=Image.BICUBIC, expand=False)
            px = int(cx)
            py = int(y + dy)
            if 0 <= px < img.width - tmp.width and 0 <= py < img.height - tmp.height:
                img.paste(tmp, (px, py), tmp)
            else:
                draw.text((cx, y + dy), word, font=word_font, fill=w_color)
        else:
            draw.text((cx, y + dy), word, font=word_font, fill=w_color)

        # natural word spacing with slight variation
        space_w = font_size * random.uniform(0.28, 0.42)
        cx += ww + space_w
        # gentle baseline drift
        baseline_drift += drift_speed
        if abs(baseline_drift) > 2:
            drift_speed *= -0.7
        if random.random() < 0.1:
            drift_speed = random.uniform(-0.08, 0.08)


def scan_artifacts(img):
    """Apply scan-like post-processing."""
    # slight rotation (scanner misalignment)
    angle = random.uniform(-0.7, 0.7)
    img = img.rotate(angle, resample=Image.BICUBIC, expand=False,
                     fillcolor=PAPER_COLOR)
    # mild blur (scan softness)
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    # reduce contrast slightly
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(0.92)
    # add a bit more noise (scanner sensor noise)
    pixels = np.array(img, dtype=np.int16)
    noise = np.random.normal(0, 2.5, pixels.shape).astype(np.int16)
    pixels = np.clip(pixels + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(pixels)
    # slight brightness variation
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(random.uniform(0.96, 1.02))
    return img


# ── Extract text structure from existing PDF ────────────────────────────

def extract_content(pdf_path):
    """Pull structured text blocks from the clean PDF."""
    doc = fitz.open(pdf_path)
    pages = []
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        page_lines = []
        for b in blocks:
            if "lines" not in b:
                continue
            for line in b["lines"]:
                text = "".join(span["text"] for span in line["spans"])
                if not text.strip():
                    continue
                size = line["spans"][0]["size"]
                flags = line["spans"][0]["flags"]  # 1=superscript,2=italic,4=bold,...
                is_bold = bool(flags & (1 << 4))
                # classify
                if size >= 15:
                    kind = "title"
                elif size >= 12 and is_bold:
                    kind = "heading"
                elif is_bold:
                    kind = "bold"
                else:
                    kind = "body"
                # detect answer boxes (green background in original)
                color = line["spans"][0].get("color", 0)
                page_lines.append({"text": text, "kind": kind, "size": size,
                                   "bold": is_bold, "color": color})
        pages.append(page_lines)
    doc.close()
    return pages


def is_answer_line(line):
    """Heuristic: answer boxes have short bold text with = sign."""
    t = line["text"].strip()
    return line["bold"] and ("=" in t or t.startswith("|")) and len(t) < 60


# ── Render pages ────────────────────────────────────────────────────────

def render_pages(content_pages):
    fonts = load_fonts()
    images = []
    is_first_page = True
    # flatten all lines into one stream (name only on page 1)
    all_lines = []
    for page_lines in content_pages:
        all_lines.extend(page_lines)

    # filter: skip "Elzodxon Sharofaddinov" lines after first occurrence
    name_seen = False
    filtered = []
    for line in all_lines:
        t = line["text"].strip()
        if "Elzodxon" in t and "Sharofaddinov" in t:
            if name_seen:
                continue  # skip name on subsequent pages
            name_seen = True
        filtered.append(line)

    img = paper_background(PAGE_W, PAGE_H)
    draw = ImageDraw.Draw(img)
    y = MARGIN_T
    max_w = PAGE_W - MARGIN_L - MARGIN_R

    for line in filtered:
        text = line["text"].strip()
        if not text:
            continue

        if line["kind"] == "title":
            fs = fonts["title"]
            color = TITLE_COLOR
            measure_font = get_font(fs)
            bbox = draw.textbbox((0, 0), text, font=measure_font)
            tw = bbox[2] - bbox[0]
            x = (PAGE_W - tw) // 2
            draw_handwritten_line(draw, jitter(x, 4), jitter(y, 3),
                                  text, fs, color, img=img)
            y += 58
        elif line["kind"] == "heading":
            fs = fonts["heading"]
            color = INK_COLOR
            y += 20
            draw_handwritten_line(draw, jitter(MARGIN_L, 3), jitter(y, 2),
                                  text, fs, color, img=img)
            # sloppy underline
            uy = y + 42
            points = []
            lx = MARGIN_L
            line_end = MARGIN_L + len(text) * 15
            while lx < line_end:
                points.append((lx, uy + random.uniform(-1.5, 1.5)))
                lx += random.uniform(8, 20)
            if len(points) > 1:
                draw.line(points, fill=INK_COLOR, width=1)
            y += 58
        elif is_answer_line(line):
            fs = fonts["bold"]
            y += 6
            draw_handwritten_line(draw, jitter(MARGIN_L, 2), jitter(y, 2),
                                  text, fs, INK_COLOR, img=img)
            # hand-drawn underline beneath answer
            uy = y + 38
            measure_font = get_font(fs)
            bbox = draw.textbbox((0, 0), text, font=measure_font)
            tw = bbox[2] - bbox[0]
            pts = []
            lx = MARGIN_L - 4
            while lx < MARGIN_L + tw + 10:
                pts.append((lx, uy + random.uniform(-1.5, 1.5)))
                lx += random.uniform(6, 15)
            if len(pts) > 1:
                draw.line(pts, fill=INK_COLOR, width=2)
            y += 52
        elif line["bold"]:
            fs = fonts["bold"]
            draw_handwritten_line(draw, jitter(MARGIN_L, 2), jitter(y, 2),
                                  text, fs, INK_COLOR, img=img)
            y += 46
        else:
            fs = fonts["body"]
            wrapped = wrap_text(text, fs, max_w, draw)
            for wl in wrapped:
                if not wl:
                    y += 18
                    continue
                draw_handwritten_line(draw, jitter(MARGIN_L, 2),
                                      jitter(y, 1.5), wl, fs, INK_COLOR, img=img)
                y += 40

        # page overflow → new page
        if y > PAGE_H - MARGIN_T:
            img = scan_artifacts(img)
            images.append(img)
            img = paper_background(PAGE_W, PAGE_H)
            draw = ImageDraw.Draw(img)
            y = MARGIN_T

    # finalize last page
    img = scan_artifacts(img)
    images.append(img)

    return images


def save_pdf(images, path):
    if not images:
        return
    images[0].save(path, "PDF", resolution=DPI, save_all=True,
                   append_images=images[1:])
    print(f"Saved handwritten PDF: {path}  ({len(images)} pages)")


def main():
    print("Extracting content from clean PDF...")
    pages = extract_content(INPUT_PDF)
    print(f"  Found {len(pages)} page(s), {sum(len(p) for p in pages)} text lines")

    print("Rendering handwritten pages...")
    images = render_pages(pages)

    save_pdf(images, OUTPUT_PDF)


if __name__ == "__main__":
    main()

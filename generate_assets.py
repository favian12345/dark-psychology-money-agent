import os, random, subprocess
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

HASHTAGS = [
    "#money", "#wealth", "#mindset", "#psychology", "#darkpsychology",
    "#discipline", "#success", "#financialfreedom", "#selfimprovement",
    "#business", "#richmindset"
]

HOOKS = [
    "Nobody tells you this about money:",
    "Hard truth about money:",
    "Dark psychology of wealth:",
    "If you grew up broke, read this:",
    "This is why most people stay poor:"
]

BRAND_LINE = "YouTube: Brain Fuel Media | IG/TikTok: @Brain.FuelMedia"

def pick_hashtags(n=6):
    n = min(n, len(HASHTAGS))
    return " ".join(random.sample(HASHTAGS, n))

def load_blocks(path="lines.txt"):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()
    blocks = [b.strip() for b in raw.split("\n\n") if b.strip()]
    if not blocks:
        raise SystemExit("lines.txt has no valid blocks. Add text separated by blank lines.")
    return blocks

def normalize_post(block: str) -> str:
    lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
    text = "\n".join(lines)
    lower = text.lower()
    if not any(lower.startswith(h.lower()) for h in HOOKS):
        text = random.choice(HOOKS) + "\n" + text
    return text

def get_font(size: int, bold=True):
    # GitHub runner has DejaVu fonts. This path is stable on ubuntu‑latest.
    path = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(path, size=size)

def fit_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def render_card(out_path, W, H, main_text):
    # Background (dark gradient-ish)
    img = Image.new("RGB", (W, H), (10, 12, 18))
    draw = ImageDraw.Draw(img)
    # Simple subtle vignette
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([0, 0, W, H], fill=(0, 0, 0, 0))
    # corners darker
    od.ellipse([-W*0.3, -H*0.3, W*1.3, H*1.3], fill=(0, 0, 0, 90))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    # Layout
    pad = int(W * 0.08)
    brand_h = int(H * 0.10)
    top_y = int(H * 0.12)
    text_area_h = H - brand_h - top_y - int(H * 0.08)
    # Brand bar
    draw.rectangle([0, H - brand_h, W, H], fill=(6, 44, 120))
    brand_font = get_font(int(H * 0.028), bold=True)
    brand_w = draw.textlength(BRAND_LINE, font=brand_font)
    draw.text(((W - brand_w) / 2, H - brand_h + (brand_h - brand_font.size) / 2),
              BRAND_LINE, font=brand_font, fill=(255, 255, 255))
    # Main text: auto-size font to fit
    max_width = W - 2 * pad
    max_height = text_area_h
    # Start big, shrink until it fits
    size = int(H * 0.060)
    while size > int(H * 0.030):
        font = get_font(size, bold=True)
        lines = []
        for paragraph in main_text.split("\n"):
            paragraph = paragraph.strip()
            if not paragraph:
                lines.append("")  # keep spacing
                continue
            wrapped = fit_text(draw, paragraph, font, max_width)
            lines.extend(wrapped)
        # measure
        line_h = int(size * 1.25)
        total_h = line_h * len(lines)
        if total_h <= max_height and all(draw.textlength(l, font=font) <= max_width for l in lines):
            break
        size -= 2
    # Draw centered
    font = get_font(size, bold=True)
    line_h = int(size * 1.25)
    y = top_y + int((text_area_h - line_h * len(lines)) / 2)
    for l in lines:
        if l == "":
            y += int(line_h * 0.6)
            continue
        x = (W - draw.textlength(l, font=font)) / 2
        # soft shadow
        draw.text((x+2, y+2), l, font=font, fill=(0, 0, 0))
        draw.text((x, y), l, font=font, fill=(245, 245, 245))
        y += line_h
    img.save(out_path, "PNG")

def make_caption(post_text: str) -> str:
    return (f"{post_text}\n\n"
            "Watch again.\n\n"
            "#money #psychology #wealth #darkpsychology #discipline #shorts\n")

def make_video_from_image(image_path, out_mp4, seconds=61):
    cmd = [
        imageio_ffmpeg.get_ffmpeg_exe(), "-y",
        "-loop", "1", "-i", image_path,
        "-t", str(seconds),
        "-vf", "scale=1080:1920,format=yuv420p",
        "-r", "30",
        "-movflags", "+faststart",
        out_mp4
    ]
    subprocess.run(cmd, check=True)

def main():
    os.makedirs("output", exist_ok=True)
    blocks = load_blocks("lines.txt")
    if len(blocks) < 3:
        raise SystemExit("Need at least three blocks in lines.txt to generate 3 posts.")
    chosen_blocks = random.sample(blocks, 3)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    for idx, block in enumerate(chosen_blocks, start=1):
        normalized = normalize_post(block)
        caption = make_caption(normalized)
        # Save individual caption file
        with open(f"output/post_{idx}.txt", "w", encoding="utf-8") as f:
            f.write(caption)
        # Append to daily log with separator
        with open(f"output/posts_{today}.txt", "a", encoding="utf-8") as f:
            f.write(caption)
            f.write("\n" + ("-" * 30) + "\n\n")
        # Render images
        story_png = f"output/post_story_{idx}.png"
        feed_png = f"output/post_feed_{idx}.png"
        render_card(story_png, 1080, 1920, normalized)
        render_card(feed_png, 1080, 1350, normalized)
        # Generate static video
        make_video_from_image(story_png, f"output/short_{idx}.mp4", seconds=61)
    print("✅ Generated three posts and associated assets.")

if __name__ == "__main__":
    main()

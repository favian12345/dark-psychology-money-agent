import random
from datetime import datetime
import os

HASHTAGS = [
    "#money", "#wealth", "#mindset", "#psychology", "#darkpsychology",
    "#discipline", "#success", "#financialfreedom", "#selfimprovement",
    "#motivation", "#business", "#richmindset"
]

HOOKS = [
    "Nobody tells you this about money:",
    "Hard truth about money:",
    "Dark psychology of wealth:",
    "If you grew up broke, read this:",
    "This is why most people stay poor:"
]

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

def make_caption(post_text: str) -> str:
    return f"""{post_text}

Read that again.

{pick_hashtags()}
"""

def main():
    blocks = load_blocks("lines.txt")
    chosen = normalize_post(random.choice(blocks))
    caption = make_caption(chosen)

    os.makedirs("output", exist_ok=True)

    # Always overwrite today's main post
    with open("output/post.txt", "w", encoding="utf-8") as f:
        f.write(caption)

    # Append to a daily log (lets you scale later)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    with open(f"output/posts_{today}.txt", "a", encoding="utf-8") as f:
        f.write(caption)
        f.write("\n" + ("-" * 30) + "\n\n")

    print("✅ Generated output/post.txt")
    print(f"✅ Appended to output/posts_{today}.txt")
    print("\n--- PREVIEW ---\n")
    print(caption)

if __name__ == "__main__":
    main()

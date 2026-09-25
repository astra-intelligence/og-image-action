#!/usr/bin/env python3
"""Generate a beautiful OG social preview image for a GitHub repository."""
import os
import sys
import requests
from PIL import Image, ImageDraw, ImageFont

def get_repo_info(repo_full):
    """Fetch repo info from GitHub API."""
    token = os.environ.get('GITHUB_TOKEN', '')
    headers = {"User-Agent": "OG-Image-Action/1.0", "Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.get(
        f"https://api.github.com/repos/{repo_full}",
        headers=headers, timeout=15
    )
    if resp.status_code != 200:
        parts = repo_full.split('/')
        return {"name": parts[-1], "full_name": repo_full,
                "description": "A GitHub repository", "stargazers_count": 0,
                "language": None, "html_url": f"https://github.com/{repo_full}"}
    return resp.json()

def verify_license_key(license_key):
    if not license_key:
        return False
    try:
        resp = requests.post("https://api.gumroad.com/v2/licenses/verify",
            data={"product_permalink": "og-preview-api-license", "license_key": license_key}, timeout=10)
        return resp.json().get("success", False)
    except Exception:
        return False

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def wrap_text(text, font, max_w, draw):
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = f"{line} {w}".strip()
        bb = draw.textbbox((0, 0), test, font=font)
        if bb[2] - bb[0] <= max_w:
            line = test
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    return lines

def load_fonts():
    """Find the best available fonts."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    title_font = body_font = small_font = None
    for path in candidates:
        if os.path.exists(path):
            try:
                title_font = ImageFont.truetype(path, 56)
                body_font = ImageFont.truetype(path, 24)
                small_font = ImageFont.truetype(path, 16)
                return title_font, body_font, small_font
            except Exception:
                continue
    # Fallback to default
    d = ImageFont.load_default()
    return d, d, d

def generate_image(repo_info, output_path, template, is_premium):
    w, h = 1280, 640
    schemes = {
        "default":  {"bg": "#0d1117", "accent": "#58a6ff", "text": "#ffffff", "dim": "#8b949e"},
        "gradient": {"bg": "#0f172a", "accent": "#3b82f6", "text": "#f8fafc", "dim": "#94a3b8"},
        "minimal":  {"bg": "#ffffff", "accent": "#000000", "text": "#000000", "dim": "#666666"},
        "bold":     {"bg": "#1e1b4b", "accent": "#a78bfa", "text": "#ffffff", "dim": "#c4b5fd"},
        "dark":     {"bg": "#000000", "accent": "#10b981", "text": "#ffffff", "dim": "#6b7280"},
    }
    if is_premium:
        cb = os.environ.get('CUSTOM_BG', '')
        ca = os.environ.get('CUSTOM_ACCENT', '')
        if cb and ca:
            schemes["premium"] = {"bg": cb, "accent": ca, "text": "#ffffff", "dim": "#9ca3af"}

    scheme = schemes.get(template, schemes["default"])
    bg = hex_to_rgb(scheme["bg"])
    accent = hex_to_rgb(scheme["accent"])
    text_c = hex_to_rgb(scheme["text"])
    dim_c = hex_to_rgb(scheme["dim"])

    img = Image.new('RGB', (w, h), bg)
    draw = ImageDraw.Draw(img)
    title_font, body_font, small_font = load_fonts()

    # Accent bar at bottom
    for i in range(6):
        shade = tuple(max(0, min(255, a + 8 + i * 12)) for a in accent)
        draw.rectangle([0, h - 8 + i, w, h - 7 + i], fill=shade)

    # Subtle decorative circle
    circle_c = tuple(max(0, c - 20) for c in accent)
    draw.ellipse([w - 200, -100, w + 50, 150], fill=circle_c)

    # Repo name
    repo_name = repo_info.get('full_name', repo_info.get('name', 'owner/repo'))
    max_name_w = w - 120
    font_size = 56
    while font_size > 28:
        try:
            tf = ImageFont.truetype(title_font.path, font_size)
        except Exception:
            break
        bb = draw.textbbox((0, 0), repo_name, font=tf)
        if bb[2] - bb[0] <= max_name_w:
            title_font = tf
            break
        font_size -= 4

    draw.text((60, 180), repo_name, fill=text_c, font=title_font)

    # Description
    desc = repo_info.get('description') or 'A GitHub project'
    desc_lines = wrap_text(desc, body_font, w - 120, draw)
    y = 260
    for line in desc_lines[:4]:
        draw.text((60, y), line, fill=dim_c, font=body_font)
        y += 30

    # Stats
    stats = []
    stars = repo_info.get('stargazers_count', 0)
    lang = repo_info.get('language')
    if stars: stats.append(f"\u2b50 {stars} stars")
    if lang: stats.append(f"\ud83d\udd35 {lang}")
    if stats:
        draw.text((60, y + 20), "  |  ".join(stats), fill=accent, font=small_font)

    # Premium badge
    if is_premium:
        badge = "PREMIUM"
        bb = draw.textbbox((0, 0), badge, font=small_font)
        bw = bb[2] - bb[0]
        bx, by = w - bw - 60, 20
        draw.rectangle([bx - 8, by - 4, bx + bw + 8, by + 20], fill=accent)
        draw.text((bx, by), badge, fill=bg, font=small_font)

    # Footer
    brand = "github.com/astra-intelligence/adventure-products"
    draw.text((60, h - 40), brand, fill=dim_c, font=small_font)

    img.save(output_path, 'PNG')
    print(f"Saved: {output_path} ({img.size[0]}x{img.size[1]})")
    return output_path

def main():
    repo = os.environ.get('INPUT_REPO', '')
    output = os.environ.get('INPUT_OUTPUT', 'og-image.png')
    template = os.environ.get('INPUT_TEMPLATE', 'default')
    license_key = os.environ.get('INPUT_LICENSE_KEY', '')

    if not repo:
        print("::error::No repo specified")
        sys.exit(1)

    print(f"Generating OG Image for {repo}")
    is_premium = verify_license_key(license_key)
    if license_key and not is_premium:
        print("::warning::Invalid license key. Using free template.")
    elif is_premium:
        print("::notice::Premium license verified!")

    repo_info = get_repo_info(repo)
    generate_image(repo_info, output, template, is_premium)

if __name__ == '__main__':
    main()
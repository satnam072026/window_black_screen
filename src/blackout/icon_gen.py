"""
icon_gen.py - Multi-resolution ICO and PNG icon generator for BlackoutMode.
"""

import os
from PIL import Image, ImageDraw


def create_blackout_icon(size: int = 256) -> Image.Image:
    """Create a high-resolution PIL Image for BlackoutMode icon."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = size * 0.06
    center = size / 2.0

    # Outer deep charcoal/black circle with antialiased border
    bg_bbox = [margin, margin, size - margin, size - margin]
    draw.ellipse(bg_bbox, fill=(18, 18, 22, 255), outline=(230, 230, 235, 255), width=max(1, int(size * 0.035)))

    # Inner moon/eclipse symbol: outer white crescent
    inner_margin = size * 0.22
    inner_bbox = [inner_margin, inner_margin, size - inner_margin, size - inner_margin]
    draw.ellipse(inner_bbox, fill=(245, 245, 250, 255))

    # Dark cutout offset to create sleek crescent
    cutout_offset_x = size * 0.13
    cutout_offset_y = size * 0.05
    cutout_bbox = [
        inner_margin + cutout_offset_x,
        inner_margin - cutout_offset_y,
        size - inner_margin + cutout_offset_x,
        size - inner_margin - cutout_offset_y,
    ]
    draw.ellipse(cutout_bbox, fill=(18, 18, 22, 255))

    # Center minimal power indicator dot
    dot_size = size * 0.045
    dot_x = center - size * 0.07
    dot_y = center + size * 0.07
    draw.ellipse([dot_x - dot_size, dot_y - dot_size, dot_x + dot_size, dot_y + dot_size], fill=(255, 255, 255, 255))

    return img


def generate_all_icons(target_dir: str) -> None:
    """Generates both icon.png and multi-resolution icon.ico into target_dir."""
    os.makedirs(target_dir, exist_ok=True)
    master_img = create_blackout_icon(256)

    # Save PNG
    png_path = os.path.join(target_dir, "icon.png")
    master_img.save(png_path, format="PNG")

    # Save high-DPI multi-resolution Windows ICO (16, 24, 32, 48, 64, 128, 256 px)
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_path = os.path.join(target_dir, "icon.ico")
    master_img.save(ico_path, format="ICO", sizes=sizes)


if __name__ == "__main__":
    generate_all_icons("assets")

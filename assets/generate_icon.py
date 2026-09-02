"""
Utility script to generate icon.ico for AI Language Translation Tool.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def generate_icon():
    assets_dir = Path(__file__).resolve().parent
    assets_dir.mkdir(parents=True, exist_ok=True)
    icon_path = assets_dir / "icon.ico"

    # Create a high-res image canvas (256x256)
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw rounded rectangle background with gradient effect (Deep Indigo/Blue)
    margin = 12
    radius = 48
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=radius,
        fill="#2563EB",
        outline="#1D4ED8",
        width=4
    )

    # Inner decorative accent circle/pill
    draw.ellipse([50, 50, 206, 206], fill="#1E40AF")

    # Draw Translation Symbol / Letter "A" & Asian/Indian symbol "अ"
    try:
        # Try to load a font if available, or draw styled text/shapes
        font_large = ImageFont.truetype("arial.ttf", 90)
        draw.text((80, 75), "A", fill="#FFFFFF", font=font_large)
        draw.text((135, 125), "अ", fill="#60A5FA", font=font_large)
    except Exception:
        # Fallback drawing geometric translate icon
        draw.text((70, 80), "A", fill="#FFFFFF")
        draw.text((140, 130), "T", fill="#60A5FA")

    # Save as ICO with multiple icon sizes
    img.save(
        icon_path,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    )
    print(f"Icon generated successfully at: {icon_path}")

if __name__ == "__main__":
    generate_icon()

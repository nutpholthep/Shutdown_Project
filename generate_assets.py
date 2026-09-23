"""
Generate Application Assets (Windows 11 Fluent Design Icon & Version Info)
for Shutdown Scheduler PyInstaller Build.
"""

import os
from PIL import Image, ImageDraw


def create_app_icon(output_path="app_icon.ico"):
    """
    Create a crisp, professional Windows 11 Fluent Design multi-resolution .ico file.
    Uses 4x supersampling to ensure razor-sharp edges and smooth antialiasing at all sizes.
    """
    resolutions = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []

    for size in resolutions:
        target_w, target_h = size
        scale = 4
        w = target_w * scale
        h = target_h * scale

        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Outer padding
        pad = int(w * 0.06)
        cx, cy = w / 2, h / 2
        radius = (w - 2 * pad) / 2

        # 1. Subtle shadow / back ring
        shadow_box = [pad - scale, pad + scale, w - pad - scale, h - pad + scale]
        draw.ellipse(shadow_box, fill=(0, 0, 0, 45))

        # 2. Main Windows 11 Fluent Accent Disc (#0078d4 base with deep gradient feel)
        main_box = [pad, pad, w - pad, h - pad]
        draw.ellipse(main_box, fill=(24, 108, 192, 255))

        # 3. Subtle inner highlight rim
        rim_width = max(scale, int(w * 0.025))
        rim_box = [pad + rim_width // 2, pad + rim_width // 2, w - pad - rim_width // 2, h - pad - rim_width // 2]
        draw.ellipse(rim_box, outline=(96, 205, 255, 140), width=rim_width)

        # 4. Modern Power Symbol / Timer Glyph (Crisp White #FFFFFF)
        # Power arc: 300 degrees to 240 degrees (gap at top)
        arc_inset = int(w * 0.22)
        arc_box = [arc_inset, arc_inset, w - arc_inset, h - arc_inset]
        stroke_w = max(scale * 2, int(w * 0.08))
        draw.arc(arc_box, start=305, end=235, fill=(255, 255, 255, 255), width=stroke_w)

        # Power vertical pin
        pin_top = int(w * 0.16)
        pin_bot = int(cy + stroke_w * 0.2)
        half_pin = stroke_w // 2
        # Rounded capsule pin
        draw.rounded_rectangle([cx - half_pin, pin_top, cx + half_pin, pin_bot], radius=half_pin, fill=(255, 255, 255, 255))

        # Downsample with high-quality Lanczos resampling
        resampled = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        images.append(resampled)

    # Save multi-resolution icon
    images[-1].save(
        output_path,
        format="ICO",
        sizes=[(im.width, im.height) for im in images],
        append_images=images[:-1]
    )
    print(f"Created Windows 11 Fluent application icon: {output_path}")


def create_version_info(output_path="file_version_info.txt"):
    """Create Windows Version Resource file for PyInstaller."""
    version_content = """# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms776495.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(4, 1, 0, 0),
    prodvers=(4, 1, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'Shutdown Project'),
          StringStruct(u'FileDescription', u'Shutdown Scheduler Desktop Application (Windows 11 Fluent Edition)'),
          StringStruct(u'FileVersion', u'4.1.0.0'),
          StringStruct(u'InternalName', u'ShutdownScheduler'),
          StringStruct(u'LegalCopyright', u'Copyright (C) 2026 Shutdown Project. All rights reserved.'),
          StringStruct(u'OriginalFilename', u'ShutdownScheduler.exe'),
          StringStruct(u'ProductName', u'Shutdown Scheduler'),
          StringStruct(u'ProductVersion', u'4.1.0.0'),
          StringStruct(u'Comments', u'Modern Windows 11 Fluent utility to schedule automatic shutdown')]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(version_content)
    print(f"Created version info: {output_path}")


if __name__ == "__main__":
    create_app_icon()
    create_version_info()

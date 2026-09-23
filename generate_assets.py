"""
Generate Application Assets (Icon & Windows Version Info)
for Shutdown Scheduler PyInstaller Build.
"""

import os
from PIL import Image, ImageDraw


def create_app_icon(output_path="app_icon.ico"):
    """Create a high-quality multi-resolution .ico file with a modern clock/power design."""
    resolutions = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []

    for size in resolutions:
        w, h = size
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Background rounded badge / circle
        margin = max(1, w // 16)
        draw.ellipse([margin, margin, w - margin, h - margin], fill="#1e1e24", outline="#ff6b6b", width=max(1, w // 24))

        # Dial markings / subtle inner ring
        inner_margin = margin + max(2, w // 10)
        draw.ellipse([inner_margin, inner_margin, w - inner_margin, h - inner_margin], outline="#48484a", width=max(1, w // 32))

        # Power Arc (C-shape)
        arc_box = [inner_margin + max(1, w // 12), inner_margin + max(1, w // 12), 
                   w - (inner_margin + max(1, w // 12)), h - (inner_margin + max(1, w // 12))]
        draw.arc(arc_box, start=300, end=240, fill="#ff6b6b", width=max(2, w // 12))

        # Center Power / Clock vertical pin
        center_x = w / 2
        center_y = h / 2
        pin_top = inner_margin + max(1, w // 20)
        pin_bottom = center_y
        draw.line([(center_x, pin_top), (center_x, pin_bottom)], fill="#f2f2f7", width=max(2, w // 14))

        # Center dot
        dot_r = max(1.5, w / 20)
        draw.ellipse([center_x - dot_r, center_y - dot_r, center_x + dot_r, center_y + dot_r], fill="#f2f2f7")

        images.append(img)

    # Save multi-resolution icon
    images[-1].save(
        output_path,
        format="ICO",
        sizes=[(img.width, img.height) for img in images],
        append_images=images[:-1]
    )
    print(f"Created application icon: {output_path}")


def create_version_info(output_path="file_version_info.txt"):
    """Create Windows Version Resource file for PyInstaller."""
    version_content = """# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms776495.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(4, 0, 0, 0),
    prodvers=(4, 0, 0, 0),
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
          StringStruct(u'FileDescription', u'Shutdown Scheduler Desktop Application'),
          StringStruct(u'FileVersion', u'4.0.0.0'),
          StringStruct(u'InternalName', u'ShutdownScheduler'),
          StringStruct(u'LegalCopyright', u'Copyright (C) 2026 Shutdown Project. All rights reserved.'),
          StringStruct(u'OriginalFilename', u'ShutdownScheduler.exe'),
          StringStruct(u'ProductName', u'Shutdown Scheduler'),
          StringStruct(u'ProductVersion', u'4.0.0.0'),
          StringStruct(u'Comments', u'Desktop application to schedule automatic shutdown')]
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

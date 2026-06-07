from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1] / "assets" / "guangyuan-xiaolongbao"
FILES = [
    "vegetables-wide.jpg",
    "xiaolongbao-steamer.jpg",
    "market-entrance.jpg",
    "meat-counter.jpg",
    "kitchen-stove.jpg",
    "kitchen-wide.jpg",
    "vegetables-close.jpg",
    "seafood-counter.jpg",
    "fruit-stand.jpg",
    "wukang-road.jpg",
    "huashan-greenland.jpg",
    "xujiahui-skywalk-cropped.jpg",
    "xujiahui-park.jpg",
    "lu-portrait.jpg",
    "lu-with-guest.jpg",
    "flower-stand.jpg",
]

MAX_SIDE = 1000
QUALITY = 72

for name in FILES:
    path = ROOT / name
    before = path.stat().st_size
    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        img.thumbnail((MAX_SIDE, MAX_SIDE), Image.Resampling.LANCZOS)
        img.save(path, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    after = path.stat().st_size
    print(f"{name}: {before / 1024:.0f}K -> {after / 1024:.0f}K")

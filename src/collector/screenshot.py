from PIL import Image
from io import BytesIO

def naive_sections_from_full(png_bytes: bytes):
    img = Image.open(BytesIO(png_bytes)).convert("RGB")
    w, h = img.size
    thirds = [(0, 0, w, h//3), (0, h//3, w, 2*h//3), (0, 2*h//3, w, h)]
    crops = []
    for i, (x1, y1, x2, y2) in enumerate(thirds):
        crop = img.crop((x1, y1, x2, y2))
        bio = BytesIO(); crop.save(bio, format="PNG")
        crops.append({"id": f"sec{i+1}", "bbox": [x1, y1, x2-x1, y2-y1], "png": bio.getvalue()})
    return {"w": w, "h": h, "sections": crops}

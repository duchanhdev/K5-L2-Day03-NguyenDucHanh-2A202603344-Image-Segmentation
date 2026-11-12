"""Render small overlays so the report can cite what the exports actually contain."""
import io
import json
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

OUT = Path("_tmp_preview")
OUT.mkdir(exist_ok=True)


def decode_compressed_rle(s: str):
    counts = []
    p = 0
    m = 0
    while p < len(s):
        x = 0
        k = 0
        more = 1
        while more:
            c = ord(s[p]) - 48
            x |= (c & 0x1F) << (5 * k)
            more = c & 0x20
            p += 1
            k += 1
            if (not more) and (c & 0x10):
                x |= -1 << (5 * k)
        if m > 2:
            x += counts[m - 2]
        counts.append(int(x))
        m += 1
    return counts


def rle_mask(seg, h, w):
    counts = seg["counts"]
    if isinstance(counts, str):
        counts = decode_compressed_rle(counts)
    flat = np.zeros(h * w, dtype=np.uint8)
    idx = 0
    val = 0
    for run in counts:
        if val:
            flat[idx : idx + run] = 1
        idx += run
        val ^= 1
    return flat.reshape((w, h)).T  # column-major


def load_coco(name):
    with zipfile.ZipFile(Path("submissions") / f"{name}.zip") as z:
        js = [n for n in z.namelist() if n.lower().endswith(".json") and "annotation" in n.lower()][0]
        return json.loads(z.read(js))


def overlay_ids(task, image_name, ann_ids, out_name):
    data = load_coco(task)
    images = {im["id"]: im for im in data["images"]}
    cats = {c["id"]: c["name"] for c in data["categories"]}
    im = next(v for v in images.values() if Path(v["file_name"]).name == image_name)
    src = Image.open(Path("data") / {
        "medium_instance": "tiers/medium_instance",
        "hard_panoptic": "tiers/hard_panoptic",
        "cp1_holes": "checkpoints/cp1_holes",
        "cp2_slice": "checkpoints/cp2_slice",
        "cp5_occlusion": "checkpoints/cp5_occlusion",
    }[task] / "images" / image_name).convert("RGB")
    base = np.array(src)
    color = {
        "person": (220, 20, 60),
        "bicycle": (119, 11, 32),
        "car": (0, 80, 255),
        "motorcycle": (255, 140, 0),
        "bus": (0, 180, 180),
        "truck": (255, 0, 255),
        "road": (128, 64, 128),
        "sidewalk": (244, 35, 232),
        "building": (70, 70, 70),
        "vegetation": (107, 142, 35),
        "sky": (70, 130, 180),
        "traffic light": (250, 170, 30),
    }
    h, w = im["height"], im["width"]
    layer = np.zeros_like(base)
    chosen = [a for a in data["annotations"] if a["image_id"] == im["id"] and (ann_ids is None or a["id"] in ann_ids)]
    for a in chosen:
        m = rle_mask(a["segmentation"], h, w)
        layer[m.astype(bool)] = color.get(cats[a["category_id"]], (255, 255, 0))
    blend = (0.55 * base + 0.45 * np.where(layer.any(axis=2, keepdims=True), layer, base)).astype(np.uint8)
    Image.fromarray(blend).save(OUT / out_name)
    print(out_name, "anns", [(a["id"], cats[a["category_id"]]) for a in chosen])


def semantic(task, image_stem, folder):
    with zipfile.ZipFile(Path("submissions") / f"{task}.zip") as z:
        png = [n for n in z.namelist() if n.endswith(image_stem + ".png") and "SegmentationClass" in n][0]
        mask = Image.open(io.BytesIO(z.read(png))).convert("RGB")
    src = Image.open(next(Path(folder).glob(image_stem + ".jpg"))).convert("RGB")
    base = np.array(src.resize(mask.size))
    m = np.array(mask)
    labeled = m.any(axis=2)
    blend = base.copy()
    blend[labeled] = (0.5 * base[labeled] + 0.5 * m[labeled]).astype(np.uint8)
    Image.fromarray(blend).save(OUT / f"{task}_{image_stem[:8]}.jpg")
    print(task, image_stem, "labeled_frac", round(float(labeled.mean()), 3))


overlay_ids("medium_instance", "000000181542.jpg", {1, 6, 13}, "med_181542_truck_moto_person.jpg")
overlay_ids("cp1_holes", "000000144300.jpg", {4}, "cp1_motorcycle.jpg")
overlay_ids("hard_panoptic", "000000350023.jpg", None, "hard_350023.jpg")
overlay_ids("cp2_slice", "000000017627.jpg", None, "cp2.jpg")
overlay_ids("cp5_occlusion", "000000336232.jpg", {44, 57, 35}, "cp5_front.jpg")
semantic("cp4_curb", "7d83710e-4697c3b2", "data/checkpoints/cp4_curb/images")
semantic("cp6_coverage", "7daa6479-67988f3f", "data/checkpoints/cp6_coverage/images")
semantic("easy_semantic", "7ee6d192-89e2408b", "data/tiers/easy_semantic/images")
semantic("cp3_thin", "839f7736-abe28069", "data/checkpoints/cp3_thin/images")
semantic("easy_semantic", "81ae7cbb-6bc63a4a", "data/tiers/easy_semantic/images")

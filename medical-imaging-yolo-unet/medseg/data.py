"""Préparation des données.

Deux sources possibles :

* ``kvasir`` : le jeu de données public Kvasir-SEG (1000 images d'endoscopie
  colorectale avec masques de polypes annotés par des experts).
* ``synthetic`` : des images d'endoscopie simulées, générées localement, pour
  tester toute la chaîne sans téléchargement.

Les deux sont convertis vers la même arborescence, compatible Ultralytics ::

    <out>/images/{train,val,test}/xxx.png   image RGB
    <out>/masks/{train,val,test}/xxx.png    masque binaire (0/255)
    <out>/labels/{train,val,test}/xxx.txt   boîtes YOLO "cls cx cy w h" (normalisées)
    <out>/data.yaml                         fichier de configuration YOLO

Les boîtes de détection sont dérivées des masques (composantes connexes), ce qui
garantit que la détection et la segmentation décrivent exactement les mêmes lésions.
"""

from __future__ import annotations

import random
import shutil
import urllib.request
import zipfile
from pathlib import Path

import cv2
import numpy as np

KVASIR_URL = "https://datasets.simula.no/downloads/kvasir-seg.zip"
SPLITS = ("train", "val", "test")
CLASS_NAMES = {0: "polyp"}


# --------------------------------------------------------------------------- #
# Masques -> boîtes YOLO
# --------------------------------------------------------------------------- #
def mask_to_boxes(mask: np.ndarray, min_area: int = 64) -> list[tuple[int, int, int, int]]:
    """Retourne les boîtes (x1, y1, x2, y2) des composantes connexes d'un masque binaire."""
    binary = (mask > 127).astype(np.uint8)
    n, _, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    boxes = []
    for i in range(1, n):  # 0 = fond
        x, y, w, h, area = stats[i]
        if area >= min_area:
            boxes.append((int(x), int(y), int(x + w), int(y + h)))
    return boxes


def boxes_to_yolo(boxes, width: int, height: int, cls: int = 0) -> str:
    lines = []
    for x1, y1, x2, y2 in boxes:
        cx = (x1 + x2) / 2 / width
        cy = (y1 + y2) / 2 / height
        bw = (x2 - x1) / width
        bh = (y2 - y1) / height
        lines.append(f"{cls} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")
    return "\n".join(lines) + ("\n" if lines else "")


def _write_sample(out: Path, split: str, name: str, image: np.ndarray, mask: np.ndarray) -> None:
    """Écrit image + masque + étiquettes YOLO d'un échantillon."""
    h, w = mask.shape[:2]
    mask = np.where(mask > 127, 255, 0).astype(np.uint8)
    cv2.imwrite(str(out / "images" / split / f"{name}.png"), image)
    cv2.imwrite(str(out / "masks" / split / f"{name}.png"), mask)
    (out / "labels" / split / f"{name}.txt").write_text(boxes_to_yolo(mask_to_boxes(mask), w, h))


def _make_dirs(out: Path) -> None:
    for kind in ("images", "masks", "labels"):
        for split in SPLITS:
            (out / kind / split).mkdir(parents=True, exist_ok=True)


def write_data_yaml(out: Path) -> Path:
    yaml_path = out / "data.yaml"
    names = "\n".join(f"  {k}: {v}" for k, v in CLASS_NAMES.items())
    yaml_path.write_text(
        f"path: {out.resolve()}\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n"
        f"names:\n{names}\n"
    )
    return yaml_path


def split_names(names: list[str], val: float, test: float, seed: int) -> dict[str, list[str]]:
    names = sorted(names)
    random.Random(seed).shuffle(names)
    n_test = int(round(len(names) * test))
    n_val = int(round(len(names) * val))
    return {
        "test": names[:n_test],
        "val": names[n_test : n_test + n_val],
        "train": names[n_test + n_val :],
    }


# --------------------------------------------------------------------------- #
# Kvasir-SEG
# --------------------------------------------------------------------------- #
def download_kvasir(raw_dir: Path) -> Path:
    """Télécharge et décompresse Kvasir-SEG si nécessaire. Retourne le dossier Kvasir-SEG."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    target = raw_dir / "Kvasir-SEG"
    if (target / "images").is_dir():
        return target
    zip_path = raw_dir / "kvasir-seg.zip"
    if not zip_path.exists():
        print(f"Téléchargement de {KVASIR_URL} ...")
        urllib.request.urlretrieve(KVASIR_URL, zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(raw_dir)
    # Le zip contient parfois un dossier "kvasir-seg/Kvasir-SEG"
    if not (target / "images").is_dir():
        found = next(raw_dir.rglob("Kvasir-SEG/images"), None)
        if found is None:
            raise FileNotFoundError("Structure Kvasir-SEG inattendue dans l'archive")
        shutil.move(str(found.parent), str(target))
    return target


def prepare_kvasir(
    out: Path, raw_dir: Path, val: float = 0.1, test: float = 0.1, seed: int = 42, max_size: int = 640
) -> Path:
    src = download_kvasir(raw_dir)
    _make_dirs(out)
    names = [p.stem for p in (src / "images").glob("*.jpg")]
    for split, items in split_names(names, val, test, seed).items():
        for name in items:
            image = cv2.imread(str(src / "images" / f"{name}.jpg"), cv2.IMREAD_COLOR)
            mask = cv2.imread(str(src / "masks" / f"{name}.jpg"), cv2.IMREAD_GRAYSCALE)
            scale = max_size / max(image.shape[:2])
            if scale < 1:
                size = (int(image.shape[1] * scale), int(image.shape[0] * scale))
                image = cv2.resize(image, size, interpolation=cv2.INTER_AREA)
                mask = cv2.resize(mask, size, interpolation=cv2.INTER_NEAREST)
            _write_sample(out, split, name, image, mask)
        print(f"  {split}: {len(items)} images")
    return write_data_yaml(out)


# --------------------------------------------------------------------------- #
# Données synthétiques (endoscopie simulée)
# --------------------------------------------------------------------------- #
def synth_endoscopy(rng: np.random.Generator, size: int = 320) -> tuple[np.ndarray, np.ndarray]:
    """Génère une image d'endoscopie simulée (BGR) et son masque de polypes.

    Fond : muqueuse rosée texturée + vaisseaux + vignettage.
    Lésions : 0 à 3 « polypes » elliptiques, déformés, ombrés et légèrement plus rouges.
    """
    s = size
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)

    # Muqueuse : couleur de base + bruit basse fréquence
    base = np.array([110, 120, 200], np.float32) + rng.normal(0, 12, 3)
    noise = cv2.resize(rng.normal(0, 1, (s // 16, s // 16)).astype(np.float32), (s, s), interpolation=cv2.INTER_CUBIC)
    img = np.clip(base[None, None, :] + 18 * noise[..., None], 0, 255)

    # Vaisseaux sanguins
    vessels = np.zeros((s, s), np.uint8)
    for _ in range(rng.integers(4, 10)):
        pts = np.cumsum(rng.normal(0, s / 12, (8, 2)), axis=0) + rng.uniform(0, s, 2)
        cv2.polylines(vessels, [pts.astype(np.int32)], False, 255, int(rng.integers(1, 3)))
    vessels = cv2.GaussianBlur(vessels, (5, 5), 0).astype(np.float32) / 255
    img = img * (1 - 0.35 * vessels[..., None]) + np.array([40, 30, 140]) * 0.35 * vessels[..., None]

    # Polypes
    mask = np.zeros((s, s), np.uint8)
    for _ in range(rng.choice([0, 1, 1, 1, 2, 2, 3])):
        cx, cy = rng.uniform(0.2 * s, 0.8 * s, 2)
        a, b = rng.uniform(0.06 * s, 0.18 * s, 2)
        theta = rng.uniform(0, np.pi)
        xr = (xx - cx) * np.cos(theta) + (yy - cy) * np.sin(theta)
        yr = -(xx - cx) * np.sin(theta) + (yy - cy) * np.cos(theta)
        # contour irrégulier
        ang = np.arctan2(yr, xr)
        wobble = 1 + 0.12 * np.sin(3 * ang + rng.uniform(0, 6)) + 0.06 * np.sin(5 * ang + rng.uniform(0, 6))
        r = np.sqrt((xr / a) ** 2 + (yr / b) ** 2) / wobble
        inside = r < 1
        mask[inside] = 255
        # relief : dôme éclairé par le haut-gauche + teinte plus rouge
        dome = np.clip(1 - r, 0, 1)
        light = 0.5 + 0.5 * np.clip(-(xr + yr) / (a + b), -1, 1)
        tint = np.array([-8, -12, 10], np.float32) + rng.normal(0, 6, 3)
        texture = 10 * cv2.resize(rng.normal(0, 1, (s // 8, s // 8)).astype(np.float32), (s, s))
        img = np.where(
            inside[..., None],
            img + tint + (35 * dome * light + texture)[..., None] - (20 * (1 - dome))[..., None],
            img,
        )
        # ombre portée sous le polype (bord bas-droit)
        rim = (r >= 1) & (r < 1.15) & ((xr + yr) > 0)
        img[rim] *= 0.8

    # Leurres : plis de la muqueuse et zones inflammatoires rouges (non annotées)
    for _ in range(rng.integers(1, 4)):
        c = tuple(int(v) for v in rng.uniform(0, s, 2))
        axes = tuple(int(v) for v in rng.uniform(0.15 * s, 0.4 * s, 2))
        fold = np.zeros((s, s), np.uint8)
        cv2.ellipse(fold, c, axes, float(rng.uniform(0, 180)), 0, float(rng.uniform(60, 160)), 255, int(rng.integers(3, 7)))
        fold = cv2.GaussianBlur(fold, (9, 9), 0).astype(np.float32) / 255
        img = img * (1 - 0.35 * fold[..., None])
    for _ in range(rng.integers(0, 3)):
        c = rng.uniform(0, s, 2)
        rad = rng.uniform(0.04 * s, 0.12 * s)
        spot = np.exp(-(((xx - c[0]) ** 2 + (yy - c[1]) ** 2) / (2 * rad**2)))
        img = img + (spot[..., None] * np.array([-12, -15, 15], np.float32))

    # Reflets spéculaires (fréquents en endoscopie)
    for _ in range(rng.integers(2, 7)):
        c = tuple(int(v) for v in rng.uniform(0, s, 2))
        cv2.circle(img, c, int(rng.integers(1, 4)), (255, 255, 255), -1)

    # Vignettage circulaire typique de l'endoscope
    rr = np.sqrt((xx - s / 2) ** 2 + (yy - s / 2) ** 2) / (s / 2)
    vignette = np.clip(1.25 - rr**2 * 0.9, 0, 1)
    img = img * vignette[..., None]
    img = cv2.GaussianBlur(np.clip(img, 0, 255).astype(np.uint8), (3, 3), 0)
    img = np.clip(img.astype(np.float32) + rng.normal(0, 4, img.shape), 0, 255).astype(np.uint8)
    return img, mask


def prepare_synthetic(out: Path, n: int = 600, size: int = 320, val: float = 0.15, test: float = 0.15, seed: int = 0) -> Path:
    _make_dirs(out)
    rng = np.random.default_rng(seed)
    names = [f"synth_{i:04d}" for i in range(n)]
    split_of = {name: split for split, items in split_names(names, val, test, seed).items() for name in items}
    for name in names:
        image, mask = synth_endoscopy(rng, size)
        _write_sample(out, split_of[name], name, image, mask)
    for split in SPLITS:
        print(f"  {split}: {sum(v == split for v in split_of.values())} images")
    return write_data_yaml(out)

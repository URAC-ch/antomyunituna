"""Dataset PyTorch pour la segmentation U-Net.

Pour que la même U-Net fonctionne à la fois sur l'image entière et sur les
régions proposées par YOLO (pipeline en cascade), l'entraînement mélange :

* des images entières (probabilité ``1 - crop_prob``) ;
* des recadrages autour d'une lésion annotée, avec une marge aléatoire qui
  imite l'imprécision des boîtes prédites par le détecteur.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset

from .data import mask_to_boxes

MEAN = np.array([0.485, 0.456, 0.406], np.float32)
STD = np.array([0.229, 0.224, 0.225], np.float32)


def expand_box(box, width: int, height: int, margin: float) -> tuple[int, int, int, int]:
    """Agrandit une boîte (x1, y1, x2, y2) d'une marge relative, en restant dans l'image."""
    x1, y1, x2, y2 = box
    mx, my = (x2 - x1) * margin, (y2 - y1) * margin
    return (
        max(0, int(x1 - mx)),
        max(0, int(y1 - my)),
        min(width, int(np.ceil(x2 + mx))),
        min(height, int(np.ceil(y2 + my))),
    )


def to_tensor(image_bgr: np.ndarray, size: int) -> torch.Tensor:
    """BGR uint8 -> tenseur normalisé (3, size, size)."""
    rgb = cv2.cvtColor(cv2.resize(image_bgr, (size, size), interpolation=cv2.INTER_LINEAR), cv2.COLOR_BGR2RGB)
    x = (rgb.astype(np.float32) / 255 - MEAN) / STD
    return torch.from_numpy(x.transpose(2, 0, 1).copy())


class SegmentationDataset(Dataset):
    def __init__(self, root: str | Path, split: str, size: int = 256, augment: bool = False, crop_prob: float = 0.5):
        root = Path(root)
        self.images = sorted((root / "images" / split).glob("*.png"))
        self.mask_dir = root / "masks" / split
        if not self.images:
            raise FileNotFoundError(f"Aucune image dans {root / 'images' / split}")
        self.size = size
        self.augment = augment
        self.crop_prob = crop_prob if augment else 0.0
        self.rng = np.random.default_rng()

    def __len__(self) -> int:
        return len(self.images)

    def _random_crop(self, image, mask):
        boxes = mask_to_boxes(mask)
        if not boxes:
            return image, mask
        box = boxes[self.rng.integers(len(boxes))]
        h, w = mask.shape
        # marge et décalage aléatoires ~ erreurs du détecteur
        margin = self.rng.uniform(0.05, 0.5)
        bw, bh = box[2] - box[0], box[3] - box[1]
        dx, dy = self.rng.normal(0, 0.08, 2) * (bw, bh)
        shifted = (box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy)
        x1, y1, x2, y2 = expand_box(shifted, w, h, margin)
        if x2 - x1 < 8 or y2 - y1 < 8:
            return image, mask
        return image[y1:y2, x1:x2], mask[y1:y2, x1:x2]

    def _augment(self, image, mask):
        if self.rng.random() < 0.5:
            image, mask = image[:, ::-1], mask[:, ::-1]
        if self.rng.random() < 0.5:
            image, mask = image[::-1], mask[::-1]
        k = int(self.rng.integers(4))
        image, mask = np.rot90(image, k), np.rot90(mask, k)
        # luminosité / contraste / teinte légère
        alpha = self.rng.uniform(0.8, 1.2)
        beta = self.rng.uniform(-20, 20)
        image = np.clip(image.astype(np.float32) * alpha + beta, 0, 255)
        image = np.clip(image * self.rng.uniform(0.92, 1.08, 3), 0, 255).astype(np.uint8)
        return np.ascontiguousarray(image), np.ascontiguousarray(mask)

    def __getitem__(self, idx: int):
        path = self.images[idx]
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        mask = cv2.imread(str(self.mask_dir / path.name), cv2.IMREAD_GRAYSCALE)
        if self.rng.random() < self.crop_prob:
            image, mask = self._random_crop(image, mask)
        if self.augment:
            image, mask = self._augment(image, mask)
        x = to_tensor(image, self.size)
        m = cv2.resize(mask, (self.size, self.size), interpolation=cv2.INTER_NEAREST)
        y = torch.from_numpy((m > 127).astype(np.float32))[None]
        return x, y

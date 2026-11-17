"""Pipeline en cascade : YOLO localise les lésions, U-Net les segmente.

    image ──► YOLO ──► boîtes (+ marge) ──► recadrage ──► U-Net ──► masque local
                                                                       │
    masque final ◄──── recollage dans l'image d'origine (max) ◄────────┘

Avantages par rapport à une U-Net appliquée à l'image entière :
* la U-Net travaille à plus haute résolution sur la lésion (petits polypes) ;
* les faux positifs de segmentation loin de toute détection sont supprimés ;
* on obtient en plus une sortie « objet » (nombre de lésions, score de confiance).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
import torch

from .dataset import expand_box, to_tensor
from .unet import UNet


@dataclass
class Detection:
    box: tuple[int, int, int, int]
    score: float
    area_px: int = 0


@dataclass
class Result:
    mask: np.ndarray  # uint8 0/255, taille de l'image d'origine
    detections: list[Detection] = field(default_factory=list)


def load_unet(weights: str | Path, device: str = "cpu") -> tuple[UNet, int]:
    ckpt = torch.load(weights, map_location=device, weights_only=False)
    cfg = ckpt.get("config", {})
    model = UNet(in_channels=3, num_classes=1, base=cfg.get("base", 32)).to(device)
    model.load_state_dict(ckpt["model"])
    model.eval()
    return model, cfg.get("size", 256)


@torch.no_grad()
def unet_predict(model: UNet, image_bgr: np.ndarray, size: int, device: str = "cpu", threshold: float = 0.5) -> np.ndarray:
    """Segmente une image (ou un recadrage) et renvoie une carte de probabilité à sa taille d'origine."""
    h, w = image_bgr.shape[:2]
    x = to_tensor(image_bgr, size)[None].to(device)
    prob = torch.sigmoid(model(x))[0, 0].cpu().numpy()
    return cv2.resize(prob, (w, h), interpolation=cv2.INTER_LINEAR)


class CascadePipeline:
    def __init__(
        self,
        yolo_weights: str | Path,
        unet_weights: str | Path,
        device: str = "cpu",
        conf: float = 0.25,
        margin: float = 0.2,
        threshold: float = 0.5,
    ):
        from ultralytics import YOLO

        self.detector = YOLO(str(yolo_weights))
        self.unet, self.size = load_unet(unet_weights, device)
        self.device = device
        self.conf = conf
        self.margin = margin
        self.threshold = threshold

    def detect(self, image_bgr: np.ndarray) -> list[Detection]:
        res = self.detector.predict(image_bgr, conf=self.conf, device=self.device, verbose=False)[0]
        dets = []
        for xyxy, score in zip(res.boxes.xyxy.cpu().numpy(), res.boxes.conf.cpu().numpy()):
            dets.append(Detection(tuple(int(v) for v in xyxy), float(score)))
        return dets

    def __call__(self, image_bgr: np.ndarray) -> Result:
        h, w = image_bgr.shape[:2]
        prob = np.zeros((h, w), np.float32)
        dets = self.detect(image_bgr)
        for det in dets:
            x1, y1, x2, y2 = expand_box(det.box, w, h, self.margin)
            if x2 - x1 < 4 or y2 - y1 < 4:
                continue
            local = unet_predict(self.unet, image_bgr[y1:y2, x1:x2], self.size, self.device)
            prob[y1:y2, x1:x2] = np.maximum(prob[y1:y2, x1:x2], local)
        mask = np.where(prob > self.threshold, 255, 0).astype(np.uint8)
        for det in dets:
            x1, y1, x2, y2 = det.box
            det.area_px = int((mask[y1:y2, x1:x2] > 0).sum())
        return Result(mask=mask, detections=dets)

    def segment_full(self, image_bgr: np.ndarray) -> np.ndarray:
        """Référence : U-Net seule sur l'image entière."""
        prob = unet_predict(self.unet, image_bgr, self.size, self.device)
        return np.where(prob > self.threshold, 255, 0).astype(np.uint8)


def overlay(image_bgr: np.ndarray, mask: np.ndarray, detections=(), gt_mask: np.ndarray | None = None) -> np.ndarray:
    """Superpose masque prédit (vert), contour vérité terrain (jaune) et boîtes YOLO (rouge)."""
    out = image_bgr.copy()
    green = np.zeros_like(out)
    green[..., 1] = 255
    m = mask > 0
    out[m] = cv2.addWeighted(out, 0.55, green, 0.45, 0)[m]
    contours, _ = cv2.findContours((mask > 0).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(out, contours, -1, (0, 200, 0), 2)
    if gt_mask is not None:
        gt_contours, _ = cv2.findContours((gt_mask > 127).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(out, gt_contours, -1, (0, 230, 255), 2)
    for det in detections:
        x1, y1, x2, y2 = det.box
        cv2.rectangle(out, (x1, y1), (x2, y2), (40, 40, 230), 2)
        label = f"polyp {det.score:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        cv2.rectangle(out, (x1, max(0, y1 - th - 6)), (x1 + tw + 4, y1), (40, 40, 230), -1)
        cv2.putText(out, label, (x1 + 2, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
    return out

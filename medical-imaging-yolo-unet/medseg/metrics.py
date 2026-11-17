"""Fonctions de perte et métriques de segmentation."""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class DiceBCELoss(nn.Module):
    """BCE + (1 - Dice) : la BCE stabilise l'apprentissage, le Dice gère le déséquilibre fond/lésion."""

    def __init__(self, bce_weight: float = 0.5, smooth: float = 1.0):
        super().__init__()
        self.bce_weight = bce_weight
        self.smooth = smooth

    def forward(self, logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        bce = F.binary_cross_entropy_with_logits(logits, target)
        prob = torch.sigmoid(logits)
        dims = (1, 2, 3)
        inter = (prob * target).sum(dims)
        union = prob.sum(dims) + target.sum(dims)
        dice = (2 * inter + self.smooth) / (union + self.smooth)
        return self.bce_weight * bce + (1 - self.bce_weight) * (1 - dice.mean())


def binary_scores(pred: np.ndarray, gt: np.ndarray) -> dict[str, float]:
    """Dice, IoU, précision et rappel (au pixel) entre deux masques binaires.

    Convention : si les deux masques sont vides, la prédiction est parfaite (1.0).
    """
    pred = pred.astype(bool)
    gt = gt.astype(bool)
    tp = np.logical_and(pred, gt).sum()
    fp = np.logical_and(pred, ~gt).sum()
    fn = np.logical_and(~pred, gt).sum()
    if tp + fp + fn == 0:
        return {"dice": 1.0, "iou": 1.0, "precision": 1.0, "recall": 1.0}
    return {
        "dice": float(2 * tp / (2 * tp + fp + fn)),
        "iou": float(tp / (tp + fp + fn)),
        "precision": float(tp / (tp + fp)) if tp + fp else 0.0,
        "recall": float(tp / (tp + fn)) if tp + fn else 1.0,
    }


@torch.no_grad()
def batch_dice(logits: torch.Tensor, target: torch.Tensor, threshold: float = 0.5) -> float:
    pred = (torch.sigmoid(logits) > threshold).float()
    inter = (pred * target).sum((1, 2, 3))
    union = pred.sum((1, 2, 3)) + target.sum((1, 2, 3))
    dice = torch.where(union > 0, 2 * inter / union.clamp(min=1e-6), torch.ones_like(union))
    return float(dice.mean())

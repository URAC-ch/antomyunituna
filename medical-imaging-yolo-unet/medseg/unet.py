"""U-Net (Ronneberger et al., 2015) en PyTorch, avec BatchNorm et taille configurable."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class DoubleConv(nn.Module):
    """(Conv 3x3 -> BN -> ReLU) x 2"""

    def __init__(self, in_ch: int, out_ch: int, dropout: float = 0.0):
        super().__init__()
        layers = [
            nn.Conv2d(in_ch, out_ch, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        ]
        if dropout > 0:
            layers.append(nn.Dropout2d(dropout))
        self.block = nn.Sequential(*layers)

    def forward(self, x):
        return self.block(x)


class Down(nn.Module):
    def __init__(self, in_ch: int, out_ch: int, dropout: float = 0.0):
        super().__init__()
        self.pool = nn.MaxPool2d(2)
        self.conv = DoubleConv(in_ch, out_ch, dropout)

    def forward(self, x):
        return self.conv(self.pool(x))


class Up(nn.Module):
    def __init__(self, in_ch: int, out_ch: int):
        super().__init__()
        self.up = nn.ConvTranspose2d(in_ch, in_ch // 2, kernel_size=2, stride=2)
        self.conv = DoubleConv(in_ch, out_ch)

    def forward(self, x, skip):
        x = self.up(x)
        # Gère les tailles non divisibles par 2^profondeur
        dy, dx = skip.shape[2] - x.shape[2], skip.shape[3] - x.shape[3]
        if dy or dx:
            x = F.pad(x, [dx // 2, dx - dx // 2, dy // 2, dy - dy // 2])
        return self.conv(torch.cat([skip, x], dim=1))


class UNet(nn.Module):
    """U-Net classique : encodeur 4 niveaux, goulot, décodeur avec skip-connections.

    Args:
        in_channels: 3 pour RGB (endoscopie), 1 pour IRM/scanner en niveaux de gris.
        num_classes: 1 pour une segmentation binaire (sortie = logits).
        base: nombre de filtres du premier niveau (64 dans l'article, 32 suffit ici).
    """

    def __init__(self, in_channels: int = 3, num_classes: int = 1, base: int = 32, dropout: float = 0.1):
        super().__init__()
        c = [base, base * 2, base * 4, base * 8, base * 16]
        self.inc = DoubleConv(in_channels, c[0])
        self.down1 = Down(c[0], c[1])
        self.down2 = Down(c[1], c[2])
        self.down3 = Down(c[2], c[3])
        self.down4 = Down(c[3], c[4], dropout)
        self.up1 = Up(c[4], c[3])
        self.up2 = Up(c[3], c[2])
        self.up3 = Up(c[2], c[1])
        self.up4 = Up(c[1], c[0])
        self.head = nn.Conv2d(c[0], num_classes, kernel_size=1)

    def forward(self, x):
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)
        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        return self.head(x)


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

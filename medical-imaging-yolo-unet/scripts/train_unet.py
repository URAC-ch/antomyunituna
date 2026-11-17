"""Entraîne la U-Net de segmentation (BCE + Dice, AdamW, cosine LR).

Exemple :
    python scripts/train_unet.py --epochs 40 --size 256 --batch 8
"""

import argparse
import csv
import sys
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from medseg.dataset import SegmentationDataset  # noqa: E402
from medseg.metrics import DiceBCELoss, batch_dice  # noqa: E402
from medseg.unet import UNet, count_parameters  # noqa: E402


def run_epoch(model, loader, loss_fn, device, optimizer=None):
    train = optimizer is not None
    model.train(train)
    total_loss, total_dice, n = 0.0, 0.0, 0
    with torch.set_grad_enabled(train):
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            loss = loss_fn(logits, y)
            if train:
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                optimizer.step()
            total_loss += loss.item() * len(x)
            total_dice += batch_dice(logits, y) * len(x)
            n += len(x)
    return total_loss / n, total_dice / n


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", type=Path, default=Path("data/processed"))
    p.add_argument("--epochs", type=int, default=40)
    p.add_argument("--size", type=int, default=256)
    p.add_argument("--batch", type=int, default=8)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--base", type=int, default=32, help="filtres du 1er niveau de la U-Net")
    p.add_argument("--crop-prob", type=float, default=0.5, help="part des recadrages autour des lésions")
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--out", type=Path, default=Path("weights/unet_best.pt"))
    p.add_argument("--log", type=Path, default=Path("runs/unet/history.csv"))
    args = p.parse_args()

    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    torch.manual_seed(0)

    train_ds = SegmentationDataset(args.data, "train", args.size, augment=True, crop_prob=args.crop_prob)
    val_ds = SegmentationDataset(args.data, "val", args.size, augment=False)
    train_dl = DataLoader(train_ds, args.batch, shuffle=True, num_workers=args.workers, drop_last=True)
    val_dl = DataLoader(val_ds, args.batch, shuffle=False, num_workers=args.workers)

    model = UNet(in_channels=3, num_classes=1, base=args.base).to(device)
    print(f"U-Net : {count_parameters(model) / 1e6:.2f} M paramètres — device={device}")
    print(f"train={len(train_ds)}  val={len(val_ds)}")

    loss_fn = DiceBCELoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.log.parent.mkdir(parents=True, exist_ok=True)
    best = -1.0
    with open(args.log, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["epoch", "train_loss", "train_dice", "val_loss", "val_dice", "lr"])
        for epoch in range(1, args.epochs + 1):
            t0 = time.time()
            tr_loss, tr_dice = run_epoch(model, train_dl, loss_fn, device, optimizer)
            va_loss, va_dice = run_epoch(model, val_dl, loss_fn, device)
            lr = optimizer.param_groups[0]["lr"]
            scheduler.step()
            writer.writerow([epoch, f"{tr_loss:.4f}", f"{tr_dice:.4f}", f"{va_loss:.4f}", f"{va_dice:.4f}", f"{lr:.6f}"])
            f.flush()
            flag = ""
            if va_dice > best:
                best = va_dice
                torch.save({"model": model.state_dict(), "config": {"base": args.base, "size": args.size},
                            "epoch": epoch, "val_dice": va_dice}, args.out)
                flag = "  ✓ meilleur"
            print(f"[{epoch:3d}/{args.epochs}] loss {tr_loss:.4f}/{va_loss:.4f}  "
                  f"dice {tr_dice:.4f}/{va_dice:.4f}  ({time.time() - t0:.0f}s){flag}")
    print(f"\nMeilleur Dice validation : {best:.4f} — poids : {args.out}")


if __name__ == "__main__":
    main()

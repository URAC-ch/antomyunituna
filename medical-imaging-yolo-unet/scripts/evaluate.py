"""Évalue sur le jeu de test : détection (YOLO), segmentation U-Net seule, et cascade YOLO → U-Net.

Produit :
    results/metrics.json      toutes les métriques
    results/metrics.md        tableau prêt à coller dans le README
    results/examples.png      grille de visualisations (image | vérité | U-Net | cascade)
    results/training_curves.png  courbes d'apprentissage U-Net (si l'historique existe)
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from medseg.metrics import binary_scores  # noqa: E402
from medseg.pipeline import CascadePipeline, overlay  # noqa: E402


def mean_scores(rows):
    return {k: float(np.mean([r[k] for r in rows])) for k in rows[0]}


def plot_curves(history: Path, out: Path):
    import csv

    import matplotlib.pyplot as plt

    rows = list(csv.DictReader(open(history)))
    if not rows:
        return
    ep = [int(r["epoch"]) for r in rows]
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    ax[0].plot(ep, [float(r["train_loss"]) for r in rows], label="train")
    ax[0].plot(ep, [float(r["val_loss"]) for r in rows], label="val")
    ax[0].set_title("Perte BCE + Dice")
    ax[1].plot(ep, [float(r["train_dice"]) for r in rows], label="train")
    ax[1].plot(ep, [float(r["val_dice"]) for r in rows], label="val")
    ax[1].set_title("Coefficient de Dice")
    for a in ax:
        a.set_xlabel("époque")
        a.grid(alpha=0.3)
        a.legend()
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", type=Path, default=Path("data/processed"))
    p.add_argument("--yolo", type=Path, default=Path("weights/yolo_best.pt"))
    p.add_argument("--unet", type=Path, default=Path("weights/unet_best.pt"))
    p.add_argument("--imgsz", type=int, default=512)
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--margin", type=float, default=0.2)
    p.add_argument("--out", type=Path, default=Path("results"))
    p.add_argument("--n-examples", type=int, default=6)
    p.add_argument("--history", type=Path, default=Path("runs/unet/history.csv"))
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    from ultralytics import YOLO

    # 1) Détection
    det = YOLO(str(args.yolo)).val(data=str((args.data / "data.yaml").resolve()), split="test",
                                   imgsz=args.imgsz, conf=0.001, verbose=False, plots=False)
    detection = {"mAP50": float(det.box.map50), "mAP50-95": float(det.box.map),
                 "precision": float(det.box.mp), "recall": float(det.box.mr)}

    # 2) Segmentation : U-Net seule vs cascade
    pipe = CascadePipeline(args.yolo, args.unet, conf=args.conf, margin=args.margin)
    images = sorted((args.data / "images" / "test").glob("*.png"))
    full_rows, cascade_rows, examples = [], [], []
    for i, path in enumerate(images):
        image = cv2.imread(str(path))
        gt = cv2.imread(str(args.data / "masks" / "test" / path.name), cv2.IMREAD_GRAYSCALE) > 127
        full = pipe.segment_full(image)
        res = pipe(image)
        full_rows.append(binary_scores(full > 0, gt))
        cascade_rows.append(binary_scores(res.mask > 0, gt))
        if i < args.n_examples:
            examples.append((image, gt, full, res))

    seg_full, seg_cascade = mean_scores(full_rows), mean_scores(cascade_rows)
    metrics = {"n_test": len(images), "detection": detection,
               "segmentation_unet_full": seg_full, "segmentation_cascade": seg_cascade}
    (args.out / "metrics.json").write_text(json.dumps(metrics, indent=2))

    md = [
        "| Détection (YOLO) | mAP@50 | mAP@50-95 | Précision | Rappel |",
        "|---|---|---|---|---|",
        f"| boîtes de polypes | {detection['mAP50']:.3f} | {detection['mAP50-95']:.3f} | "
        f"{detection['precision']:.3f} | {detection['recall']:.3f} |",
        "",
        "| Segmentation | Dice | IoU | Précision | Rappel |",
        "|---|---|---|---|---|",
    ]
    for label, s in (("U-Net seule (image entière)", seg_full), ("Cascade YOLO → U-Net", seg_cascade)):
        md.append(f"| {label} | {s['dice']:.3f} | {s['iou']:.3f} | {s['precision']:.3f} | {s['recall']:.3f} |")
    (args.out / "metrics.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))

    # 3) Visualisations
    if examples:
        tiles = []
        for image, gt, full, res in examples:
            h = 256
            def fit(im):
                return cv2.resize(im, (int(im.shape[1] * h / im.shape[0]), h))
            gt_vis = overlay(image, (gt * 255).astype(np.uint8))
            row = [fit(image), fit(gt_vis), fit(overlay(image, full, gt_mask=gt * 255)),
                   fit(overlay(image, res.mask, res.detections, gt_mask=gt * 255))]
            tiles.append(np.hstack(row))
        width = max(t.shape[1] for t in tiles)
        tiles = [cv2.copyMakeBorder(t, 0, 4, 0, width - t.shape[1], cv2.BORDER_CONSTANT, value=(255, 255, 255)) for t in tiles]
        header = np.full((34, width, 3), 255, np.uint8)
        col_w = tiles[0].shape[1] // 4
        for j, title in enumerate(["Image", "Verite terrain", "U-Net seule", "Cascade YOLO -> U-Net"]):
            cv2.putText(header, title, (j * col_w + 8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30, 30, 30), 1, cv2.LINE_AA)
        cv2.imwrite(str(args.out / "examples.png"), np.vstack([header, *tiles]))

    if args.history.exists():
        plot_curves(args.history, args.out / "training_curves.png")
    print(f"\nRésultats écrits dans {args.out}/")


if __name__ == "__main__":
    main()

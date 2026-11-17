"""Entraîne un détecteur YOLO (Ultralytics) sur les boîtes de lésions.

Exemples :
    python scripts/train_yolo.py --model yolov8n.pt --epochs 50            # GPU / Colab
    python scripts/train_yolo.py --model yolov8n.yaml --epochs 15 --imgsz 320  # CPU, sans poids pré-entraînés
"""

import argparse
import shutil
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default="data/processed/data.yaml")
    p.add_argument("--model", default="yolov8n.pt", help="poids pré-entraînés (.pt) ou architecture (.yaml)")
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--imgsz", type=int, default=512)
    p.add_argument("--batch", type=int, default=16)
    p.add_argument("--device", default=None, help="'0' pour le GPU, 'cpu' sinon (auto par défaut)")
    p.add_argument("--project", default="runs/yolo")
    p.add_argument("--name", default="polyp")
    p.add_argument("--out", type=Path, default=Path("weights/yolo_best.pt"))
    args = p.parse_args()

    from ultralytics import YOLO

    model = YOLO(args.model)
    model.train(
        data=str(Path(args.data).resolve()),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=str(Path(args.project).resolve()),
        name=args.name,
        exist_ok=True,
        patience=20,
        # augmentations adaptées à l'endoscopie (pas d'orientation privilégiée)
        flipud=0.5,
        fliplr=0.5,
        degrees=15,
        mosaic=1.0,
        plots=True,
    )
    best = Path(model.trainer.best)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(best, args.out)

    metrics = YOLO(str(args.out)).val(data=str(Path(args.data).resolve()), split="test", imgsz=args.imgsz, verbose=False)
    print(f"\nPoids : {args.out}")
    print(f"Test  : mAP50={metrics.box.map50:.3f}  mAP50-95={metrics.box.map:.3f}  "
          f"P={metrics.box.mp:.3f}  R={metrics.box.mr:.3f}")


if __name__ == "__main__":
    main()

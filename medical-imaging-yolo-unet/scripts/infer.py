"""Inférence sur une ou plusieurs images avec la cascade YOLO → U-Net.

Exemple :
    python scripts/infer.py path/to/image.jpg --out results/predictions
"""

import argparse
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from medseg.pipeline import CascadePipeline, overlay  # noqa: E402


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("images", nargs="+", type=Path)
    p.add_argument("--yolo", type=Path, default=Path("weights/yolo_best.pt"))
    p.add_argument("--unet", type=Path, default=Path("weights/unet_best.pt"))
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--out", type=Path, default=Path("results/predictions"))
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    pipe = CascadePipeline(args.yolo, args.unet, conf=args.conf)
    for path in args.images:
        image = cv2.imread(str(path))
        if image is None:
            print(f"Ignoré (illisible) : {path}")
            continue
        res = pipe(image)
        cv2.imwrite(str(args.out / f"{path.stem}_overlay.png"), overlay(image, res.mask, res.detections))
        cv2.imwrite(str(args.out / f"{path.stem}_mask.png"), res.mask)
        total = (res.mask > 0).mean() * 100
        print(f"{path.name}: {len(res.detections)} lésion(s), surface segmentée {total:.1f} %")
        for d in res.detections:
            print(f"   boîte={d.box}  conf={d.score:.2f}  pixels={d.area_px}")


if __name__ == "__main__":
    main()

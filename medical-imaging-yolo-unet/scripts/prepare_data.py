"""Prépare le jeu de données (Kvasir-SEG ou synthétique) au format YOLO + masques.

Exemples :
    python scripts/prepare_data.py --source kvasir
    python scripts/prepare_data.py --source synthetic --n 600
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from medseg.data import prepare_kvasir, prepare_synthetic  # noqa: E402


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--source", choices=["kvasir", "synthetic"], default="kvasir")
    p.add_argument("--out", type=Path, default=Path("data/processed"))
    p.add_argument("--raw", type=Path, default=Path("data/raw"), help="dossier de téléchargement (kvasir)")
    p.add_argument("--n", type=int, default=600, help="nombre d'images (synthetic)")
    p.add_argument("--size", type=int, default=320, help="taille des images (synthetic)")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    print(f"Préparation de « {args.source} » vers {args.out}")
    if args.source == "kvasir":
        yaml_path = prepare_kvasir(args.out, args.raw, seed=args.seed)
    else:
        yaml_path = prepare_synthetic(args.out, n=args.n, size=args.size, seed=args.seed)
    print(f"OK — configuration YOLO : {yaml_path}")


if __name__ == "__main__":
    main()

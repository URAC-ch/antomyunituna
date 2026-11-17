"""Démo interactive (Gradio) : déposez une image d'endoscopie, obtenez détections + segmentation.

    pip install gradio
    python app.py            # puis ouvrir http://127.0.0.1:7860
"""

from pathlib import Path

import cv2
import gradio as gr
import numpy as np

from medseg.pipeline import CascadePipeline, overlay

ROOT = Path(__file__).parent
pipe = CascadePipeline(ROOT / "weights/yolo_best.pt", ROOT / "weights/unet_best.pt")


def predict(image_rgb: np.ndarray, conf: float, margin: float):
    if image_rgb is None:
        return None, None, "Aucune image."
    pipe.conf, pipe.margin = conf, margin
    bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    res = pipe(bgr)
    vis = cv2.cvtColor(overlay(bgr, res.mask, res.detections), cv2.COLOR_BGR2RGB)
    lines = [f"**{len(res.detections)} lésion(s) détectée(s)** — surface segmentée : {(res.mask > 0).mean() * 100:.1f} %"]
    for i, d in enumerate(res.detections, 1):
        lines.append(f"- Lésion {i} : confiance {d.score:.2f}, {d.area_px} px")
    return vis, res.mask, "\n".join(lines)


examples = sorted(str(p) for p in (ROOT / "data/processed/images/test").glob("*.png"))[:4]

demo = gr.Interface(
    fn=predict,
    inputs=[
        gr.Image(type="numpy", label="Image d'endoscopie"),
        gr.Slider(0.05, 0.9, value=0.25, step=0.05, label="Seuil de confiance YOLO"),
        gr.Slider(0.0, 0.6, value=0.2, step=0.05, label="Marge autour des boîtes"),
    ],
    outputs=[gr.Image(label="Détection + segmentation"), gr.Image(label="Masque"), gr.Markdown()],
    examples=[[e, 0.25, 0.2] for e in examples] or None,
    title="Détection & segmentation de polypes — YOLO + U-Net",
    description="Projet pédagogique, non destiné à un usage clinique.",
)

if __name__ == "__main__":
    demo.launch()

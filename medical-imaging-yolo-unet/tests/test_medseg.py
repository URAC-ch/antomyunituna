import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from medseg.data import boxes_to_yolo, mask_to_boxes, prepare_synthetic, synth_endoscopy  # noqa: E402
from medseg.dataset import SegmentationDataset, expand_box  # noqa: E402
from medseg.metrics import DiceBCELoss, binary_scores  # noqa: E402
from medseg.unet import UNet  # noqa: E402


def test_unet_output_shape_odd_size():
    model = UNet(base=8)
    out = model(torch.randn(2, 3, 100, 132))
    assert out.shape == (2, 1, 100, 132)


def test_mask_to_boxes_and_yolo_format():
    mask = np.zeros((100, 200), np.uint8)
    mask[10:30, 20:60] = 255
    mask[50:90, 150:190] = 255
    boxes = sorted(mask_to_boxes(mask))
    assert boxes == [(20, 10, 60, 30), (150, 50, 190, 90)]
    line = boxes_to_yolo([boxes[0]], 200, 100).split()
    assert line[0] == "0"
    assert np.allclose([float(v) for v in line[1:]], [0.2, 0.2, 0.2, 0.2])


def test_expand_box_clips_to_image():
    assert expand_box((0, 0, 10, 10), 12, 12, 0.5) == (0, 0, 12, 12)


def test_binary_scores():
    a = np.zeros((10, 10), bool)
    b = np.zeros((10, 10), bool)
    assert binary_scores(a, b)["dice"] == 1.0
    a[:5] = True
    b[:5] = True
    assert binary_scores(a, b)["iou"] == 1.0
    b[:] = False
    b[5:] = True
    assert binary_scores(a, b)["dice"] == 0.0


def test_loss_decreases_for_perfect_prediction():
    target = torch.zeros(1, 1, 8, 8)
    target[..., 2:6, 2:6] = 1
    loss = DiceBCELoss()
    good = loss((target * 2 - 1) * 10, target)
    bad = loss(-(target * 2 - 1) * 10, target)
    assert good < 0.05 < bad


def test_synthetic_pipeline(tmp_path):
    img, mask = synth_endoscopy(np.random.default_rng(0), 128)
    assert img.shape == (128, 128, 3) and mask.shape == (128, 128)
    prepare_synthetic(tmp_path, n=10, size=96)
    assert (tmp_path / "data.yaml").exists()
    ds = SegmentationDataset(tmp_path, "train", size=64, augment=True, crop_prob=1.0)
    x, y = ds[0]
    assert x.shape == (3, 64, 64) and y.shape == (1, 64, 64)

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.feature_extractor import load_satlas_backbone
from src.transformation import transform_image_to_ndarray, transform_for_inference
import torch
import glob

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MODEL_ID = os.getenv("MODEL_ID", "Sentinel2_SwinB_SI_RGB")
CHECKPOINT_PATH = os.getenv("CHECKPOINT", "")

print(f"Using device: {DEVICE}")
print(f"Model ID: {MODEL_ID}")
print(f"Checkpoint: {CHECKPOINT_PATH if CHECKPOINT_PATH else 'None'}")

model = load_satlas_backbone(MODEL_ID, CHECKPOINT_PATH)
model.eval()

data_root = "/workspace/training_inference/data/test"
image_pattern = os.path.join(data_root, "*.jpg")  # adapt pattern as needed


for path in glob.glob(image_pattern):
    print(f"Inferencing: {path}")
    x = transform_image_to_ndarray(path)
    x = transform_for_inference(x)

    with torch.no_grad():
        features = model(x)

    shapes = [list(f.shape) for f in features]
    print("Feature shapes:", shapes)

print("Inference complete.")

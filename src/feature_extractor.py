import torch
import numpy as np
import satlaspretrain_models
from typing import Dict, Any

from .transformation import transform_for_inference, tile_image
# Assume you implement sar_loader.py to load your actual SAR data - pasul 1

"""Configuration"""
# ID-ul modelului pe care il folosim de la satlaspretrain (Sentinel1, Swin-v2-Base, Single-Image Input)
S1_MODEL_ID = "Sentinel1_SwinB_SI"
CHECKPOINT_PATH = "src/model/marine_placeholder_weights.pth"  # momentan aici am pus weights-urile pt antrenarea modelului de marine pana le facem pe ale noastre

weights_manager = satlaspretrain_models.Weights()

"""Incarcare Model"""


def load_satlas_backbone(model_id: str, checkpoint_path: str | None = None):
    """Model Sentinel-1 pretrained"""
    try:
        model = weights_manager.get_pretrained_model(
            model_identifier=model_id,
            fpn=True,
        )
        # state = torch.load(checkpoint_path)
        # if "model_state_dict" in state:
        #     state = state["model_state_dict"]
        # print(state.keys())
        # missing, unexpected = model.load_state_dict(state, strict=False)
        # print("Loaded checkpoint.")
        # print("Missing keys:", missing)
        # print("Unexpected keys:", unexpected)
        # model.eval()
        return model
    except Exception as e:
        print(
            f"ERROR: Failed to load Satlas model. Ensure .pth file is at {checkpoint_path}"
        )
        print(f"Details: {e}")
        return None


"""Extragere Features + Transformare pt inferare"""


def integrate_and_infer(
    raw_sar_data: np.ndarray,
) -> Dict[
    tuple, np.ndarray
]:  # raw_sar_data este un numpy array care contine datele "raw ale imaginii" -> asta s-ar obtine cu din partea lui Ionut+Dana (alt fisier .py in mod normal)
    model = load_satlas_s1_backbone(CHECKPOINT_PATH)
    if model is None:
        return {}

    all_features = {}  # retinem caracteristici

    # parcurgere toate "bucatile" de 256x256 din imaginea noastra mare
    for patch, coords in tile_image(raw_sar_data):
        # 1. transformare in formatul necesar
        input_tensor = transform_for_inference(patch)

        # 2. Inferenta
        with torch.no_grad():
            # oferim inputul modelului si obtinem vectorul de caracteristici
            features = model(input_tensor)

        # 3. Stocam trasaturile pentru coordonatele respective (zona) intr-un array NumPy unidimensional
        all_features[coords] = features.cpu().numpy().flatten()

    print(f"Inference complete. Extracted {len(all_features)} feature vectors.")
    return all_features

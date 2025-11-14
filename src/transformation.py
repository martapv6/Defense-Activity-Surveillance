# src/pipelines/transformation.py
import torch
import numpy as np

TARGET_PATCH_SIZE = 256

def transform_for_inference(sar_patch: np.ndarray) -> torch.Tensor:
    """
    Aplicare Satlas S-1 Normalization (vezi Normalization.md din repo-ul lor) 
    + convertire patch in PyTorch tensor format (1, C, H, W).
    """
    # 1. Convertire in PyTorch tensor (must be float idk)
    tensor = torch.from_numpy(sar_patch).float() 
    
    # 2. Normalizarea Satlas Sentinel-1: Divide by 255 and clip to 0-1
    tensor = tensor / 255.0
    tensor = torch.clip(tensor, 0.0, 1.0)
    
    # 3. (H, W, C) -> (C, H, W)
    tensor = tensor.permute(2, 0, 1)

    # 4. (C, H, W) -> (1, C, H, W); B=batch=1
    tensor_batch = tensor.unsqueeze(0) #nume amuzant functie lmao 

    return tensor_batch

def tile_image(image_data: np.ndarray, patch_size: int = TARGET_PATCH_SIZE):
    #image_data este imaginea mare (cea de interes selectata), patch_size este dimensiunea fixata (256x256) in care impartim imaginea mare, ulterior pasandu-le modelului
    H, W, C = image_data.shape #height, width, channels; din ce am inteles C=2 pt ca sunt canale: VV (vertical-vertical) si VH (vertical-horizontal). nu ne batem capul lasam asa cum e
    for y in range(0, H, patch_size): #x si y cresc din 256 in 256
        for x in range(0, W, patch_size):
            if y + patch_size <= H and x + patch_size <= W: #ne asiguram ca nu depasim la final dimensiunile imaginii mari
                patch = image_data[y:y + patch_size, x:x + patch_size, :] #salvare bucata de dimensiune patch_size (256x256x2)
                yield patch, (y, x) #yield pentru ca fct asta e apelata in feature_extractor de mai multe ori. Generam fiecare patch la request
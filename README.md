# 🛰️ Defense-Activity-Surveillance: GEOINT Feature Extraction Pipeline

This repository contains the foundational code for a robust pipeline designed for **defense-oriented activity monitoring** and **anomaly detection** using satellite radar data.

* **Goal:** Convert raw Sentinel-1 SAR imagery into dense numerical feature vectors (embeddings) using the pre-trained Satlas Foundation Model for later analysis by an anomaly classifier.
* **Key Advantage:** Uses Sentinel-1 (SAR) for all-weather, day/night monitoring.

---

## 1. ⚙️ Prerequisites and Setup

This project requires Python 3.9+ and uses a dedicated virtual environment for deep learning dependencies (PyTorch).

### A. Initial Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/martapv6/Defense-Activity-Surveillance.git
    cd Defense-Activity-Surveillance
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate   # Linux/macOS
    .\venv\Scripts\activate     # Windows PowerShell
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### B. Model Acquisition (CRITICAL STEP)

The trained model weights are too large to store on GitHub, so they must be downloaded externally.

1.  **Download Model Weights:** Obtain the **1.5 GB Satlas Foundation Model weights file** (the "models only" download).
2.  **Create Local Directory:** Create the secure folder structure for the model weights:
    ```bash
    mkdir -p src/models/
    ```
3.  **Place File:** For now we place the downloaded `.pth` file related to marines into this folder and ensure it is named as such:
    * **Destination Path:** `src/model/marine_placeholder_weights.pth`
    * *Note: This file is ignored by `.gitignore` and must **not** be committed.*

---

## 2. 🧠 Pipeline Overview

The pipeline is based on **Transfer Learning** using the **Sentinel1\_SwinB\_SI** model.

| Module | Purpose | Key Action |
| :--- | :--- | :--- |
| **`sar_loader.py`** | **Data Acquisition** | Fetches Sentinel-1 GRD imagery (VV/VH bands) from the STAC catalog for a defined bounding box and date range. |
| **`transformation.py`** | **Preprocessing** | Applies the required **Satlas Normalization** (divides pixels by 255 and clips to 0-1) and tiles the image into $256 \times 256$ PyTorch tensors. |
| **`feature_extractor.py`** | **Inference Core** | Loads the downloaded model and runs every tile through the Swin Transformer backbone to extract a high-dimensional feature vector. |

### Execution Command

Run the main pipeline script from the project root. This script orchestrates the loading, processing, and feature extraction: (we dont have this yet but we might need it to test our code)

```bach
python src/main_extractor.py

```
3.  Annotated Dataset: MVRSD (Military Vehicle Remote Sensing Dataset)

This project also integrates a pre-annotated optical remote–sensing dataset to validate the pipeline on real object-detection data.

### 3.1 Dataset Description

We use the **MVRSD – Military Vehicle Remote Sensing Dataset**, derived from Google Earth imagery.  
Key characteristics:

- **Images:** 3,000 RGB satellite images
- **Resolution:** 0.3 m per pixel
- **Image size:** 640 × 640 px
- **Annotations:** 32,626 labeled vehicle instances

The dataset contains five fine-grained vehicle classes:

1. **SMV** – Small Military Vehicles  
2. **LMV** – Large Military Vehicles  
3. **AFV** – Armored Fighting Vehicles  
4. **MCV** – Military Construction Vehicles  
5. **CV** – Civilian Vehicles  

### 3.2 Original Annotation Format

In the original MVRSD release, objects are annotated with **axis-aligned (horizontal) bounding boxes**.  
Each labeled instance is defined by pixel-based coordinates:

- `x_min`, `y_min` – top-left corner  
- `x_max`, `y_max` – bottom-right corner  
- `class_id` – one of the 5 classes above  

Coordinates are expressed in pixels with respect to the 640×640 image grid.

Conceptually, an annotation record has the structure:

```text
image_name, x_min, y_min, x_max, y_max, class_id
```
3.3 Conversion to Model Input Format
To train detection models, we convert the original pixel-based bounding boxes into the YOLO format.  
Each image receives one .txt file containing all normalized bounding boxes in the form:

class_id x_center y_center width height

Normalization is performed with respect to the image width and height (640x640):

- x_center = (x_min + x_max) / 2 / 640  
- y_center = (y_min + y_max) / 2 / 640  
- width    = (x_max - x_min) / 640  
- height   = (y_max - y_min) / 640  

After conversion, the MVRSD dataset has the same structure as the standard YOLO training datasets and can be used directly for fine-tuning or evaluation.


3.4 Example Transformation Code
The conversion is implemented in:

src/MVRSD_dataset/transformation.py

Below is a minimal example that performs the conversion from the original XML annotation file to YOLO .txt label files:

```python
from pathlib import Path
from MVRSD_dataset.transformation import convert_mvrsd_csv_to_yolo

DATASET_ROOT = Path("src/MVRSD_dataset/data")

convert_mvrsd_csv_to_yolo(
    csv_path=DATASET_ROOT / "annotations_mvrsd.csv",
    labels_out_dir=DATASET_ROOT / "labels",
)




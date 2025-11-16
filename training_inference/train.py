import os
import sys
import xml.etree.ElementTree as ET

import torch
import torch.utils.data as data
from torch.utils.data import DataLoader
import torch.optim as optim

from torchvision.models.detection import FasterRCNN
from torchvision.ops import MultiScaleRoIAlign

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.feature_extractor import load_satlas_backbone
from src.transformation import transform_image_to_ndarray, transform_for_inference

import mlflow
from tqdm import tqdm
from torch.cuda.amp import autocast, GradScaler

CLASSES = ["SMV", "LMV", "AFV", "MCV", "CV"]
NAME_TO_ID = {name: i + 1 for i, name in enumerate(CLASSES)}

EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "satlas_experiments")

print(f"MLFLOW_TRACKING_URI: {os.getenv('MLFLOW_TRACKING_URI', '(not set)')}")
print(f"MLFLOW_EXPERIMENT_NAME: {EXPERIMENT_NAME}")

if EXPERIMENT_NAME:
    mlflow.set_experiment(EXPERIMENT_NAME)


class AerialDataset(data.Dataset):
    def __init__(self, root, img_dir="images", ann_dir="annotations", transforms=None):
        self.root = root
        self.img_dir = os.path.join(root, img_dir)
        self.ann_dir = os.path.join(root, ann_dir)
        self.ids = [
            os.path.splitext(f)[0]
            for f in os.listdir(self.img_dir)
            if f.endswith(".jpg")
        ]
        self.transforms = transforms

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, idx):
        img_id = self.ids[idx]
        img_path = os.path.join(self.img_dir, img_id + ".jpg")
        ann_path = os.path.join(self.ann_dir, img_id + ".xml")

        img = transform_image_to_ndarray(img_path)
        img = transform_for_inference(img)

        boxes = []
        labels = []

        tree = ET.parse(ann_path)
        root = tree.getroot()
        for obj in root.findall("object"):
            name = obj.find("name").text
            if name not in NAME_TO_ID:
                continue
            label = NAME_TO_ID[name]

            bnd = obj.find("bndbox")
            xmin = float(bnd.find("xmin").text)
            ymin = float(bnd.find("ymin").text)
            xmax = float(bnd.find("xmax").text)
            ymax = float(bnd.find("ymax").text)

            boxes.append([xmin, ymin, xmax, ymax])
            labels.append(label)

        if len(boxes) == 0:
            boxes = torch.zeros((0, 4), dtype=torch.float32)
            labels = torch.zeros((0,), dtype=torch.int64)
        else:
            boxes = torch.tensor(boxes, dtype=torch.float32)
            labels = torch.tensor(labels, dtype=torch.int64)

        target = {
            "boxes": boxes,
            "labels": labels,
            "image_id": torch.tensor([idx]),
        }

        return img, target


class SatlasBackboneWrapper(torch.nn.Module):
    def __init__(self, satlas_model, out_channels=256):
        super().__init__()
        self.backbone = satlas_model
        self.out_channels = out_channels

    def forward(self, x):
        feats = self.backbone(x)
        if isinstance(feats, (list, tuple)):
            return {str(i): f for i, f in enumerate(feats)}
        return {"0": feats}


def collate_fn(batch):
    images, targets = list(zip(*batch))
    return list(images), list(targets)


train_dataset = AerialDataset(
    root="/workspace/training_inference/data/MVRSD/",
    img_dir="images/train",
    ann_dir="labels/train/xml",
)

val_dataset = AerialDataset(
    root="/workspace/training_inference/data/MVRSD/",
    img_dir="images/val",
    ann_dir="labels/val/xml",
)

train_loader = DataLoader(
    train_dataset,
    batch_size=1,
    shuffle=False,
    num_workers=4,
    collate_fn=collate_fn,
)

val_loader = DataLoader(
    val_dataset,
    batch_size=1,
    shuffle=False,
    num_workers=4,
    collate_fn=collate_fn,
)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MODEL_ID = os.getenv("MODEL_ID", "Sentinel2_SwinB_SI_RGB")
CHECKPOINT_PATH = os.getenv("CHECKPOINT", "")

print(f"Using device: {DEVICE}")
print(f"Model ID: {MODEL_ID}")
print(f"Checkpoint: {CHECKPOINT_PATH if CHECKPOINT_PATH else 'None'}")

satlas_model = load_satlas_backbone(MODEL_ID, CHECKPOINT_PATH)
satlas_model.to(DEVICE)
backbone = SatlasBackboneWrapper(satlas_model, out_channels=128)
backbone = torch.compile(backbone, mode="max-autotune")
print(
    f"Backbone number of parameters {sum([p.numel() for p in backbone.parameters()])}"
)
num_classes = len(CLASSES) + 1
print("Freezing Satlas backbone...")
for name, p in backbone.named_parameters():
    p.requires_grad = False
model = FasterRCNN(
    backbone=backbone,
    num_classes=num_classes,
    box_roi_pool=MultiScaleRoIAlign(
        featmap_names=["0", "1", "2", "3"],  # keys produced in wrapper
        output_size=7,
        sampling_ratio=2,
    ),
).to(DEVICE)

params = [p for p in model.parameters() if p.requires_grad]

optimizer = optim.AdamW(params, lr=0.0001)

# lr_scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)

num_epochs = 20
model.train()
print(
    f"Number of trainable parameters {sum([p.numel() for p in model.parameters() if p.requires_grad])}"
)

scaler = GradScaler()

with mlflow.start_run():
    # mlflow.log_param("model_id", MODEL_ID)
    # mlflow.log_param("lr", 1e-4)
    # mlflow.log_param("epochs", num_epochs)
    # mlflow.log_param("device", DEVICE)

    for epoch in range(num_epochs):
        running_loss = 0.0

        for images, targets in tqdm(train_loader):
            images = [img.squeeze(0).to(DEVICE) for img in images]

            targets = [{k: v.to(DEVICE) for k, v in t.items()} for t in targets]
            optimizer.zero_grad()

            with autocast(dtype=torch.float16, enabled=(DEVICE == "cuda")):
                loss_dict = model(images, targets)  # Faster R-CNN
                loss = sum(loss for loss in loss_dict.values())

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            running_loss += loss.item()

        # lr_scheduler.step()
        avg_loss = running_loss / max(1, len(train_loader))
        print(f"Epoch {epoch + 1}/{num_epochs}, train loss: {avg_loss:.4f}")
        mlflow.log_metric("train_loss", avg_train_loss, step=epoch)

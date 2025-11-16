# src/MVSRD_dataset/transformation.py
"""
functii pentru conversia adnotarilor originale din mvrsd
din format xml (pascal voc) in format yolo

cod pentru a lua o imagine din satelit si a o aduce
in formatul respectiv (transformarea bounding box-urilor)
"""

import xml.etree.ElementTree as ET
from pathlib import Path

# mapare clase din xml -> id numeric
CLASS_TO_ID = {
    "SMV": 0,
    "LMV": 1,
    "AFV": 2,
    "MCV": 3,
    "CV": 4,
}


def convert_bbox_to_yolo(xmin, ymin, xmax, ymax, img_w, img_h):
    """
    transforma bbox voc (pixeli) in bbox yolo normalizat
    """
    w = xmax - xmin
    h = ymax - ymin
    x_c = xmin + w / 2.0
    y_c = ymin + h / 2.0

    return x_c / img_w, y_c / img_h, w / img_w, h / img_h


def convert_xml_to_yolo(xml_path: Path, labels_out_dir: Path):
    """
    converteste un singur fisier xml voc in fisier txt yolo
    """

    tree = ET.parse(xml_path)
    root = tree.getroot()

    # citim numele imaginii
    filename = root.find("filename").text
    txt_name = filename.replace(".jpg", ".txt").replace(".png", ".txt")

    # citim dimensiunea imaginii din tagul <size>
    size = root.find("size")
    img_w = int(size.find("width").text)
    img_h = int(size.find("height").text)

    yolo_lines = []

    for obj in root.findall("object"):
        class_name = obj.find("name").text

        # ignoram obiectele cu clasa necunoscuta
        if class_name not in CLASS_TO_ID:
            continue

        class_id = CLASS_TO_ID[class_name]

        bbox = obj.find("bndbox")
        xmin = float(bbox.find("xmin").text)
        ymin = float(bbox.find("ymin").text)
        xmax = float(bbox.find("xmax").text)
        ymax = float(bbox.find("ymax").text)

        x_c, y_c, w, h = convert_bbox_to_yolo(xmin, ymin, xmax, ymax, img_w, img_h)
        yolo_lines.append(f"{class_id} {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}")

    labels_out_dir.mkdir(parents=True, exist_ok=True)
    out_path = labels_out_dir / txt_name
    out_path.write_text("\n".join(yolo_lines), encoding="utf-8")


def batch_convert(xml_folder: Path, labels_out_dir: Path):
    """
    converteste toate fisierele xml dintr-un folder in yolo
    """
    xml_folder = Path(xml_folder)
    labels_out_dir = Path(labels_out_dir)
    labels_out_dir.mkdir(parents=True, exist_ok=True)

    for xml_file in xml_folder.glob("*.xml"):
        convert_xml_to_yolo(xml_file, labels_out_dir)

    print(f"[ok] conversie finalizata pentru {xml_folder} -> {labels_out_dir}")


if __name__ == "__main__":
    here = Path(__file__).resolve().parent

    xml_dir = Path(r"D:\sateliti\MVRSD_dataset\data\labels\train\xml")
    labels_out = Path(r"D:\sateliti\MVRSD_dataset\data_transf\labels\train")

    batch_convert(xml_dir, labels_out)

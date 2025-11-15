# maybe SENTINEL HUB for more data in the future

import os
import json
import requests
from pathlib import Path
from datetime import date
from dotenv import load_dotenv

def load_locations(paths):
    for path in paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
    # If none of the paths exist
    raise FileNotFoundError(f"JSON file not found in any of the locations: {paths}")

# incarcare API key din .env
load_dotenv()
API_KEY = os.getenv('SPECTATOR_API_KEY')
if not API_KEY:
    raise ValueError("No SPECTATOR_API_KEY in .env!")

LOCATIONS_PATHS = ["src/locations.json", "locations.json"]
LOCATIONS = load_locations(LOCATIONS_PATHS)

BASE_URL = "https://api.spectator.earth"
DATASET_DIR = Path("dataset")
IMAGES_DIR = DATASET_DIR / "images" # imagini descarcate
FEATURES_DIR = DATASET_DIR / "features" # pentru vectorii generati ??
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
FEATURES_DIR.mkdir(parents=True, exist_ok=True)


def search_images(lat, lon, date_from, date_to, name = '#', type = 'default', max_cloud = 20, bbox_size = 0.01):
    # cautare imag satelit pe Spectator
    # max_cloud = procent max de nori acceptat
    # bbox_size = 0.05 inseamna un patrat de 0.1 grade in jurul locatiei

    print(f"\n Cautare imagini pentru ({lat}, {lon})")
    print(f"   Perioada: {date_from} → {date_to}")
    print(f"   Max cloud: {max_cloud}%")

    bbox = [lon - bbox_size, lat - bbox_size, lon + bbox_size, lat + bbox_size] # bounding box
    bbox =",".join(f"{crd:.2f}" for crd in bbox)

    # Parametri query
    params = {
        "api_key": API_KEY,
        "bbox": bbox,  # convertire lista în string
        "date_from": date_from,
        "date_to": date_to,
        "cc_less_than": max_cloud,
        "satellites": "Sentinel-2A,Sentinel-2B"  # si/sau Sentinel-1 ?
    }

    url = f"{BASE_URL}/imagery/" # request la API

    try:
        response = requests.get(url, params=params)
        # response.raise_for_status()
        
        data = response.json()
        
        file_path = "output.txt"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        images = data.get("results", [])
        
        print(f"Gasite {len(images)} imagini")
        return images
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            print("Eroare: API key invalid sau lipsa!")
            print("   Verifica fisierul .env")
        else:
            print(f"Eroare HTTP: {e}")
        return []
    except Exception as e:
        print(f"Eroare: {e}")
        return []

# pentru reincarcare dataset ulterior
def save_metadata(images, filename="spectator_metadata.json"):
    with open(filename, 'w') as f:
        json.dump(images, f, indent=2)
        
def download_image(filename, output_dir = IMAGES_DIR):
    os.makedirs(output_dir, exist_ok=True)

    data = None
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    if data == None:
        return
    
    for item in data:
        base_url = item.get("download_url")
        identifier = item.get("identifier")

        if not base_url or not identifier:
            print("Missing download_url, skipping entry.")
            continue

        region_output_dir = os.path.join(output_dir, identifier)
        os.makedirs(region_output_dir, exist_ok=True)

        api_addon = '?api_key={api_key}'.format(api_key=API_KEY)
        base_url_with_api = base_url + api_addon
        
        print(f"\nFetching file list for: {identifier}")

        # 1. get the list of files inside this imagery package
        try:
            file_list_response = requests.get(base_url_with_api)
            file_list_response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch file list: {e}")
            continue

        try:
            files = file_list_response.json()
        except ValueError:
            print("The server did not return valid JSON for file list.")
            continue

        # 2. download each file inside that imagery folder
        for file_info in files:
            file_path = file_info.get("path")
            file_name = file_info.get("name")
            file_url = os.path.join(base_url, file_path) + api_addon

            if not file_path or not file_name:
                continue

            output_path = os.path.join(region_output_dir, file_name)
            print(f"   → Downloading {file_name}")

            try:
                file_data = requests.get(file_url)
                file_data.raise_for_status()
            except requests.RequestException as e:
                print(f"Failed: {e}")
                continue

            # save file to disk
            with open(output_path, "wb") as out:
                out.write(file_data.content)

    print("\nALL DONE")

    pass

def display_results(images):
    if not images:
        print("Fara imagini disponibile")
        return
    
    for i, img in enumerate(images, 1):
        image_id = img.get("id", "N/A")
        date = img.get("date", "N/A")
        satellite = img.get("satellite", "N/A")
        cloud_cover = img.get("cloud_coverage", "N/A")

    # extragere doar data (fara ora)
        if "T" in str(date):
            date = date.split("T")[0]
        
        print(f"{i}. Imagine ID: {image_id}")
        print(f"Data: {date}")
        print(f"Satelit: {satellite}")
        print(f"Cloud Cover: {cloud_cover}%")
        print()


if __name__ == "__main__":
    for loc_name in LOCATIONS:
        loc_data = LOCATIONS[loc_name]
        
        print(loc_data)
        if loc_data:
            images_data = search_images(
                lat=loc_data['lat'],
                lon=loc_data['lon'],
                date_from=loc_data['date_from'],
                date_to=loc_data['date_to'],
                name=loc_data.get('name', '#'),
                type=loc_data.get('type', 'default')
            )
            display_results(images_data)
            save_location_path = "metadata_"+loc_name+".json"
            save_metadata(images_data, save_location_path)
            download_image(save_location_path)



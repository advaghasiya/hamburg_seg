from polygon_image_creator import process_tif_file
from tqdm import tqdm
import os

gml_file_path = 'tools/convert_datasets/use_Feinkartierung_Strasse_HH_2022-03-25/Feinkartierung_Strasse_HH_2022-03-25.gml'

tiff_dirs = [
    'tools/convert_datasets/DOP20_HH-Altona_fruehjahrsbefliegung_2022_rgbi/Hamburg_Altona/',
    'tools/convert_datasets/DOP20_HH-Bergedorf_fruehjahrsbefliegung_2022_rgbi/Hamburg_Bergedorf/',
    'tools/convert_datasets/DOP20_HH-Eimsbuettel_fruehjahrsbefliegung_2022_rgbi/Hamburg_Eimsbuettel/',
    'tools/convert_datasets/DOP20_HH-Hamburg-Nord_fruehjahrsbefliegung_2022_rgbi/Hamburg_Hamburg-Nord/',
    'tools/convert_datasets/DOP20_HH-Harburg_fruehjahrsbefliegung_2022_rgbi/Hamburg_Harburg/',
    'tools/convert_datasets/DOP20_HH-Hamburg-Mitte_fruehjahrsbefliegung_2022_rgbi/Hamburg_Hamburg-Mitte/',
    'tools/convert_datasets/DOP20_HH-Wandsbek_fruehjahrsbefliegung_2022_rgbi/Hamburg_Wandsbek/',
]

total_files_processed = 0
current_file = None

for tiff_dir in tiff_dirs:
    print(f"Current TIFF directory: {tiff_dir}")
    tif_files = [f for f in os.listdir(tiff_dir) if f.endswith('.tif')]
    output_folder_path = tiff_dir.replace('_rgbi', '_gray')

    # Check if the output folder exists
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path, exist_ok=True)
        processed_files = []
    else:
        processed_files = [f.replace('.png', '.tif') for f in os.listdir(output_folder_path) if f.endswith('.png')]

    tif_files_to_process = [f for f in tif_files if f not in processed_files]

    for tif_file in tqdm(tif_files_to_process, desc="Processing TIFF files"):
        tif_file_path = os.path.join(tiff_dir, tif_file)
        output_file_path = os.path.join(output_folder_path, tif_file.replace('.tif', '.png'))
        current_file = tif_file_path
        process_tif_file(gml_file_path, tif_file_path, output_file_path)
        print(f"Processed file: {tif_file_path} -> {output_file_path}")
        total_files_processed += 1

print(f"Total files processed: {total_files_processed}")
if current_file:
    print(f"Currently processing: {current_file}")
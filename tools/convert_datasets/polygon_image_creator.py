import xml.etree.ElementTree as ET
from shapely.geometry import Polygon, Point
from shapely.errors import TopologicalError
from joblib import Parallel, delayed
import geopandas as gpd
import rasterio
from PIL import Image, ImageDraw
import time

def parse_gml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    categories = ["Verkehrsflächen", "befestigte Flächen", "sonstige Flächen", "unbefestigte Flächen"]
    category_polygons = {category: [] for category in categories}

    print("Parsing GML file...")
    for member in root.findall('.//{http://www.opengis.net/gml}featureMember'):
        category_elem = member.find('.//{https://registry.gdi-de.org/id/de.hh.up}kategorie')
        if category_elem is not None and category_elem.text.strip() in categories:
            polygon_elem = member.find('.//{http://www.opengis.net/gml}posList')
            if polygon_elem is not None:
                coords = polygon_elem.text.split()
                coords = [float(coord) for coord in coords]
                coords = [(coords[i], coords[i + 1]) for i in range(0, len(coords), 2)]
                category_polygons[category_elem.text.strip()].append(Polygon(coords))
    
    print("GML parsing completed.")
    return category_polygons

def any_point_in_bbox(polygon, bbox_polygon):
    for point in polygon.exterior.coords:
        if bbox_polygon.contains(Point(point)):
            return True
    return False

def clip_polygon(geom, bbox_polygon):
    try:
        if any_point_in_bbox(geom, bbox_polygon):
            if not geom.is_valid:
                geom = geom.buffer(0)
            clipped_geom = geom.intersection(bbox_polygon)
            if not clipped_geom.is_empty:
                return clipped_geom
    except TopologicalError as e:
        print(f"Error clipping polygon: {e}")
        print(f"Invalid geometry: {geom}")
    return None

def process_tif_file(gml_file_path, tif_file_path, output_file_path):
    print(f"\nProcessing TIFF file: {tif_file_path}")
    category_polygons = parse_gml(gml_file_path)

    with rasterio.open(tif_file_path) as src:
        bounds = src.bounds
        width = src.width
        height = src.height

    print(f"Bounds: {bounds}")
    print(f"Width: {width}, Height: {height}")

    if isinstance(bounds, (list, tuple)) and len(bounds) == 4:
        left, bottom, right, top = bounds
    else:
        print("Error: Unexpected bounds format. Using default values.")
        left, bottom, right, top = 0, 0, width, height

    bbox_polygon = Polygon([(left, bottom), (right, bottom), (right, top), (left, top)])

    print("Clipping polygons...")
    clipped_polygons = {}
    for category, polygons in category_polygons.items():
        clipped_geoms = Parallel(n_jobs=40)(delayed(clip_polygon)(geom, bbox_polygon) for geom in polygons)
        clipped_geoms = [geom for geom in clipped_geoms if geom is not None]
        clipped_polygons[category] = clipped_geoms

    clipped_gdfs = {}
    print("Creating GeoDataFrames...")
    for category, polygons in clipped_polygons.items():
        gdf = gpd.GeoDataFrame(geometry=polygons)
        clipped_gdfs[category] = gdf

    extents = {}
    print("Calculating extents...")
    for category, gdf in clipped_gdfs.items():
        bounds = []
        for geom in gdf['geometry']:
            if not geom.is_empty and geom.is_valid:
                bounds.append(geom.bounds)
        if bounds:
            extents[category] = (
                min(bound[0] for bound in bounds),
                min(bound[1] for bound in bounds),
                max(bound[2] for bound in bounds),
                max(bound[3] for bound in bounds)
            )
        else:
            extents[category] = (0, 0, 0, 0)  # Default extent for empty GeoDataFrame

    print("Creating and saving polygon image...")
    create_polygon_image(clipped_gdfs, width, height, (left, bottom, right, top), output_file_path)
    print("Process completed.")

def create_polygon_image(clipped_gdfs, width, height, bounds, output_file_path):
    img = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(img)

    left, bottom, right, top = bounds

    def transform(x, y):
        try:
            px = int((x - left) / (right - left) * width)
            py = int((y - top) / (bottom - top) * height)
            return px, py
        except Exception as e:
            print(f"Error in transform: {e}")
            print(f"x: {x}, y: {y}, bounds: {bounds}, width: {width}, height: {height}")
            return 0, 0

    for category, gdf in clipped_gdfs.items():
        for geom in gdf['geometry']:
            try:
                if geom.geom_type == 'Polygon':
                    pixels = [transform(x, y) for x, y in geom.exterior.coords]
                    draw.polygon(pixels, outline=1, fill=1)
                elif geom.geom_type == 'MultiPolygon':
                    for part in geom:
                        pixels = [transform(x, y) for x, y in part.exterior.coords]
                        draw.polygon(pixels, outline=1, fill=1)
            except Exception as e:
                print(f"Error processing geometry: {e}")
                continue

    img.save(output_file_path, 'PNG')
    print(f"Image saved to {output_file_path}")

# Main execution
if __name__ == "__main__":
    start_time = time.time()  # Record start time
    
    gml_file_path = "tools/convert_datasets/use_Feinkartierung_Strasse_HH_2022-03-25/Feinkartierung_Strasse_HH_2022-03-25.gml"
    tif_file_path = "tools/convert_datasets/truedop20rgbi_32_566_5934_1_hh_2022.tif"
    output_file_path = "tools/convert_datasets/output_polygons.png"
    
    process_tif_file(gml_file_path, tif_file_path, output_file_path)

    end_time = time.time()  # Record end time
    elapsed_time = end_time - start_time  # Calculate elapsed time
    print(f"Total processing time: {elapsed_time:.2f} seconds")
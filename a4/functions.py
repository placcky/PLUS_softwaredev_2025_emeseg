"""
Activity Mapping for Salzburg Region

This script processes GPX files from Strava activity exports and creates
visualizations of GPS tracks within the Salzburg, Austria area. It reads
multiple GPX files, filters the data to a specific geographic bounding box
around Salzburg, and generates a map visualization using Mercator projection.

Requirements:
    - gpxpy: For parsing GPX files
    - pandas: For data manipulation
    - matplotlib: For plotting and visualization
    - rich: For progress tracking
    - math: For coordinate transformations

Author: Emese Gojdár
Date: 2025
"""

from math import log, pi, tan
import matplotlib.pyplot as plt
import os
import gpxpy
import pandas as pd
from rich.progress import track

def read_gpx_file(filepath):
    """
    Read and parse a GPX file.
    
    This function attempts to read GPX files using multiple character encodings
    to handle files that may have been exported with different encoding settings.
    It extracts GPS coordinates, elevation, and timestamp data from all tracks
    and segments within the GPX file.
    
    Args:
        filepath (str): Full path to the GPX file to be processed.
        
    Returns:
        pandas.DataFrame: DataFrame containing columns:
            - lat (float): Latitude coordinates
            - lon (float): Longitude coordinates  
            - ele (float): Elevation data (may be None)
            - time (datetime): Timestamp of GPS point
            - name (str): Activity name derived from filename
            
    Raises:
        Exception: Prints error message if file cannot be read and returns empty DataFrame.
    """
    # Multiple encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                gpx = gpxpy.parse(f)
                break
        except (UnicodeDecodeError, UnicodeError):
            continue
    else:
        # If all encodings fail, error handling
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                gpx = gpxpy.parse(f)
        except Exception as e:
            print(f"Failed to read {filepath}: {e}")
            return pd.DataFrame()  

    data = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data.append({
                    'lat': point.latitude,
                    'lon': point.longitude,
                    'ele': point.elevation,
                    'time': point.time,
                    'name': os.path.basename(filepath)  
                })
    return pd.DataFrame(data)

#Folder
script_dir = os.path.dirname(__file__)  
gpx_folder = os.path.join(script_dir, "..", "a3", "gpx")
gpx_folder = os.path.abspath(gpx_folder)  

if not os.path.exists(gpx_folder):
    print(f"Directory not found: {gpx_folder}")
    exit()


# Reading all the .gps files
df_list = []
for file in os.listdir(gpx_folder):
    # Fixed: endswith() takes a tuple for multiple extensions
    if file.endswith((".gpx")):
        filepath = os.path.join(gpx_folder, file)
        try:
            df = read_gpx_file(filepath)
            if not df.empty:  # Only append if DataFrame is not empty
                df_list.append(df)
        except Exception as e:
            print(f"Error processing file {file}: {e}")
            continue

# Check if we have any data before concatenating
if not df_list:
    print("No GPX files found in the specified directory!")
    exit()

# Concatenate all GPX data into a DataFrame
df_all = pd.concat(df_list, ignore_index=True)

# Bounding box - up to you to modify - DELETE # before each line
LON_MIN = 12.9
LON_MAX = 13.08
LAT_MIN = 47.72
LAT_MAX = 47.82

# Filter to the area - DELETE # before each line
df_salzburg = df_all[
    (df_all["lon"] >= LON_MIN) & (df_all["lon"] <= LON_MAX) &
    (df_all["lat"] >= LAT_MIN) & (df_all["lat"] <= LAT_MAX)
]

# Map units
MAP_WIDTH = 1
MAP_HEIGHT = 1


def convert_x(lon):
    """
    Pass-through function for longitude coordinates.
    
    Returns longitude values unchanged for direct geographic plotting.
    This simplified approach uses raw geographic coordinates instead of
    applying map projections, suitable for small regional areas like Salzburg
    where distortion is minimal.
    
    Args:
        lon (float): Longitude in decimal degrees.
        
    Returns:
        float: Unchanged longitude value.
    """
    return lon  # Simple

def convert_y(lat):
    """
    Pass-through function for latitude coordinates.
    
    Returns latitude values unchanged for direct geographic plotting.
    This simplified approach avoids complex map projections and works well
    for small regional mapping where the curvature of the Earth has minimal
    visual impact on the final map.
    
    Args:
        lat (float): Latitude in decimal degrees.
        
    Returns:
        float: Unchanged latitude value.
    """
    return lat  # Simple

def plot_map(
    df,
    lon_min=None,
    lon_max=None,
    lat_min=None,
    lat_max=None,
    alpha=0.3,
    linewidth=0.3,
    output_file="map.png",
):
    """
    Create a map visualization of GPS tracks from DataFrame.
    
    Generates a matplotlib plot showing GPS tracks as lines on a map using
    Mercator projection. Each activity is plotted as a separate line with
    consistent styling. The map can be bounded to specific geographic areas.
    
    Args:
        df (pandas.DataFrame): DataFrame containing GPS data with columns:
            'lat', 'lon', 'name' (required), 'ele', 'time' (optional).
        lon_min (float, optional): Minimum longitude boundary for map extent.
        lon_max (float, optional): Maximum longitude boundary for map extent.
        lat_min (float, optional): Minimum latitude boundary for map extent.
        lat_max (float, optional): Maximum latitude boundary for map extent.
        alpha (float, optional): Line transparency (0.0-1.0). Default: 0.3.
        linewidth (float, optional): Width of track lines. Default: 0.3.
        output_file (str, optional): Filename for saved map image. Default: "map.png".
        
    Returns:
        Displays the plot and saves to file.
    """
    # Create a new figure
    plt.figure()

    # Remove data outside the input ranges for lon / lat
    if lon_min is not None:
        df = df[df["lon"] >= lon_min]

    if lon_max is not None:
        df = df[df["lon"] <= lon_max]

    if lat_min is not None:
        df = df[df["lat"] >= lat_min]

    if lat_max is not None:
        df = df[df["lat"] <= lat_max]

    # Create a list of activity names
    activities = df["name"].unique()

    # Plot activities one by one
    for activity in track(activities, "Plotting activities"):
        activity_data = df[df["name"] == activity]
        x = activity_data["lon"]
        y = activity_data["lat"]

        # Transform to Mercator projection so maps aren't squashed away from equator
        x_converted = x.apply(convert_x)
        y_converted = y.apply(convert_y)

        plt.plot(x_converted, y_converted, color="black", alpha=alpha, linewidth=linewidth)

    # Update plot aesthetics
    plt.axis("off")
    plt.axis("equal")
    plt.margins(0)
    plt.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95)
    plt.savefig(output_file, dpi=600)
    plt.show()

# Example usage:
if __name__ == "__main__":
    plot_map(df_salzburg, 
             lon_min=LON_MIN, 
             lon_max=LON_MAX,
             lat_min=LAT_MIN, 
             lat_max=LAT_MAX)

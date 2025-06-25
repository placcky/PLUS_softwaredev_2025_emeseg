"""
Strava File Extractor
Extracts .gpx and .fit files that are gzip compressed (.gz) and copies them to the target folder.
"""

import os
import zipfile
import shutil
import gzip
from pathlib import Path

def unzip_strava_files(source_folder='.', target_folder=None):
    """
    Unzips Strava compressed files (.gpx.gz and .fit.gz) and copies 
    the extracted files to the target folder.
    
    Args:
        source_folder (str): Folder containing the compressed files (default: current directory)
        target_folder (str): Folder to copy extracted files to (default: same as source)
    """
    
    source_path = Path(source_folder)
    if target_folder is None:
        target_path = source_path
    else:
        target_path = Path(target_folder)
    
    # Create target folder if it doesn't exist
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Find all .gz files in the source folder (both .gpx.gz and .fit.gz)
    gz_files = list(source_path.glob('*.gz'))
    
    if not gz_files:
        print(f"No .gz files found in {source_path}")
        return
    
    print(f"Found {len(gz_files)} compressed files to process")
    
    extracted_count = 0
    
    for gz_file in gz_files:
        print(f"\nProcessing: {gz_file.name}")
        
        try:
            # Determine the output filename by removing .gz extension
            if gz_file.name.endswith('.gpx.gz'):
                output_filename = gz_file.name[:-3]  # Remove .gz
            elif gz_file.name.endswith('.fit.gz'):
                output_filename = gz_file.name[:-3]  # Remove .gz
            else:
                # For other .gz files, just remove .gz
                output_filename = gz_file.stem
            
            # Create target file path
            target_file = target_path / output_filename
            
            # Handle filename conflicts
            counter = 1
            original_target = target_file
            while target_file.exists():
                name_part = original_target.stem
                suffix = original_target.suffix
                target_file = target_path / f"{name_part}_{counter}{suffix}"
                counter += 1
            
            # Extract the gzipped file
            with gzip.open(gz_file, 'rb') as gz_in:
                with open(target_file, 'wb') as file_out:
                    shutil.copyfileobj(gz_in, file_out)
            
            print(f"  Extracted: {gz_file.name} -> {target_file.name}")
            extracted_count += 1
            
        except Exception as e:
            print(f"  Error processing {gz_file.name}: {str(e)}")
    
    print("\nProcessing complete!") 
    print(f"Extracted {extracted_count} files to {target_path}")
    
    # Show summary of file types
    gpx_files = list(target_path.glob('*.gpx'))
    fit_files = list(target_path.glob('*.fit'))
    print(f"Summary: {len(gpx_files)} GPX files, {len(fit_files)} FIT files")

def main():
    """
    Main function with example usage
    """
    print("Strava GPX File Unzipper")
    print("=" * 30)
    
    # You can modify these paths as needed
source_folder = r"C:\Users\emese\Documents\ErasmusGIS\semester_2\SoftwareDev\Strava\export_70483903\activities"     
target_folder = r"C:\Users\emese\Documents\ErasmusGIS\semester_2\SoftwareDev\Strava\export_70483903\activities"   

unzip_strava_files(source_folder, target_folder) 

if __name__ == "__main__":
    main()
import re
from typing import Optional, Union
import zipfile
import os


def extract_zip_file(progress_item, zip_file_path: str, dest_dir: str) -> str:
    """Extract a zip file to a destination directory.

    Args:
        zip_file_path (str): The path to the zip file.
        dest_dir (str): The directory where the zip file should be extracted.

    """
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(dest_dir)

    foulder_name = os.path.basename(zip_file_path).replace(".zip", "")
    return os.path.join(dest_dir, foulder_name)


def zip_folder(folder_path: str, output_path: str) -> Union[str, bool]:

    if not os.path.isdir(folder_path):
        return False

    if not output_path.endswith(".zip"):
        return False

    folder_path = os.path.abspath(folder_path)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

    return output_path

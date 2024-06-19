import zipfile


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

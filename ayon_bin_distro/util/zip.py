from typing import Union
import zipfile
import os
import platform


def _get_long_path(path: str) -> str:
    """Convert path to Windows long path format if needed.

    On Windows, paths longer than 260 characters require the \\?\ prefix
    to work correctly with most file operations.

    Args:
        path (str): The original file path.

    Returns:
        str: The path with long path prefix on Windows, or original on other OS.
    """
    if platform.system().lower() != "windows":
        return path

    # Already has the prefix
    if path.startswith("\\\\?\\"):
        return path

    # Convert to absolute path and add prefix
    abs_path = os.path.abspath(path)
    return "\\\\?\\" + abs_path


def extract_zip_file(progress_item, zip_file_path: str, dest_dir: str) -> str:
    """Extract a zip file to a destination directory.

    Args:
        zip_file_path (str): The path to the zip file.
        dest_dir (str): The directory where the zip file should be extracted.

    Returns:
        str: Path to the extracted content directory.

    Note:
        On Windows, this function handles paths longer than MAX_PATH (260 chars)
        by using the \\?\ long path prefix.
    """
    # Use long path prefix on Windows to handle paths > 260 characters
    long_dest_dir = _get_long_path(dest_dir)

    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        # Extract each file individually with long path support
        for member in zip_ref.namelist():
            # Normalize path separators for Windows (zip uses forward slashes)
            normalized_member = member.replace("/", os.sep)

            # Build the full destination path with long path prefix
            dest_path = os.path.join(long_dest_dir, normalized_member)

            if member.endswith('/'):
                # Create directory
                os.makedirs(dest_path, exist_ok=True)
            else:
                # Ensure parent directory exists
                parent_dir = os.path.dirname(dest_path)
                os.makedirs(parent_dir, exist_ok=True)

                # Extract file
                with zip_ref.open(member) as source:
                    with open(dest_path, "wb") as target:
                        target.write(source.read())

    foulder_name = os.path.basename(zip_file_path).replace(".zip", "")
    return os.path.join(dest_dir, foulder_name)


# TODO add progress_item optionm
def zip_folder(folder_path: str, output_path: str) -> Union[str, bool]:
    """zip a given folder to a given output path

    Args:
        folder_path: folder to be zipped
        output_path: zip output location (needs to end in .zip)

    Returns:
        Union[str, bool]: Returns False if zip failed. On success the output path is returned.

    """
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

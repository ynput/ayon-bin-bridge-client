from typing import Union
import zipfile
import os
import platform


class ZipFileLongPaths(zipfile.ZipFile):
    """Allows longer paths in zip files.

    Regular DOS paths are limited to MAX_PATH (260) characters, including
    the string's terminating NUL character.
    That limit can be exceeded by using an extended-length path that
    starts with the '\\?\' prefix.
    """
    _is_windows = platform.system().lower() == "windows"

    def _extract_member(self, member, tpath, pwd):
        if self._is_windows:
            tpath = os.path.abspath(tpath)
            if tpath.startswith("\\\\"):
                tpath = "\\\\?\\UNC\\" + tpath[2:]
            else:
                tpath = "\\\\?\\" + tpath

        return super()._extract_member(member, tpath, pwd)


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
    with ZipFileLongPaths(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(dest_dir)

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

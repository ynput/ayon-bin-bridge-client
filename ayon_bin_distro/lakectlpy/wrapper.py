import sys
import subprocess
import os
import shutil
from typing import Optional, Union
import yaml
import platform
import fcntl

from ..work_handler import worker


def create_config(
    dist_path: str,
    access_key_id: str,
    secret_access_key: str,
    server_url: str,
    enable_retries: bool = True,
    retrie_max_attempts: int = 4,
    retrie_max_wait: str = "30s",
    retrie_min_wait: str = "200ms",
) -> Union[str, None]:
    if not dist_path.endswith(".yaml"):
        return None
    data = {
        "credentials": {
            "access_key_id": access_key_id,
            "secret_access_key": secret_access_key,
        },
        "metastore": {
            "glue": {"catalog_id": ""},
            "hive": {"db_location_uri": "file:/user/hive/warehouse/", "uri": ""},
        },
        "server": {
            "endpoint_url": server_url,
            "retries": {
                "enabled": enable_retries,
                "max_attempts": retrie_max_attempts,
                "max_wait_interval": retrie_max_wait,
                "min_wait_interval": retrie_min_wait,
            },
        },
    }

    with open(dist_path, "w") as file:
        yaml.dump(data, file, default_flow_style=True)

    return dist_path


# TODO test windows version
class LakeCtl:
    def __init__(
        self,
        conf_file_path=None,
        base_uri_oberwrite=None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        server_url: Optional[str] = None,
    ) -> None:

        self.bin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")

        if platform.system().lower() == "windows":
            self.wrapped_lakectl = os.path.join(self.bin_path, "lakectl.exe")
        elif platform.system().lower() == "linux":
            self.wrapped_lakectl = os.path.join(self.bin_path, "lakectl")
        else:
            raise NotImplementedError(
                "only windows and linux are suported at the current time"
            )

        self.conf_file = os.path.join(os.path.dirname(__file__), "bin", ".lakectl.yaml")

        if not os.path.exists(self.wrapped_lakectl):
            raise RuntimeError("the lakectl exe is missing")

        if not os.path.exists(self.conf_file):
            raise RuntimeError("the lakectl config file is missing")

        with open(self.conf_file, "r") as file:
            config = yaml.safe_load(file)
            self.access_key_id = config["credentials"]["access_key_id"]
            self.secret_access_key = config["credentials"]["secret_access_key"]
            self.endpoint_url = config["server"]["endpoint_url"]

        if base_uri_oberwrite:
            self.base_uri = base_uri_oberwrite
        else:
            self.base_uri = None

        if access_key_id and secret_access_key and server_url:
            os.environ["LAKECTL_SERVER_ENDPOINT_URL"] = server_url
            os.environ["LAKECTL_CREDENTIALS_ACCESS_KEY_ID"] = access_key_id
            os.environ["LAKECTL_CREDENTIALS_SECRET_ACCESS_KEY"] = secret_access_key

        elif conf_file_path:
            self.conf_file = os.path.abspath(conf_file_path)
        else:
            self.conf_file = os.path.join(self.bin_path, ".lakectl.yaml")

        self.data = ""

    def _run(
        self, lakectl_command: list, cwd=None, non_blocking_stdout: bool = True
    ) -> subprocess.Popen:
        base_uri_command = []
        if self.base_uri:
            base_uri_command = ["--base-uri", self.base_uri]

        process = subprocess.Popen(
            [
                self.wrapped_lakectl,
                "--config",
                f"{self.conf_file}",
                *base_uri_command,
                *lakectl_command,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=cwd,
        )
        if process.stdout and process.stderr and non_blocking_stdout:
            flags = fcntl.fcntl(process.stdout.fileno(), fcntl.F_GETFL)
            fcntl.fcntl(process.stdout.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)
            flags = fcntl.fcntl(process.stderr.fileno(), fcntl.F_GETFL)
            fcntl.fcntl(process.stderr.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)

        return process

    def help(self):
        process = self._run(["--help"])

        while process.poll() is None:
            sys.stdout.write(process.stdout.readline())

    def list_repo_objects(self, lake_fs_repo_uri: str):
        process = self._run(
            ["fs", "ls", "-r", lake_fs_repo_uri], non_blocking_stdout=False
        )
        object_list = []
        while process.poll() is None:
            stdout = process.stdout.readline()
            if stdout and "object" in stdout:
                object_list.append(stdout.split()[-1])

        return object_list

    def clone_local(
        self,
        progress_obj: Optional[Union[worker.BaseProgressItem, worker.ProgressItem]],
        repo_branch_uri: str,
        dist_path: str,
        exists_okay=False,
        print_stdout: bool = False,
    ) -> str:

        if dist_path and exists_okay:
            if os.path.exists(dist_path):
                shutil.rmtree(dist_path)
            os.makedirs(dist_path)

        process = self._run(["local", "clone", repo_branch_uri], cwd=dist_path)

        current_progress = None
        current_object = None
        dest_dir = ""

        while process.poll() is None:
            stdout = process.stdout.readline()
            stderr = process.stderr.readline()

            if stderr and print_stdout:
                sys.stderr.write(stderr)
                sys.stderr.flush()
                if progress_obj:
                    progress_obj.failed = True
                    continue

            if not stdout:
                continue

            if stdout and progress_obj:
                current_line_split = stdout.split()
                for i in current_line_split:
                    if "%" in i:
                        current_progress_r = float(i.replace("%", ""))
                        if current_progress_r != current_progress:
                            current_progress = current_progress_r
                            progress_obj.progress = int(current_progress)

                if "download" in current_line_split:
                    if current_line_split[1] != current_object:
                        current_object = current_line_split[1]

            if "Successfully cloned" in stdout:
                dest_dir = os.path.abspath(
                    stdout.split(" to ")[-1][:-2].strip()
                )  # we split the string because its constructed as a sentence with a . At then end

            if print_stdout:
                sys.stdout.write(stdout)
                sys.stdout.flush()
        return dest_dir

    def clone_element(
        self,
        progress_obj: Optional[Union[worker.BaseProgressItem, worker.ProgressItem]],
        lake_fs_object_uir: str,
        dist_path: str,
        print_stdout: bool = False,
    ) -> str:
        process = self._run(["fs", "download", lake_fs_object_uir, dist_path])

        if progress_obj:
            progress_obj.progress = -1
        dest_path = ""
        while process.poll() is None:
            stdout = process.stdout.readline()
            stderr = process.stderr.readline()

            if stderr:
                if print_stdout:
                    sys.stderr.write(stderr)
                    sys.stderr.flush()
                if progress_obj:
                    progress_obj.failed = True
                continue
            if "download:" in stdout and "to" in stdout:
                dest_path = os.path.abspath(stdout.split(" to ")[-1].strip())
            if stdout and print_stdout:
                sys.stdout.write(stdout)
                sys.stdout.flush()
        return dest_path

    def commit_local(self, commit_message: str, local_path=None):
        process = self._run(
            ["local", "commit", ".", "-m", commit_message], cwd=local_path
        )

        while process.poll() is None:
            sys.stdout.write(process.stdout.readline())

import sys
import subprocess
import os
import shutil
import select
from typing import Union
import yaml
import platform
import fcntl

from ..work_handler import worker


# TODO windows version (should just be a singe change in _run)
class LakeCtl:
    def __init__(self, conf_file_pos=None, base_uri_oberwrite=None) -> None:
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

        if conf_file_pos:
            self.conf_file = os.path.abspath(conf_file_pos)
        else:
            self.conf_file = os.path.join(self.bin_path, ".lakectl.yaml")
        self.data = ""

    def _run(self, lakectl_command: list, cwd=None) -> subprocess.Popen:
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

        flags = fcntl.fcntl(process.stdout.fileno(), fcntl.F_GETFL)
        fcntl.fcntl(process.stdout.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)
        flags = fcntl.fcntl(process.stderr.fileno(), fcntl.F_GETFL)
        fcntl.fcntl(process.stderr.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)

        return process

    def help(self):
        process = self._run(["--help"])

        while process.poll() is None:
            sys.stdout.write(process.stdout.readline())

    def clone_local(
        self,
        progress_obj: Union[worker.BaseProgressItem, worker.ProgressItem],
        repo_branch_uri: str,
        dist_path: str,
        exists_okay=False,
        print_stdout: bool = False,
    ) -> None:

        if dist_path:
            if exists_okay:
                if os.path.exists(dist_path):
                    shutil.rmtree(dist_path)
            os.makedirs(dist_path)

        process = self._run(["local", "clone", repo_branch_uri], cwd=dist_path)

        current_progress = None
        current_object = None

        while process.poll() is None:
            if select.select([process.stdout], [], [], 0.1)[0]:
                current_line = process.stdout.readline()
                if current_line:
                    current_line_split = current_line.split()
                    for i in current_line_split:
                        if "%" in i:
                            current_progress_r = float(i.replace("%", ""))
                            if current_progress_r != current_progress:
                                current_progress = current_progress_r
                                progress_obj.progress = int(current_progress)

                    if "download" in current_line_split:
                        if current_line_split[1] != current_object:
                            current_object = current_line_split[1]

                    if print_stdout:
                        sys.stdout.write(current_line)
                        sys.stdout.flush()

            if select.select([process.stderr], [], [], 0.1)[0]:
                stderr = process.stderr.readline()
                if stderr:
                    progress_obj.failed = True
                    sys.stderr.write(stderr)
                    sys.stderr.flush()

        if print_stdout:
            for line in process.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()

            for line in process.stderr:
                sys.stderr.write(line)
                sys.stderr.flush()

        process.stdout.close()
        process.stderr.close()

    # TODO i think fs dose not return progress (needs testing with a big zip)
    def clone_element(
        self,
        progress_obj: Union[worker.BaseProgressItem, worker.ProgressItem],
        lake_fs_object_uir: str,
        dist_path: str,
    ):
        process = self._run(["fs", "download", lake_fs_object_uir, dist_path])
        while process.poll() is None:
            if select.select([process.stdout], [], [], 0.1)[0]:
                current_line = process.stdout.readline()
                if current_line:
                    progress_obj.progress = -1
            if process.stderr.readline():
                progress_obj.failed = True

    def commit_local(self, commit_message: str, local_path=None):
        process = self._run(
            ["local", "commit", ".", "-m", commit_message], cwd=local_path
        )

        while process.poll() is None:
            sys.stdout.write(process.stdout.readline())

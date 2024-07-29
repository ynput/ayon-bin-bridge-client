import sys
import subprocess
import os
import shutil
from typing import Dict, Optional, Union
import platform

from ..work_handler import worker

if sys.platform.lower() =="linux":
    import fcntl

# TODO test windows version
class LakeCtl:
    def __init__(
        self,
        base_uri_oberwrite=None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        server_url: Optional[str] = None,
    ) -> None:

        self.bin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
        self.lake_config = os.path.join(self.bin_path, ".lakectl.yaml")
        if platform.system().lower() == "windows":
            self.wrapped_lakectl = os.path.join(self.bin_path, "lakectl.exe")
        elif platform.system().lower() == "linux":
            self.wrapped_lakectl = os.path.join(self.bin_path, "lakectl")
            os.chmod(self.wrapped_lakectl, 0o755)
        else:
            raise NotImplementedError(
                "only windows and linux are suported at the current time"
            )

        if not os.path.exists(self.wrapped_lakectl):
            raise RuntimeError("the lakectl exe is missing")

        if base_uri_oberwrite:
            self.base_uri = base_uri_oberwrite
        else:
            self.base_uri = None

        if access_key_id:
            os.environ["LAKECTL_CREDENTIALS_ACCESS_KEY_ID"] = access_key_id
        if secret_access_key: 
            os.environ["LAKECTL_CREDENTIALS_SECRET_ACCESS_KEY"] = secret_access_key
        if server_url:
            os.environ["LAKECTL_SERVER_ENDPOINT_URL"] = server_url

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
                "--base-uri", self.lake_config,
                *base_uri_command,
                *lakectl_command,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=cwd,
        )
        # TODO implement non blocking stderr stdout pull for windows 
        if process.stdout and process.stderr and non_blocking_stdout and sys.platform.lower() =="linux":
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

    def get_element_info(self, lake_fs_object_uir:str) -> Dict[str,str]:
        data_dict = {}
        process = self._run(["fs", "stat", lake_fs_object_uir], non_blocking_stdout=False)

        while process.poll() is None:
                data_line = process.stdout.readline()
                data_parts = [entry.strip() for entry in str(data_line).split(":")]
                data_dict[data_parts[0]] = " ".join(data_parts[1:])

        return data_dict

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

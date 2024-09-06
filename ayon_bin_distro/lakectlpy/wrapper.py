import os
import platform
import shutil
import subprocess
import sys
from typing import Dict, Optional, Union

from ..work_handler import worker

if sys.platform.lower() == "linux":
    import fcntl


# TODO test windows version
class LakeCtl:
    def __init__(
        self,
        base_uri_oberwrite: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        server_url: Optional[str] = None,
    ) -> None:
        """Wrapper class for the LakeCtl binary (windows, linux)

        Args:
            base_uri_oberwrite: optional str base URI used for lakeFS address parse. can be set in lakectl.yaml
            access_key_id: optional str LakeFs server acces key Id. can be set in lakectl.yaml
            secret_access_key: optional str LakeFs server acces key. can be set in lakectl.yaml
            server_url: optional str used to connect to a specific LakeFs server

        Raises:
            NotImplementedError: raised if a method is called that we do not yet implement usually because no one needed it until now (best to write a ticket)
            RuntimeError: raised to protect lakectl calles with invalid data. (specific data will be in the error info )
        """
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
            self.lake_ctl_acces_key_id = access_key_id
            # os.environ["LAKECTL_CREDENTIALS_ACCESS_KEY_ID"] = access_key_id
        if secret_access_key:
            self.lake_ctl_secret_acces_key = secret_access_key
            # os.environ["LAKECTL_CREDENTIALS_SECRET_ACCESS_KEY"] = secret_access_key
        if server_url:
            self.lake_ctl_server_url = server_url
            # os.environ["LAKECTL_SERVER_ENDPOINT_URL"] = server_url

        self.data = ""

    def _run(
        self, lakectl_command: list, cwd=None, non_blocking_stdout: bool = True
    ) -> subprocess.Popen:
        """call lakectl bin with args gets lakectl bin, base uri and config from the member vars

        Args:
            cwd (): option to move the path from where we call the lakectl passed to subprocess.Popen
            lakectl_command: lakectl command to run
            non_blocking_stdout: enable non blocking stdout on linux only

        Returns:

        """
        base_uri_command = []
        if self.base_uri:
            base_uri_command = ["--base-uri", self.base_uri]

        wrapper_env = os.environ.copy()
        if self.lake_ctl_acces_key_id:
            wrapper_env["LAKECTL_CREDENTIALS_ACCESS_KEY_ID"] = self.lake_ctl_acces_key_id 
        if self.lake_ctl_secret_acces_key:
            wrapper_env["LAKECTL_CREDENTIALS_SECRET_ACCESS_KEY"] = self.lake_ctl_secret_acces_key 
        if self.lake_ctl_server_url:
            wrapper_env["LAKECTL_SERVER_ENDPOINT_URL"] = self.lake_ctl_server_url 
        process = subprocess.Popen(
            [
                self.wrapped_lakectl,
                "--config",
                self.lake_config,
                *base_uri_command,
                *lakectl_command,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=cwd,
            env=wrapper_env
        )
        # TODO implement non blocking stderr stdout pull for windows
        if (
            process.stdout
            and process.stderr
            and non_blocking_stdout
            and sys.platform.lower() == "linux"
        ):
            flags = fcntl.fcntl(process.stdout.fileno(), fcntl.F_GETFL)
            fcntl.fcntl(process.stdout.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)
            flags = fcntl.fcntl(process.stderr.fileno(), fcntl.F_GETFL)
            fcntl.fcntl(process.stderr.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)

        return process

    def help(self):
        """print the output of lakectl --help"""
        process = self._run(["--help"])

        while process.poll() is None:
            if process.stdout is None:
                continue
            sys.stdout.write(process.stdout.readline())

    def list_repo_objects(self, lake_fs_repo_uri: str):
        """list objects on a given repository

        Args:
            lake_fs_repo_uri: lakeFs internal uri for the repository

        Returns:

        """
        process = self._run(
            ["fs", "ls", "-r", lake_fs_repo_uri], non_blocking_stdout=False
        )
        object_list = []
        while process.poll() is None:
            if process.stdout is None:
                continue
            stdout = process.stdout.readline()
            if stdout and "object" in stdout:
                object_list.append(stdout.split()[-1])

        return object_list

    def clone_local(
        self,
        progress_obj: Optional[Union[worker.BaseProgressItem, worker.ProgressItem]],
        repo_branch_uri: str,
        dist_path: str,
        exists_okay: bool = False,
        print_stdout: bool = False,
    ) -> str:
        """clone a lakeFs repository to a local path

        Args:
            exists_okay (bool): delete dist_path if folder exists
            progress_obj: optional ProgressItem to connect a wrapper to an work item
            repo_branch_uri: str lakeFs internal uri to the repository
            dist_path: str destination path
            print_stdout: bool print stdout or operate silent

        Returns:
            str: The destination directory.

        """
        if dist_path and exists_okay:
            if os.path.exists(dist_path):
                shutil.rmtree(dist_path)
            os.makedirs(dist_path)

        process = self._run(["local", "clone", repo_branch_uri], cwd=dist_path)
        current_progress = None
        current_object = None
        dest_dir = ""

        while process.poll() is None:
            if process.stdout is None:
                continue
            stdout = process.stdout.readline()
            if process.stderr is None:
                continue
            stderr = process.stderr.readline()

            if stderr and print_stdout:
                sys.stderr.write(stderr)
                sys.stderr.flush()
                if progress_obj:
                    progress_obj.failed = True
                    continue

            if not stdout:
                continue

            if progress_obj:
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

    def get_element_info(self, lake_fs_object_uir: str) -> Dict[str, str]:
        """get metadata information about a given lakeFs object

        Args:
            lake_fs_object_uir: lakeFs internal uri to an lakeFs element

        Returns:
            Dict[str, str]: The element info for the LakeFS object.

        """
        data_dict = {}
        process = self._run(
            ["fs", "stat", lake_fs_object_uir], non_blocking_stdout=False
        )

        while process.poll() is None:
            if process.stdout is None:
                continue
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
        """clone an individual lakeFs element to a local path

        Args:
            progress_obj: optional ProgressItem to connect to a workItem
            lake_fs_object_uir: str lakeFs internal object uri
            dist_path: str machine local path to clone to
            print_stdout: bool enable printing the stdout

        Returns:
            str: The destination path.

        """
        process = self._run(["fs", "download", lake_fs_object_uir, dist_path])

        if progress_obj:
            progress_obj.progress = -1
        dest_path = ""
        while process.poll() is None:
            if process.stdout is None:
                continue
            stdout = process.stdout.readline()
            if process.stderr is None:
                continue
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

    def commit_local(self, commit_message: str, local_path: Optional[str] = None):
        """commits changes from a local repository (like git commit -m)

        Args:
            commit_message (str): Commit message that will be send to lakeFs for the commit
            local_path (Optional[str]): Specify the local repository path, if not provided the
                current working directory (cwd) will be used.
        """
        process = self._run(
            ["local", "commit", ".", "-m", commit_message], cwd=local_path
        )

        while process.poll() is None:
            if process.stdout is None:
                continue
            sys.stdout.write(process.stdout.readline())

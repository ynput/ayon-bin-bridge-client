import sys 
import subprocess
import os
import shutil
import select
from typing import Callable

# TODO windows version (should just be a singe change in _run)
class LakeCtl:
    def __init__(self, conf_file_pos=None, base_uri_oberwrite=None) -> None:
        self.bin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
        self.wrapped_lakectl = os.path.join(self.bin_path, "lakectl")

        if base_uri_oberwrite:
            self.base_uri = base_uri_oberwrite
        else:
            self.base_uri = None

        if conf_file_pos:
            self.conf_file = os.path.abspath(conf_file_pos)
        else:
            self.conf_file = os.path.join(self.bin_path, ".lakectl.yaml")
        self.data = ""
    
    def _run(self, lakectl_command:list, cwd=None):
        base_uri_command = []
        if self.base_uri:
            base_uri_command = ["--base-uri", self.base_uri]

        process = subprocess.Popen([self.wrapped_lakectl, "--config", f"{self.conf_file}", *base_uri_command, *lakectl_command], stdout=subprocess.PIPE, universal_newlines=True, cwd=cwd)

        return process

    def help(self):
        process = self._run(["--help"])

        while process.poll() is None:
            sys.stdout.write(process.stdout.readline())

    def clone_local(self, repo_branch_uri:str, dist_path=None, exists_okay=False, progress_callback:Callable[[int], None]=None, finished_callback:Callable[[], None]=None, element_name_callback:Callable[[str], None]=None, print_stdout:bool = False)->None:
        
        if dist_path:
            if exists_okay:
                    if os.path.exists(dist_path):
                        shutil.rmtree(dist_path)
            os.makedirs(dist_path)

        process = self._run(["local", "clone", repo_branch_uri], cwd=dist_path)

        while process.poll() is None:
            if select.select([process.stdout], [], [], 0.1)[0]:

                # get the data we want to send to an optional callback (object name and progress)
                current_line = process.stdout.readline()
                current_line_split = current_line.split()
                current_progress = ""
                for i in current_line_split:
                    if "%" in i:
                        current_progress_r = float(i.replace("%", ""))
                        if not current_progress_r == current_progress:
                            current_progress = current_progress_r
                            if progress_callback:
                                progress_callback(int(current_progress))

                current_object = ""
                if "download" in current_line_split:
                    if not current_line_split[1] == current_object:
                        current_object = current_line_split[1]
                        if element_name_callback:
                            element_name_callback(current_object)
                
                # write out the debug info to the terminal
                if print_stdout:
                    sys.stdout.write(current_line)
                    sys.stdout.flush()
        if finished_callback:
            finished_callback()

    def commit_local(self, commit_message:str, local_path=None):
        process = self._run(["local", "commit", ".", "-m", commit_message], cwd=local_path)

        while process.poll() is None:
            sys.stdout.write(process.stdout.readline())

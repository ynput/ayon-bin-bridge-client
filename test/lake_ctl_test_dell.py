import os 
import shutil
import sys

from qtpy.QtWidgets import QApplication

from work_handler import AyonWorkSys
from gui.BinDistroUiElements import AyonMultiProgressWidget
from lakectlpy import wrapper

ctl = wrapper.LakeCtl()

from typing import Callable 

def load_ayon_usd(progress_callback:Callable[[int], None], finished_callback:Callable[[], None], lake_path:str, dist_path:str):
    ctl.clone_local(repo_branch_uri=lake_path, dist_path=dist_path, exists_okay=True, finished_callback=finished_callback, progress_callback=progress_callback)

def main():
    icon_path = os.path.join(os.path.abspath(os.curdir), "test","ay-symbol-blackw-full.png")  
    app = QApplication(sys.argv)
    download_window = AyonMultiProgressWidget()
   
    WorkQueA = AyonWorkSys.AyonWorkQue()

    for i in range(20):
        i = i+1 # i want the numbers in the display to start at 1 that all
        pgbA = download_window.add_progress_bar(text=f"Download Usd {i}", icon_path=icon_path)
        
        d_path = os.path.join(os.path.abspath(os.curdir), "dell", f"foulder_{i}")
        if os.path.exists(d_path):
            shutil.rmtree(d_path)
        os.mkdir(d_path)

        WorkItemA = AyonWorkSys.AyonWorkItem()
        WorkItemA.name = f"test item {i}"
        WorkItemA.func = load_ayon_usd
        WorkItemA.args = ["lakefs://ayon-usd/main/", os.path.join(os.path.abspath(os.curdir), d_path)] 
        WorkItemA.kargs = {}
        WorkItemA.additional_progress_callback = pgbA.set_progress
        WorkItemA.additional_finish_callback = pgbA.close_progress_bar

        WorkHanlderB = AyonWorkSys.AyonWorkItemHandler()
        WorkHanlderB.add_work_item(WorkItemA)

        WorkQueA.add_work_handler(WorkHanlderB)



    WorkQueA.start_all()

    download_window.show()
    sys.exit(app.exec_())


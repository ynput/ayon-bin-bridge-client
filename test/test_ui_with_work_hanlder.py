import os 
import sys
from time import time
from typing import List
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, pyqtSignal, pyqtSlot
import time

import threading
from work_handler import AyonWorkSys
from gui.BinDistroUiElements import AyonProgressBar, AyonMultiProgressWidget


def main():
    icon_path = os.path.join(os.path.abspath(os.curdir), "test","ay-symbol-blackw-full.png")  


    app = QApplication(sys.argv)
    download_window = AyonMultiProgressWidget()
   

    WorkQueA = AyonWorkSys.AyonWorkQue()

    for i in range(10):
        i = i+1 # i want the numbers in the display to start at 1 that all
        pgbA = download_window.add_progress_bar(text=f"test item {i}", icon_path=icon_path)

        WorkItemA = AyonWorkSys.AyonWorkItem()
        WorkItemA.name = f"test item {i}"
        WorkItemA.func = AyonWorkSys.ayon_work_item_excample_func
        WorkItemA.args = ["this"]
        WorkItemA.kargs = {"welxxcsdf":"this"}
        WorkItemA.additional_progress_callback = pgbA.set_progress
        WorkItemA.additional_finish_callback = pgbA.close_progress_bar

        WorkHanlderB = AyonWorkSys.AyonWorkItemHandler()
        WorkHanlderB.add_work_item(WorkItemA)

        WorkQueA.add_work_handler(WorkHanlderB)



    WorkQueA.start_all()

    download_window.show()
    sys.exit(app.exec_())


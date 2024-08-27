# Getting Started

This repository is designed to be used as a library.\n in most cases it will be
easy to have it linked as a git submodule. But you could also use pip install
against the ayon_bin_distro folder to install it like any other python module.

there are 4 modules availalbe for your use.

## gui

this module is mainly concerned about giving you easy library classes that allow
showing a fancy ui to your user that displays the work_hanlder state

the most important clas is the `ProgressDialog` class. it allows you to display
the state of an work_controller.

`ProgressDialog`

- controller
- delet_progress_bar_on_finish: bool = True,
- close_on_finish: bool = False,
- auto_close_timeout: float = 0.5,
- title: str = "",

```py
import sys
from qtpy import QtWidgets
from ayon_bin_distro.gui import progress_ui

app = QtWidgets.QApplication(sys.argv)
ui = progress_ui.ProgressDialog(<Controler_Instance>)

ui.start()
sys.exit(app.exec_())
```

## lakectlpy

## util

## work_hanlder

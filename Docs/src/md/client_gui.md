# ayon_bin_distro.gui: GUI utils for the work handler module

The target for this module is to give an convenient way to display the state of
an [work_hanlder Controller](md_md_client_work_hanlder.html@id="doc-content")

The most important class is the `ProgressDialog` class. It allows you to display
the state of an work_controller.

Most common example usage would be

```py
import sys
from qtpy import QtWidgets
from ayon_bin_distro.gui import progress_ui

app = QtWidgets.QApplication(sys.argv)
ui = progress_ui.ProgressDialog(<Controler_Instance>)

ui.start()
sys.exit(app.exec_())
```

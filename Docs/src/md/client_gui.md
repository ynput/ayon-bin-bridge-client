# ayon_bin_distro.gui: GUI utils for the work handler module

**Module Target**

This module aims to provide a convenient way to display the state of a [work_handler Controller](md_md_client_work_hanlder.html@id="doc-content").

**Key Class** 

The most important class in this module is `ProgressDialog`. It enables you to display the state of a work_controller.

**Common Example Usage**

```py
import sys
from qtpy import QtWidgets
from ayon_bin_distro.gui import progress_ui

app = QtWidgets.QApplication(sys.argv)
ui = progress_ui.ProgressDialog(<Controler_Instance>)

ui.start()
sys.exit(app.exec_())
```

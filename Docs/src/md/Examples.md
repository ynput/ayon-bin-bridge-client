# Examples

The best way to understand this tool set is to look at the tests we try to have
high test coverage so even when the docs don't show you an example you might
find your answer there.

For the rest we will have a quick look at how to use this tool set.

### Using the Work Hanlder

This is an example on how to use a controller with items that depend on each
other both by running after each other but also the second item depends on the
output of itemA

```py
controller = worker.Controller()

itemA = controller.construct_work_item(func=func_name)
controller.construct_work_item(
    func=fun_name,
    kwargs={"data": itemA.connect_func_return},
    dependency_id=[itemA.get_uuid()],
)

controller.start()

while controller.is_running():
    print("Controller is running")
    time.sleep(0.2)
```

so how dose it work ?

When we create a WorkItem it will have an uuid that we can use to make an other
work item in the same Controller dependent on it.

We also have a connect_func_return option in every WorkItem this is done to
ensures itemA has run and can safely be evaluated before getting the needed data
for the kwargs in this case

### Connection the Work handler with the Ui

This is a very simple example to show how you could connect a Controller to an
ProgressDialog instance.\n remember the ProgressDialog will start the work
handler for you.

```py
icon_path = "path/to/png.png"

app = QtWidgets.QApplication(sys.argv)

controller = worker.Controller()
ui = progress_ui.ProgressDialog(controller,title="A Titile")

controller.construct_work_item(func=func, progress_title="a cool running functoin", icon_path=icon_path)

ui.start()
sys.exit(app.exec_())
```

Interesting to know might be. Every item in the work handler can have an
individual icon and title.

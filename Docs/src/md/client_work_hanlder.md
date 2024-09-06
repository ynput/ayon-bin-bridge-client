# ayon_bin_distro.work_handler: classes to distribute work items

The work handler package is concerned about allowing you to create dependent
tasks and then distributing them.

This example is one of the easy ways to use a controller and construct a work
item on it.

```py
controller = worker.Controller()
controller.construct_work_item(func=test_func, progress_title=f"test{i}")
```

You can also add a work item manually, most of the time the construct work item
is a bit simpler to use as it reduces the lines to write.

```py
work_item_instance = WorkItem()
Controller.add_work_item(work_item_instance)
```

It's important to know that every work item will be started on a separate thread
so the thread that calls `Controller.start()` is free to continue its work.

When the controller is connected to a GUI you don't need to start the
controller this will be handled by the GUI instance instead.

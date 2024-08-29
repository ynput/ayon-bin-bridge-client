# ayon_bin_distro.work_halnder: classes to distribute work items

the work hanlder package is concerend about allowing you to create dependend
tasks and then distrusting them.

this excample is one of the easy ways to use a controller and construct a work
item on it

```py
controller = worker.Controller()
controller.construct_work_item(func=test_func, progress_title=f"test{i}")
```

you can also add a work item manually, most of the time the construct work item
is a bit simpler to use as it reduces the lines to write.

```py
work_item_instance = WorkItem()
Controller.add_work_item(work_item_instance):
```

Its important to know that every work item will be started on a separate thread
so the thread that calls `Controller.start()` is free to continue its work. \n
when the controller is connected to an GUI you don't need to start the
controller this will be handled by the GUI instance.

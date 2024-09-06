# ayon_bin_distro.work_handler: Classes for Distributing Work Items

The `work_handler` package focuses on enabling you to create dependent tasks and subsequently distribute them efficiently.

Here's an easy way to use a controller and construct a work item on it:

```python
controller = worker.Controller()
controller.construct_work_item(func=test_func, progress_title=f"test{i}")
```

You can also add work items manually. However, using `construct_work_item` often simplifies the process by reducing the amount of code to write:

```python
work_item_instance = WorkItem()
Controller.add_work_item(work_item_instance)
```

It's crucial to note that each work item will be started on a separate thread. This allows the thread that calls `Controller.start()` to continue its own tasks freely.

When connected to a GUI, there is no need to start the controller manually; instead, this process will be managed by the GUI instance itself.

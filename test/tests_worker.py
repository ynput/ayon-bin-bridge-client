from ayon_bin_distro.work_handler import worker
import random
import time


def test_func(progress_item):
    for i in range(101):
        time.sleep(random.uniform(0.01, 0.1))
        progress_item.progress = i


def test_with_fake_data_with_progess_titile():

    controller = worker.Controller()
    for i in range(100):
        controller.construct_work_item(func=test_func, progress_title=f"test{i}")
    controller.start()

    while controller.is_running():
        for index, item in controller.get_progress_items():
            print(
                "\n",
                "item:",
                index,
                "\n",
                "failed:",
                item.is_failed,
                ",progress:",
                item.progress,
            )
        time.sleep(0.5)

    if controller.work_finished:
        print("controller reported work finished")


def test_with_fake_data_without_progess_titile():
    controller = worker.Controller()
    for i in range(10):
        controller.construct_work_item(func=test_func)
    controller.start()

    while controller.is_running():
        for index, item in controller.get_progress_items():
            print(
                "\n",
                "item:",
                index,
                "\n",
                "failed:",
                item.is_failed,
                ",progress:",
                item.progress,
            )
        time.sleep(0.5)

    if controller.work_finished:
        print("controller reported work finished")

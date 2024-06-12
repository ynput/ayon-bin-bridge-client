import time
import uuid
import threading
from typing import Callable, Any, List, Dict, Optional, Set, Union


class BaseProgressItem:
    """Base class for ProgressItem. Holds common attributes and initialization logic."""

    def __init__(
        self,
        started: bool = False,
        progress: Optional[int] = -1,
        finished: bool = False,
        failed: bool = False,
    ):
        self._id = uuid.uuid4()
        self.started = started
        self.progress = progress
        self.finished = finished
        self.failed = failed

    @property
    def is_failed(self):
        return self.failed

    @property
    def id(self):
        return self._id.hex

    def get_uuid(self):
        return self._id


class ProgressItem(BaseProgressItem):
    """ProgressItem will hold data needed to read out the progress work a WorkItem without having to interact with the work item itself

    Attributes:
        title: The title of the progress item.
        icon: The icon path for the progress item.
    """

    def __init__(
        self, title: Optional[str] = None, icon_path: Optional[str] = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.title = title
        self.icon = icon_path


class WorkItem:
    """WorkItem will hold a single function and its dependency's in order to allow organized parallel execution via the Controler class.
    the WorkItem can have an optional ProgressItem attached to it if progress should be reported

    Attributes:
        func: Callable[..., Any] = this will be the function that gets executed
        args: = func() arguments
        kwargs: = func() kwargs
        progress: Optional[ProgressItem] = optional progress object to report back to.
        dependenct_id: optional list off ids from a different work item that this work item depends on.
    """

    def __init__(
        self,
        func: Callable[[Union[BaseProgressItem, ProgressItem], Any], Any],
        args: Optional[List[Any]] = [],
        kwargs: dict = {},
        progress_item_instance: Union[
            BaseProgressItem, ProgressItem
        ] = BaseProgressItem(),
        dependency_id: Optional[List[uuid.UUID]] = None,
    ):

        self._id = uuid.uuid4()
        self.dependency_id = dependency_id
        self._progress_item = progress_item_instance
        self._func = func
        self._args = args
        self._kwargs = kwargs

    @property
    def id(self):
        return self._id.hex

    def get_uuid(self):
        return self._id

    def get_progress_item(self):
        return self._progress_item

    def start(self):
        self._progress_item.started = True
        try:
            self._func(self._progress_item, *self._args, **self._kwargs)
        except BaseException:
            self._progress_item.failed = True
            return

        self._progress_item.finished = True


class Controller:

    def __init__(self):

        self._work_items_by_id_hex: Dict[str, WorkItem] = {}
        self._progress_items_by_work_item_id_hex: Dict[
            str, Union[BaseProgressItem, ProgressItem]
        ] = {}

        self._threads_by_work_item_id: Dict[str, threading.Thread] = {}
        self._dependent_items_by_id: Set[str] = set()
        self._work_started: bool = False
        self._work_finished: bool = False
        self._main_thread = threading.Thread

    def get_progress_items(self):
        """returns a list off progress items that can be read out in order to get the progress per object

        Yields: List[ProgressItem or BaseProgressItem]

        """
        yield from self._progress_items_by_work_item_id_hex.items()

    @property
    def work_finished(self):
        return self._work_finished

    # TODO find a better name for this
    def construct_work_item(
        self,
        func: Callable[[Any], Any],
        args: Optional[List[Any]] = [],
        kwargs: Optional[Dict[Any, Any]] = {},
        dependency_id=None,
        icon_path: Optional[str] = None,
        progress_title: Optional[str] = None,
    ):
        if icon_path or progress_title:
            progress_item = ProgressItem(title=progress_title, icon_path=icon_path)
        else:
            progress_item = BaseProgressItem()

        item = WorkItem(
            func=func,
            args=args,
            kwargs=kwargs,
            progress_item_instance=progress_item,
            dependency_id=dependency_id,
        )

        self._work_items_by_id_hex[item.id] = item
        self._progress_items_by_work_item_id_hex[item.id] = progress_item

    def add_work_item(self, work_item_instance: WorkItem):
        self._work_items_by_id_hex[work_item_instance.id] = work_item_instance

        self._progress_items_by_work_item_id_hex[work_item_instance.id] = (
            work_item_instance.get_progress_item()
        )

    def _can_item_be_run(self, work_item_id_hex: str) -> bool:
        """this function checks if an work_item has a dependency's that has not finished running"""

        if work_item_id_hex in self._threads_by_work_item_id:
            return False

        work_item_instance = self._work_items_by_id_hex[work_item_id_hex]
        if work_item_instance.dependency_id == None:
            return True

        for dependent_item_id in work_item_instance.dependency_id:
            if self._progress_items_by_work_item_id_hex[dependent_item_id.hex].finished:
                return True

        return False

    def _start_main_loop(self):
        """this function will start all work items in order and wait with starting work items that have dependency's"""
        work_items_waiting_for_start = list(
            self._work_items_by_id_hex.values()
        )  # TODO not sure if this is more than we need. we could compare the id in self._threads_by_work_item_id to see if the work item is running

        self._work_started = True  # TODO in theory this should be more like request work work start emitted because we don't really know whats going on at this point in time
        self._work_finished = False  # TODO is this needed ? the default is False

        while len(work_items_waiting_for_start) > 0:
            for work_item in work_items_waiting_for_start:
                if self._can_item_be_run(work_item.id):
                    thread = threading.Thread(target=work_item.start)
                    self._threads_by_work_item_id[work_item.id] = thread
                    thread.start()
                    work_items_waiting_for_start.remove(work_item)
                    # self._start_thread(item)
            time.sleep(0.1)

        while not self._work_finished:
            thread_alive = False
            for thread in self._threads_by_work_item_id.values():
                if thread.is_alive():
                    thread_alive = True
            time.sleep(0.1)
            if not thread_alive:
                self._work_finished = True
                break

    def start(self):
        """this function is used to start execution off all work items.
        the _start_main_loop function is called to a different thread so this function will not block further execution
        """
        self._main_thread = threading.Thread(target=self._start_main_loop)
        self._main_thread.start()

    def is_running(self):
        if self._work_started and not self._work_finished:
            return True
        return False

    # def _start_thread(self, work_item: WorkItem):
    #     """this function start a thread and appends the thread to the self._threads_by_work_item_id dict.
    #     this function dose not run any tests
    #
    #     Args:
    #         work_item:
    #     """
    #     thread = threading.Thread(target=work_item.start)
    #     thread.start()
    #     self._threads_by_work_item_id[work_item.id] = thread

import threading
from typing import Callable, Any, List, Dict, Optional
from dataclasses import dataclass, field 
import random
import time


def ayon_work_item_excample_func(progress_callback:Callable[[int], None], finished_callback:Callable[[], None], *args, **kargs):
    for i in range(101):
        # print(f" i finished {i}% off the work \n the args are: {args} and the kargs are: {kargs}")
        time.sleep(random.uniform(0.01,0.1))
        # time.sleep(0.01)
        progress_callback(i)
    finished_callback()

class AyonThread(threading.Thread):
    def __init__(self, finished_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.finished_callback = finished_callback

    def run(self):
        super().run()
        self.finished_callback()


@dataclass 
class AyonWorkItem:
    name: str
    func: Callable[..., Any] # TODO this needs to enforce the option to define a progress_callback and a finished_callback because the work_hanlder will place a progress and finish callback into slot 0 and 1
    args: List[Any] 
    kargs: Dict[str, Any]

    additional_progress_callback: Optional[Callable[[int], None]] = None

    additional_finish_callback: Optional[Callable[[], None]] = None

    progress: int = 0
    progress_started: bool = False
    progress_finished: bool = False
    progress_text_info: Optional[str] = None

    print_log: bool = False


    def __init__(self) -> None:
        pass

    def set_progress(self, current_progress:int) -> None:
        self.progress = current_progress
        if self.additional_progress_callback:
            try: 
                self.additional_progress_callback(self.progress)
            except Exception:
                if self.print_log:
                    print("callback func not available")

    def set_progress_text_info(self, text_info:str) -> None:
        self.progress_text_info = text_info

    def set_finished(self) -> None:
        self.progress_finished = True
        if self.additional_finish_callback:
            try:
                self.additional_finish_callback()
            except Exception:
                if self.print_log:
                    print("finish callback func not available")


    def run(self):
        self.func(self.set_progress, self.set_finished, *self.args, **self.kargs)



@dataclass
class AyonWorkItemHandler:
    work_item_dict: Dict[str, AyonWorkItem] = field(default_factory=dict)
    started: bool = False
    finished_work: bool = False

    def add_func(self, func_in: Callable[[], Any], args: List[Any], kargs: Dict[str, Any], work_item_name: str, progress_overwrite:int=0) -> None:
        new_work_item = AyonWorkItem()

        new_work_item.name=work_item_name
        new_work_item.func=func_in
        new_work_item.args=args
        new_work_item.kargs=kargs
        new_work_item.progress=progress_overwrite

        self.work_item_dict[work_item_name] = new_work_item

    def add_work_item(self, work_item_in:AyonWorkItem) -> None:
        self.work_item_dict[work_item_in.name] = work_item_in 

    def get_progress(self) -> Dict[str, int]:
        progress_view = dict()
        for work_item in self.work_item_dict.values():
            progress_view[work_item.name] = work_item.progress

        return progress_view

    def get_progress_by_name(self, work_item_name:str) -> Optional[Dict[str, int]]:
        progress_view = dict()

        if not work_item_name:
            return None

        work_item = self.work_item_dict.get(work_item_name)
        
        if not work_item:
            return None

        progress_view[work_item.name] = work_item.progress
        return progress_view

    def run(self, finished_callback:Optional[Callable[[], None]], current_serial_item:Optional[Callable[[int], None]]):

        for index, work_item in enumerate(self.work_item_dict.values()):
            work_item.run()
            if current_serial_item:
                current_serial_item(index)

        if finished_callback:
            finished_callback()


@dataclass
class AyonWorkHandlerData:
    work_hanlder_instance: AyonWorkItemHandler

    started: bool = False
    finished: bool = False
    current_serial_item: int = 0

    def __init__(self) -> None:
        pass

    def current_serial_item_callback(self, progress: int):
        self.progress = progress

    def finished_callback(self):
        self.finished = True

    def started_callback(self):
        self.started = True

class AyonWorkQue:
    work_handler_list: List[AyonWorkHandlerData] = list()
    finish_event = threading.Event()
    started_threads = list()

    threads_running = int = 0

    def __init__(self) -> None:
        pass

    def add_work_handler(self, work_hanlder:AyonWorkItemHandler):
        new_work_hanlder_data = AyonWorkHandlerData()
        new_work_hanlder_data.work_hanlder_instance = work_hanlder
        self.work_handler_list.append(new_work_hanlder_data)

    def start_workitem_handler(self):
        pass

    def get_workitem_handler_progress(self):
        pass

    def get_progess(self):
        # this runction will return what work hanlder are running and there progress 
        # it will alos run a sub list off all items in the work handler and there progress

        # can i find an index in an list by the giving the function a whorhalnder instance ? 
        pass

    def start_work_handler(self):
        # start an individual work hanlder
        pass

    def is_running(self):
        return

    def decrease_running_threads(self):
        self.threads_running = self.threads_running - 1

    def wait_for_all_thread_to_finish_and_call_callback(self):
        while self.threads_running > 0: 
            time.sleep(0.1)

    def start_all(self, optional_finish_callback: Optional[Callable[[], None]] = None) -> List[threading.Thread]:

        for handler in self.work_handler_list:
            # TODO the thread needs to remove him self from the list
            self.threads_running = self.threads_running + 1
            thread = AyonThread(finished_callback=self.decrease_running_threads, target=handler.work_hanlder_instance.run, args=(handler.finished_callback,handler.current_serial_item_callback))
            self.started_threads.append(thread)
            thread.start()

        if optional_finish_callback:
            watcher_thread = AyonThread(finished_callback=optional_finish_callback, target=self.wait_for_all_thread_to_finish_and_call_callback)
            watcher_thread.start()

        return self.started_threads 
  


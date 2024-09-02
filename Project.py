from ayon_automator.AyonCiCd import Project

AyonBinDistroPrj = Project.Project("AyonBinDistro")

AyonBinDistroPrj.add_pip_package("black")
AyonBinDistroPrj.add_pip_package("QtPy")
AyonBinDistroPrj.add_pip_package("PyQt5")
AyonBinDistroPrj.add_pip_package("lakefs")
AyonBinDistroPrj.add_pip_package("lakefs-sdk")

AyonBinDistroPrj.setup()

from test import tests_ui, tests_worker
from test import test_object_infos
from test import test_lake_fs_wrapper

test_without_icon = Project.Stage("test_without_icon")
test_without_icon.add_funcs(tests_ui.test_with_fake_data_no_icon)
AyonBinDistroPrj.add_stage(test_without_icon)

test_with_icon = Project.Stage("test_with_icon")
test_with_icon.add_funcs(tests_ui.test_ui_with_fake_data_with_icon)
AyonBinDistroPrj.add_stage(test_with_icon)

test_no_delet = Project.Stage("test_no_delet")
test_no_delet.add_funcs(tests_ui.test_no_delet)
AyonBinDistroPrj.add_stage(test_no_delet)

test_worker_with_progress_title = Project.Stage("test_worker_with_progress_title")
test_worker_with_progress_title.add_funcs(
    tests_worker.test_with_fake_data_with_progess_titile
)
AyonBinDistroPrj.add_stage(test_worker_with_progress_title)

test_without_progess_titile = Project.Stage("test_worker_with_progress_title")
test_without_progess_titile.add_funcs(
    tests_worker.test_with_fake_data_without_progess_titile
)
AyonBinDistroPrj.add_stage(test_without_progess_titile)

test_get_object_metadata_stage = Project.Stage("test_get_object_metadata")
test_get_object_metadata_stage.add_funcs(test_object_infos.test_get_object_metadata)
AyonBinDistroPrj.add_stage(test_get_object_metadata_stage)

test_lake_fs_wrapper_stage = Project.Stage("test_lake_fs_wrapper")
test_lake_fs_wrapper_stage.add_funcs(test_lake_fs_wrapper.test_help, test_lake_fs_wrapper.test_get_object_metadata,test_lake_fs_wrapper.test_clone_local ,test_lake_fs_wrapper.test_list_repo_objects, test_lake_fs_wrapper.test_clone_elemente, test_lake_fs_wrapper.test_commit_local)
AyonBinDistroPrj.add_stage(test_lake_fs_wrapper_stage)

AyonBinDistroPrj.creat_stage_group(
    "test_worker_all", test_worker_with_progress_title, test_without_progess_titile
)

with AyonBinDistroPrj as PRJ:
    PRJ.make_project_cli_available()

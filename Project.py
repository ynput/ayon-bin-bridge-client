from ayon_automator.AyonCiCd import Project


AyonBinDistroPrj = Project.Project("AyonBinDistro")

AyonBinDistroPrj.add_pip_package("black")
AyonBinDistroPrj.add_pip_package("QtPy")
AyonBinDistroPrj.add_pip_package("PyQt5")
AyonBinDistroPrj.add_pip_package("lakefs")
AyonBinDistroPrj.add_pip_package("lakefs-sdk")

AyonBinDistroPrj.setup_prj()

from test import tests_ui, tests_worker, test_lake_fs_wrapper, test_object_infos

test_without_icon = Project.Stage("test_without_icon")
test_without_icon.add_funcs(
    Project.Func(
        "Test Ui no icon",
        tests_ui.test_with_fake_data_no_icon,
    ),
)
AyonBinDistroPrj.add_stage(test_without_icon)

test_with_icon = Project.Stage("test_with_icon")
test_with_icon.add_funcs(
    Project.Func(
        "test Ui with icon",
        tests_ui.test_ui_with_fake_data_with_icon,
    ),
)
AyonBinDistroPrj.add_stage(test_with_icon)

test_no_delet = Project.Stage("test_no_delet")
test_no_delet.add_funcs(
    Project.Func(
        "",
        tests_ui.test_no_delet,
    ),
)
AyonBinDistroPrj.add_stage(test_no_delet)

test_worker_with_progress_title = Project.Stage("test_worker_with_progress_title")
test_worker_with_progress_title.add_funcs(
    Project.Func(
        "Worker Testing with Progress Title",
        tests_worker.test_with_fake_data_with_progess_titile,
    ),
)
AyonBinDistroPrj.add_stage(test_worker_with_progress_title)

test_without_progess_titile = Project.Stage("test_worker_with_progress_title")
test_without_progess_titile.add_funcs(
    Project.Func(
        "Worker Testing without Progress Title",
        tests_worker.test_with_fake_data_without_progess_titile,
    ),
)
AyonBinDistroPrj.add_stage(test_without_progess_titile)

test_get_object_metadata_stage = Project.Stage("test_get_object_metadata")
test_get_object_metadata_stage.add_funcs(
    Project.Func(
        "Testing Object Metadata",
        test_object_infos.test_get_object_metadata,
    ),
)
AyonBinDistroPrj.add_stage(test_get_object_metadata_stage)

test_lake_fs_wrapper_stage = Project.Stage("test_lake_fs_wrapper")
test_lake_fs_wrapper_stage.add_funcs(
    Project.Func(
        "Start LakeFs Wrapper help",
        test_lake_fs_wrapper.test_help,
    ),
    Project.Func(
        "Start LakeFs Wrapper get metadata",
        test_lake_fs_wrapper.test_get_object_metadata,
    ),
    Project.Func(
        "Start LakeFs Wrapper clone local",
        test_lake_fs_wrapper.test_clone_local,
    ),
    Project.Func(
        "Start LakeFs Wrapper list objects",
        test_lake_fs_wrapper.test_list_repo_objects,
    ),
    Project.Func(
        "Start LakeFs Wrapper clone element",
        test_lake_fs_wrapper.test_clone_elemente,
    ),
    Project.Func(
        "Start LakeFs Wrapper commit local",
        test_lake_fs_wrapper.test_commit_local,
    ),
)
AyonBinDistroPrj.add_stage(test_lake_fs_wrapper_stage)

AyonBinDistroPrj.creat_stage_group(
    "test_worker_all", test_worker_with_progress_title, test_without_progess_titile
)

with AyonBinDistroPrj as PRJ:
    PRJ.make_project_cli_available()

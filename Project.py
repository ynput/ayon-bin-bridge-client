from ayon_cicd_tools.AyonCiCd import Project

AyonBinDistroPrj = Project.Project("AyonBinDistro")

AyonBinDistroPrj.add_pip_package("black")
AyonBinDistroPrj.add_pip_package("QtPy")
AyonBinDistroPrj.add_pip_package("lakefs")
AyonBinDistroPrj.add_pip_package("lakefs-sdk")


from test import tests_ui, tests_worker


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

AyonBinDistroPrj.creat_stage_group(
    "test_worker_all", test_worker_with_progress_title, test_without_progess_titile
)

with AyonBinDistroPrj as PRJ:
    PRJ.make_project_cli_available()

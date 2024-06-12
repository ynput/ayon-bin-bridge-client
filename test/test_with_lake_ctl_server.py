# import os
# import sys
# from PyQt5.QtWidgets import QApplication
#
# from ..work_handler import worker
# from ..gui import progress_ui
#
# from ayon_bin_distro.lakectlpy import wrapper
#
#
# def main():
#     icon_path = os.path.join(
#         os.path.abspath(os.curdir), "test", "ay-symbol-blackw-full.png"
#     )
#     ctl = wrapper.LakeCtl()
#     app = QApplication(sys.argv)
#     controller = worker.Controller()
#     ui = progress_ui.ProgressDialog(controller, False)
#
#     for i in range(1):
#         controller.construct_work_item(
#             func=ctl.clone_local,
#             kwargs={
#                 "repo_branch_uri": "lakefs://ayon-usd/main/",
#                 "dist_path": f"/home/lyonh/ynput/DevEnv/projects/AyonBinBridgeClient/AyonBinBridge-Client/dell/down_b{i}",
#                 "exists_okay": True,
#             },
#             progress_title="Usd_Clone",
#         )
#         controller.construct_work_item(
#             func=ctl.clone_element,
#             args=[
#                 "lakefs://ayon-usd/main/AyonUsdResolverBin/AyonUsd/ayon-usd-resolver_usd23.5_linux_py39.zip",
#                 f"/home/lyonh/ynput/DevEnv/projects/AyonBinBridgeClient/AyonBinBridge-Client/dell/",
#             ],
#             # kwargs={
#             #     "lake_fs_object_uir": "lakefs://ayon-usd/main/AyonUsdResolverBin/AyonUsd/ayon-usd-resolver_usd23.5_linux_py39.zip",
#             #     "dist_path": f"/home/lyonh/ynput/DevEnv/projects/AyonBinBridgeClient/AyonBinBridge-Client/dell/",
#             # },
#             progress_title="Element_Clone",
#         )
#
#     ui.start()
#     sys.exit(app.exec_())

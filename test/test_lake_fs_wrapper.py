from datetime import datetime
import shutil
import sys
from ayon_bin_distro.lakectlpy import wrapper
from ayon_cicd_tools.AyonCiCd import helpers
import os


access_key_id=input("lakeFs access_key_id: ") 
secret_access_key=input("lakeFs secret_access_key: ")

ctl = wrapper.LakeCtl(base_uri_oberwrite="https://lake.ayon.cloud", )

test_object_on_the_repo = "15-44-17.png"
lake_fs_prj = "lakefs://lake-fs-cicd-test-prj/main/"
lake_fs_object = "lakefs://lake-fs-cicd-test-prj/main/Screenshot from 2024-03-17 15-44-17.png"


temp_dir = os.path.join(os.path.dirname(__file__),"temp")

def test_help():
    ctl.help()

def test_list_repo_objects():
    repo_list = ctl.list_repo_objects(lake_fs_prj)
    print(repo_list)
    if not test_object_on_the_repo in repo_list:
        helpers.FAIL(f"did not list file {test_object_on_the_repo} <- this is a test object uploaded to the lake fs test repo")
    print()

def test_clone_local():
    dist_path = os.path.join(temp_dir, "repo_clone")
    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)
    os.makedirs(dist_path, exist_ok=True)

    path = ctl.clone_local(progress_obj=None, repo_branch_uri=lake_fs_prj, dist_path=dist_path, print_stdout=True)

    if not os.path.exists(dist_path):
        helpers.FAIL("File dose not exist in its destination")
    shutil.rmtree(dist_path)
    print("output_path:", path)

def test_get_object_metadata():
    t = ctl.get_element_info(lake_fs_object)

    print("object_metadata:", t)

    if not t.get("Checksum") == "94e1d72a850647cdeae88eafbb821916":
        helpers.FAIL(f"Wrong Checksum for object {test_object_on_the_repo}")

def test_clone_elemente():
    dist_path = os.path.join(temp_dir, "element_clone")
    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)
    os.makedirs(dist_path, exist_ok=True)

    element = ctl.clone_element(progress_obj=None,lake_fs_object_uir=lake_fs_object ,dist_path=dist_path)
    
    if not os.path.exists(element):
        helpers.FAIL("File dose not exist in its destination")
    shutil.rmtree(dist_path)
    print("element pos:", element)

def test_commit_local():
    repo_path = os.path.join(temp_dir, "commit_local_repo_temp")
    os.makedirs(repo_path)
    ctl.clone_local(None, lake_fs_prj, repo_path)
    
    with open(os.path.join(repo_path, "runs.txt"), "a") as runsfile:
        runsfile.write(f"new_run at: {datetime.utcnow()} \n")

    ctl.commit_local(f"ci cd test run at: {datetime.utcnow()}", repo_path)
    shutil.rmtree(repo_path)

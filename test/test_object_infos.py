from ayon_bin_distro.lakectlpy import wrapper


def test_get_object_metadata():
    ctl = wrapper.LakeCtl()
    t = ctl.get_element_info(
        "lakefs://ayon-usd/pinning-suport/AyonUsdResolverBin/Hou/ayon-usd-resolver_hou19.5_linux_py37.zip"
    )
    print(t)
    print("timeStamp: ", t.get("Modified Time"))

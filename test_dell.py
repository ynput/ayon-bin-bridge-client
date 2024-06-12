from test import testA, testB


# list off packages lakefs

testB.main()
# lake_ctl_test_dell.main()


# from lakectlpy import wrapper
# #
# ctlB = wrapper.LakeCtl()
#
# print(ctlB.help())

# import lakefs
# from lakefs.client import Client

# clt = Client(username="AKIAIOSFOLKFSSAMPLES", password="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", host="http://127.0.0.1:58000")
# repo = lakefs.Repository(repository_id="ayon-usd", client=clt)

# ref = repo.ref("main")
#
# for i in ref.objects():
#     g = i.path.split("/")
#     if "AyonUsdBin" in g:
#         print(i.path)

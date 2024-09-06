# ayon_bin_distro.lakectlpy: LakeCtl python wrapper

The `lakectlpy` module is a simple wrapper around select functions of the [LakeCtl](https://docs.lakefs.io/reference/cli.html) command-line tool. \n
This Python wrapper enables easy interactions within an Ayon-Addon. 
Although it currently uses LakeCtl directly, future iterations might switch to using the [`lakepy`](https://pypi.org/project/lakepy/) library while maintaining compatible function signatures.

The `LakeCtl` class in this module exposes many of the functions provided by the CLI version of LakeCtl.The lakectlpy modules is a Simple wrapper around a few selected functions of the
[LakeCtl](https://docs.lakefs.io/reference/cli.html).

We wrapped this tool into a python module to allow for easy interactions from within an Ayon-Addon. \n 
in later iterations this might be rewritten to be based on the [lakepy](https://pypi.org/project/lakepy/) modules instead, but the module
function signatures will stay the same.

There is only really one important class in lakectlpy

`LakeCtl` in the wrapper module\n it exposes many of the functions that the CLI
version of the lakectl provides.





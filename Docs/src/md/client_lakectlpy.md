# ayon_bin_distro.lakectlpy: lakeCtl python wrapper

The lakectlpy modules is a Simple wrapper around a few selected functions of the
[LakeCtl](https://docs.lakefs.io/reference/cli.html).

We wrapped this tool into a python module to allow for easy interactions from
within an Ayon-Addon. in later iterations this might be rewritten to be based on
the [lakepy](https://pypi.org/project/lakepy/) modules instead but the module
function signatures will stay the same.

There is only really one important class in lakectlpy

`LakeCtl` in the wrapper module\n it exposes many of the functions that the Cli
version of the lakectl provides.

# Getting Started

This repository is intended as a library, designed to facilitate interaction with LakeFS.

We commonly use vendor code and submodules for this purpose; however, if feasible, 
you can also install it via pip against GitHub, though extensive testing has not been conducted yet. 
Primarily, your interactions with this tool set will revolve around processing binary or larger data files.

## General Concepts

**Key Concepts to Understand Early:**

- **Work Handling:** This core principle revolves around individual tasks such as function calls and similar operations, 
which often run concurrently or are dependent on each other. 
Consequently, we typically utilize a work queue provided by our WorkHandler module.

- **LakeFS Wrapper:** This is simply an abstraction layer over lakectl to facilitate interaction with LakeFS repositories.
It's recommended to familiarize oneself with the [LakeFS Documentation](https://docs.lakefs.io/) beforehand.

- **Progress Displays:** Many tools in this repository can provide progress updates, which are handled internally. 
For most straightforward usage, connect a GUI from the gui module with a controller from the work_handler module; further details can be found on their respective pages.

## Modules

The bin bridge client is divided into four modules, each with its own dedicated documentation for more information:

### GUI
The GUI module provides classes to display progress and status of work handler items to users.

### LakeCtlPy
The LakeCtlPy module serves as a simple wrapper around select functions of the [LakeCtl](https://docs.lakefs.io/reference/cli.html), facilitating Python interaction with LakeCtl.

### Utilities (Util)
This module contains helper functions for working with data that may need to be uploaded or downloaded from LakeFS.

### Work Handler
The work handler system enables distributed tasks with dependencies, ensuring they run in the correct order across your system.

[Examples](md_md_Examples.html)

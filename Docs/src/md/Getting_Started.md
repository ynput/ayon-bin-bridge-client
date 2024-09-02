# Getting Started

This repository is designed to be used as a library. to aid you by interacting
with LakeFs

we often vendor this code and use submodules to do so. If possible for you you
should also be able to install it using the pip install method's against github
this has no extensive testing yet.

in most cases your interaction with this tool set will center around processing
binary or generally larger data.

## General Concepts

the most important things to grasp early or are:

**work handling** This fundamental concept is that individual tasks, such as
function calls and similar operations, often either run concurrently in parallel
or are dependent on each other. As a result, most of the time we employ a work
queue provided by our WorkHandler module.

**The lakeFs Wrapper** this is simply a wrapper around the lakectl, it makes it
easy to interact with a given LakeFs reposetroy. i advice to read the
[LakeFs Docs](https://docs.lakefs.io/) before using it

**Progress Displays** many of the tools in this repo can report back there
progress. This is handles internally and in most cases it will be most straight
forward if you just use the options to connect a GUI from the gui module with a
controller from the work_hanlder module a bit more on that in there individual
pages.

## Modules

The bin bridge client is broken into 4 modules. They all have an dedicated site
with more information about them

### gui

The GUI module exposes classes that allow you to show progress and state of work
handler items to a user

### lakectlpy

The lakectlpy modules is a Simple wrapper around a few selected functions of the
[LakeCtl](https://docs.lakefs.io/reference/cli.html). it makes it easy to
interact with LakeCtl from python

### util

Holds some functions to aid the interaction with data that you might want to up
and download from LakeFs.

### work_hanlder

System to create distrusted tasks with dependency's that run in order across
your system

[Examples](md_md_Examples.html)

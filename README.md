# TealPkg

TealPkg: Package management frontend for [Slackware Linux](http://www.slackware.com)


## About this Code

During the summer of 2021, we completed a feasibility analysis of Slackware Linux as a potential distribution
for use on HPC nodes, servers, and laboratory workstations. The intent of the study was to determine whether
or not a small team of people could maintain a software stack for approximately 100 systems, while having
complete control of each system. The lack of [systemd](https://systemd.io/) was a major factor in choosing to
evaluate Slackware, since systemd had proven to be a consistent pain point.

Although Slackware was not found to be feasible for an HPC system, it was later determined to be useful
for laboratory machines and as a base operating system for other research and development projects. During the
original study in 2021, I wrote the TealPkg package management frontend using Python 3. After about a year on
the back burner, and a few adventures into shell scripting and Awk, I decided to revive the application in
2022, focusing on desktop and appliance systems.


## Features

1. Hardened GPG checking. Key fingerprints and official key distribution channels are used to ensure that
   received packages are authentic.
2. Support for tagfiles. Multiple systems can be installed with the same software stack using these files.
3. Script support. Example post-transaction scripts are provided for mkinitrd, LILO, and GRUB.
4. Repository rollback protection.
5. Stale repository detection (for use with Slackware(64)-current).
6. Multiple repositories are supported, with a total ordering of priorities for package selection.
7. Yum/DNF-like interface with automatic metadata management.
8. Transaction protection in the event of a SIGHUP.


## CLI

tealpkg [options] command [args]

* check-update
* clean {all | metadata | packages}
* info [--available | --extras | --install | --upgrades]  [package ...]
* install {package} [...]
* list [--available | --extras | --install | --upgrades]  [package ...]
* provides {file} [...]
* remove {package} [...]
* repolist [--enabled | --disabled | --all]
* search {query}
* sync [package ...]

Aliases:

* update --> sync
* upgrade --> sync
* whatprovides --> provides


### Options

* -c --config   : specifies an alternate configuration file
* -d --debug    : sets log level to DEBUG
* -D --dry-run  : doesn't actually install, remove, or update packages
* -i --include  : includes a previously excluded package
* -q --quiet    : suppresses all standard output (implies -y)
* -x --exclude  : excludes a package from consideration
* -y --yes      : skip all confirmation prompts (implied with -q)
* --enablerepo  : enables disabled repositories (comma-separated or '\*' for all)
* --disablerepo : disables enabled repositories (comma-separated or '\*' for all)
* --refresh     : expires all metadata, forcing a refresh
* --version     : displays current TealPkg version

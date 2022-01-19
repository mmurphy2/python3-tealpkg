# TealPkg

TealPkg: Package management frontend for [Slackware Linux](http://www.slackware.com)

It isn't quite dead :).


## About this Code

During the summer of 2021, we completed a feasibility analysis of Slackware Linux as a potential distribution for use
on HPC nodes, servers, and laboratory workstations. The intent of the study was to determine whether or not a small team
of people could maintain a software stack for approximately 100 systems, while having complete control of each system.
The lack of [systemd](https://systemd.io/) was a major factor in choosing to evaluate Slackware, since systemd has proven
to be a pain point in our existing CentOS 7 infrastructure. A highly cohesive, loosely coupled init system (such as the
one found in Slackware) is desirable.

Unfortunately, the need to maintain a significant number of additional packages beyond those included with the
distribution proved to be a much larger pain point than the init system. With hundreds of users with various software
requests, the coverage of the official repositories was simply too small to be able to meet our needs by itself. Various
add-on repositories are available for this distribution, along with a comprehensive set of build scripts available at
[SlackBuilds.org](https://slackbuilds.org). However, the lack of standardization of package names within even this one
repository was a major impediment to building the required software stack from source.

During the course of the study, I wrote the TealPkg package management frontend after determining that the existing
Slackpkg and Slackpkg+ tools did not meet our requirements. After my experience with the TealBuild system (also available
here in GitHub), I determined that Bash was **not** the language to use for this tool. I therefore used Python 3,
limiting the use of add-on packages to those which were available in the official repositories for Slackware -current at
the time (15.0).

TealPkg was approaching feature parity with Slackpkg as of the time of the end of the 2021 study. In addition, it was
written with several additional major features:

1. Logging was partially implemented, with the objective of having complete transaction logs.
2. GPG checks were significantly hardened compared to Slackpkg, with key fingerprints and official public key
   distribution channels used to verify that the correct keys were obtained for each repository.
3. For anticipated (at the time) future software set customizations, TealPkg was designed to read and write standard
   Slackware tagfiles to make it easy to deploy this distribution across multiple systems.
4. Post-transaction script support was integrated, with example scripts provided for LILO and GRUB.

Although ensuring that TealPkg could replace Slackpkg was a design objective, the code for TealPkg is clean sheet and does
not build upon Slackpkg (which is written in shell script anyway). The CLI for TealPkg also follows that of Yum/DNF, since
the software was created with the intent of supporting refugees from CentOS after the CentOS Stream announcement.

In early 2022, I found another use case for the Slackware distribution as a desktop OS. On the desktop, the software stack
can be supplemented with Flatpak packages in a manner similar to the approach taken by the KDE Neon distribution. Accordingly,
development of TealPkg has resumed, at least slowly.


## Original Description

TealPkg is a yum-like tool for Slackware Linux, with an important caveat: an "upgrade" may be a downgrade, since
TealPkg is designed to keep the local system in sync with the versions of software available in remote repositories.
In the same fashion as yum with the priorities plugin, repositories configured for use with TealPkg all have priority
numbers, and packages in higher priority (lower-numbered) repositories mask packages of the same name in lower
priority (higher-numbered) repositories.

As of 0.8.0, TealPkg includes transaction protection in case of a disconnected SSH session (SIGHUP).


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


## Multilib

Enabling:

1. Enable the alienbob-multilib.ini file
2. tealpkg sync
3. tealpkg install compat32-tools
4. tealpkg install \*-compat32
5. Reboot to migrate onto the new glibc

Reversing multilib:

1. tealpkg remove \*-compat32
2. tealpkg remove compat32-tools
3. Disable to remove the alienbob-multilib.ini file
4. tealpkg sync
5. Reboot to migrate onto the new glibc

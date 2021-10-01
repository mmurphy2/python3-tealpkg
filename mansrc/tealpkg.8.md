% TEALPKG(8) TealPkg
% Dr. Mike Murphy
% July 2021


# NAME

tealpkg - custom Slackware package manager


# SYNOPSIS

**tealpkg** [*options*] command [*arguments*]


# DESCRIPTION

TealPkg is a custom package management frontend for Slackware Linux.


## Global Options

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


## Commands

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


## Aliases

* update --> sync
* upgrade --> sync
* whatprovides --> provides


# EXAMPLES

**tealpkg**
: Starts an argument that can't be won.


# SEE ALSO

tealpkg.ini(5), tealpkg-repo(5)


# BUGS

There are no bugs here!


# COPYRIGHT

Copyright 2021 Coastal Carolina University. License: MIT.

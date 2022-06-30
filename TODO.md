# TODO

- Fix metadata change detection
- Add ChangeLog support
- Add a --download-only option (in addition to the dry run) - might be better to have a download command, instead
- Add an option or docs to install new packages from official repos (for full installs)
- Per-repository masking
- Add a flag to disable running scripts at the end
- Add options for handling .new files
- Ensure that each type of cprint has a unique style
- Tweak colors
- Parse the MANIFEST and PACKAGES files directly into a SQLite DB, instead of the current pickling approach, so
  that searches can be done as faster SQL queries (alternatively, use a filesystem-based hierarchy of metadata)
- Integrate Flatpak support for desktop convenience
- Add port/build system for building packages from SlackBuilds (rewrite and add TealBuild, perhaps as a separate
  command)


## Potential Additional Features

- Handling for package renames within a repository (see if the metadata are already in /var/lib/pkgtools/packages)
- Add backup/history capabilities
- Add a TUI for interactive mode (if designed correctly, a GUI should also be possible)

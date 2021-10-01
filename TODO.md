# Original TODO

Please note that this project has been abandoned. The following items were on the TODO list at the end of the project.
These are left as exercises for anyone who would like to fork the code (MIT licensed).

- Add ChangeLog support
- Add a --download-only option (in addition to the dry run) - might be better to have a download command, instead
- Handling for package renames within a repository (see if the metadata are already in /var/lib/pkgtools/packages)
- Add an option or docs to install new packages from official repos (for full installs)
- Per-repository masking
- Add a flag to disable running scripts at the end
- Add options for handling .new files
- Add backup/history capabilities
- Ensure that each type of cprint has a unique style
- Tweak colors
- Add a TUI for interactive mode (if designed correctly, a GUI should also be possible)
- Parse the MANIFEST and PACKAGES files directly into a SQLite DB, instead of the current pickling approach, so
  that searches can be done as faster SQL queries

# ConanExiles-OrphanCleaner

A cleanup tool for Conan Exiles mod developers. Scans your mod folder and removes orphaned `.uasset` stubs left behind by UE4 when assets are deleted from a project.

---

## The Problem

When you delete an asset in UE4 (the Conan Exiles DevKit), the engine does not always fully clean up after itself. It leaves behind tiny stub `.uasset` files — typically under 1KB — that contain no real asset data. These orphaned stubs can cause **"Missing cooked file"** errors when packaging or running your mod.

## How It Works

Rather than relying on file size alone, this tool inspects the binary header of every `.uasset` file in your mod folder. A real asset always references `/Script/Engine` in its name table. An orphaned stub never does. This makes detection reliable regardless of file size.

A file is flagged as an orphaned stub if it:
- Has a valid UE4 package magic header (`0x9E2A83C1`)
- Contains `PackageMetaData`
- Does **not** contain `/Script/Engine`

---

## Requirements

- Python 3.x
- Conan Exiles DevKit (UE4)

---

## Usage

### Option 1 — Double-click
Run `!Start.cmd` to launch the tool directly.

### Option 2 — Command line
```
python orphan_cleaner.py
```

### Steps
1. Select **option 1** from the menu
2. Enter your mod folder path, e.g.:
   ```
   G:\ConanExilesDevKit\Games\ConanSandbox\Content\Mods\YourModName
   ```
   The path is saved automatically for future runs.
3. The tool scans all `.uasset` files and lists any orphaned stubs found
4. Choose to delete them all at once or individually

---

## Menu

```
1. Clean project - scan mod folder for orphaned stubs
2. Change mod folder
q. Quit
```

---

## Notes

- Your mod folder path is saved in `file_manager_config.json` next to the script
- A backup of the config is kept as `file_manager_config.json.backup`
- Deleted files are permanently removed — there is no recycle bin step

---

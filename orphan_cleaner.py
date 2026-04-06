#V0.1.0
import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Tuple, Any

UE4_MAGIC = bytes([0xC1, 0x83, 0x2A, 0x9E])

CONFIG_FILE = 'file_manager_config.json'
DEFAULT_CONFIG = {
    'mod_directory': '',
    'last_modified': ''
}


def load_config() -> Dict[str, Any]:
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
    except Exception as e:
        print(f"Error loading config: {e}")
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    try:
        if os.path.exists(CONFIG_FILE):
            shutil.copy2(CONFIG_FILE, CONFIG_FILE + '.backup')
        config['last_modified'] = datetime.now().isoformat()
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")


def format_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"


def get_path_with_default(prompt: str, default_value: str) -> str:
    if default_value:
        print(f"Saved path: {default_value}")
        if input("Use this path? (y/n): ").lower() == 'y':
            return default_value
    return input(prompt)


def is_orphaned_uasset(file_path: str) -> bool:
    """
    Returns True if the .uasset is an orphaned stub left behind after UE4 asset deletion.
    Orphaned stubs have a valid UE4 header and PackageMetaData but no /Script/Engine
    reference, meaning they contain no real asset data.
    """
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        return (
            data[:4] == UE4_MAGIC and
            b'PackageMetaData' in data and
            b'/Script/Engine' not in data
        )
    except OSError:
        return False


def scan_orphaned_files(mod_directory: str) -> List[Tuple[str, int]]:
    """Walk the mod directory and return all orphaned .uasset stubs."""
    orphaned = []
    total_scanned = 0

    print(f"\nScanning: {mod_directory}")
    print("Checking .uasset headers for orphaned stubs...")

    for root, _, files in os.walk(mod_directory):
        for filename in files:
            if not filename.lower().endswith('.uasset'):
                continue
            full_path = os.path.join(root, filename)
            total_scanned += 1
            if is_orphaned_uasset(full_path):
                orphaned.append((full_path, os.path.getsize(full_path)))

    print(f"Scanned {total_scanned} .uasset files, found {len(orphaned)} orphaned stub(s).")
    return orphaned


def delete_files(files: List[Tuple[str, int]]) -> Tuple[int, List[str]]:
    success = 0
    failed = []
    for file_path, _ in files:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
            success += 1
        except OSError as e:
            print(f"Error deleting {file_path}: {e}")
            failed.append(file_path)
    return success, failed


def main():
    config = load_config()

    while True:
        print("\nConan Exiles Mod File Manager By Sibercat V0.1.0")
        print("1. Clean project - scan mod folder for orphaned stubs")
        print("2. Change mod folder")
        print("q. Quit")

        choice = input("\nEnter your choice: ")

        if choice.lower() == 'q':
            break

        elif choice == '1':
            mod_dir = get_path_with_default(
                "Enter your mod folder path: ",
                config.get('mod_directory', '')
            )

            if not os.path.exists(mod_dir):
                print("Error: Directory does not exist.")
                continue

            if mod_dir != config.get('mod_directory'):
                config['mod_directory'] = mod_dir
                save_config(config)

            orphaned_files = scan_orphaned_files(mod_dir)

            if not orphaned_files:
                print("No orphaned stubs found. Your project is clean!")
                continue

            print("\nOrphaned stubs found:")
            for idx, (file_path, size) in enumerate(orphaned_files, 1):
                print(f"{idx}. {file_path}")
                print(f"   Size: {format_size(size)}")

            while orphaned_files:
                print(f"\nOptions:")
                print("1. Delete individual file (enter file number)")
                print(f"2. Delete all {len(orphaned_files)} orphaned stubs")
                print("q. Return to main menu")

                subchoice = input("Enter your choice: ")

                if subchoice.lower() == 'q':
                    break

                elif subchoice == '1':
                    try:
                        file_idx = int(input("Enter file number to delete: ")) - 1
                        if 0 <= file_idx < len(orphaned_files):
                            confirm = input(f"Delete '{orphaned_files[file_idx][0]}'? (y/n): ")
                            if confirm.lower() == 'y':
                                success, _ = delete_files([orphaned_files[file_idx]])
                                if success:
                                    orphaned_files.pop(file_idx)
                                    print(f"Remaining: {len(orphaned_files)}")
                        else:
                            print("Invalid file number.")
                    except ValueError:
                        print("Please enter a valid number.")

                elif subchoice == '2':
                    confirm = input(f"Delete all {len(orphaned_files)} orphaned stubs? (y/n): ")
                    if confirm.lower() == 'y':
                        success, failed = delete_files(orphaned_files)
                        print(f"\nDeleted {success} of {len(orphaned_files)} orphaned stubs.")
                        if failed:
                            print("Failed to delete:")
                            for fp in failed:
                                print(f"  - {fp}")
                        orphaned_files = [(f, s) for f, s in orphaned_files if os.path.exists(f)]

                else:
                    print("Invalid choice.")

        elif choice == '2':
            new_dir = input("Enter new mod folder path: ")
            if os.path.exists(new_dir):
                config['mod_directory'] = new_dir
                save_config(config)
                print("Mod folder updated.")
            else:
                print("Error: Directory does not exist.")

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()

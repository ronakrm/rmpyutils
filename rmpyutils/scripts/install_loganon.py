import argparse
import hashlib
import os
import shutil
import site
import sys


def get_file_checksum(filename):
    with open(filename, "rb") as f:
        file_hash = hashlib.md5()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)
    return file_hash.hexdigest()


def get_site_packages_dir():
    # Check if we're in a virtual environment
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        # We're in a virtual environment, use sys.prefix
        return os.path.join(
            sys.prefix,
            "lib",
            f"python{sys.version_info.major}.{sys.version_info.minor}",
            "site-packages",
        )
    else:
        # We're not in a virtual environment, use site.getusersitepackages()
        return site.getusersitepackages()


def install_sitecustomize():
    parser = argparse.ArgumentParser(description="Install sitecustomize.py")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force installation even if sitecustomize.py already exists",
    )
    args = parser.parse_args()

    force = args.force

    # Get the appropriate site-packages directory
    site_packages = get_site_packages_dir()

    # Ensure the directory exists
    os.makedirs(site_packages, exist_ok=True)

    # Check if sitecustomize.py already exists
    dest_path = os.path.join(site_packages, "sitecustomize.py")
    if os.path.exists(dest_path):
        if not force:
            print(f"Error: A sitecustomize.py file already exists at {dest_path}")
            print("Use --force to overwrite the existing file (use with caution).")
            return
        else:
            print(f"Warning: Overwriting existing sitecustomize.py at {dest_path}")

    # Copy sitecustomize.py to the site-packages
    source_path = os.path.join(os.path.dirname(__file__), "sitecustomize.py")
    shutil.copy(source_path, dest_path)

    # Calculate and store the checksum
    checksum = get_file_checksum(dest_path)
    with open(os.path.join(site_packages, "sitecustomize_checksum.txt"), "w") as f:
        f.write(checksum)

    print(f"sitecustomize.py has been installed to {site_packages}")
    print(
        "Your package will now be auto-imported in all Python executions within this environment."
    )


def uninstall_sitecustomize():
    site_packages = get_site_packages_dir()

    sitecustomize_path = os.path.join(site_packages, "sitecustomize.py")
    checksum_path = os.path.join(site_packages, "sitecustomize_checksum.txt")

    if not os.path.exists(sitecustomize_path):
        print("sitecustomize.py is not installed in this environment.")
        return

    if not os.path.exists(checksum_path):
        print(
            "Warning: Checksum file not found. Cannot verify sitecustomize.py integrity."
        )
        return

    # Read the stored checksum
    with open(checksum_path, "r") as f:
        stored_checksum = f.read().strip()

    # Calculate the current checksum
    current_checksum = get_file_checksum(sitecustomize_path)

    if current_checksum != stored_checksum:
        print("Error: The sitecustomize.py file has been modified since installation.")
        print("It may have been changed by another program or manually edited.")
        print("Please check the file contents before removing it manually.")
        return

    # If checksums match, proceed with removal
    os.remove(sitecustomize_path)
    os.remove(checksum_path)
    print(f"sitecustomize.py has been successfully uninstalled from {site_packages}.")

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


def install_sitecustomize(force=False):
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
    source_path = "sitecustomize.py"
    shutil.copy(source_path, dest_path)

    # Calculate and store the checksum
    checksum = get_file_checksum(dest_path)
    with open(os.path.join(site_packages, "sitecustomize_checksum.txt"), "w") as f:
        f.write(checksum)

    print(f"sitecustomize.py has been installed to {site_packages}")
    print(
        "Your package will now be auto-imported in all Python executions within this environment."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install sitecustomize.py")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force installation even if sitecustomize.py already exists",
    )
    args = parser.parse_args()

    install_sitecustomize(force=args.force)

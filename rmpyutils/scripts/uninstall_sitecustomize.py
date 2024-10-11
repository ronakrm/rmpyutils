import hashlib
import os
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
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        return os.path.join(
            sys.prefix,
            "lib",
            f"python{sys.version_info.major}.{sys.version_info.minor}",
            "site-packages",
        )
    else:
        return site.getusersitepackages()


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


if __name__ == "__main__":
    uninstall_sitecustomize()

import os
import sys
from urllib import request
from tuf.api.exceptions import DownloadError, RepositoryError
from tuf.ngclient import UpdaterConfig
from tuf.ngclient import Updater

# constants
download_dir = "downloads"
metadata_url = "http://127.0.0.1:8080"
repo_url = "http://127.0.0.1:8000"
metadata_dir = "metadata"


def download(target: str) -> bool:
    """
    Download the target file using ``ngclient`` Updater.
    1. Download the root metadata file
    2. Download the target file and verify against the root metadata file
    """
    root_url = f"{metadata_url}/1.root.json"
    local_root_file = f"{metadata_dir}/root.json"
    print("Downloading...")
    if not os.path.isdir(metadata_dir):
        os.makedirs(metadata_dir)
    if not os.path.isdir(download_dir):
        os.makedirs(download_dir)

    try:
        request.urlretrieve(root_url, local_root_file)
    except OSError:
        print(f"Failed to download initial root from {root_url}")
        return False

    print(f"Using trusted root in {metadata_dir}")

    try:
        uconfig = UpdaterConfig(prefix_targets_with_hash=False)
        updater = Updater(
            metadata_dir=metadata_dir,
            metadata_base_url=f"{metadata_url}",
            target_base_url=f"{repo_url}",
            target_dir=download_dir,
            config=uconfig
        )
        updater.refresh()

        info = updater.get_targetinfo(target)

        if info is None:
            print(f"Target {target} not found")
            return True

        path = updater.find_cached_target(info)
        if path:
            print(f"Target is available in {path}")
            return True

        path = updater.download_target(info)
        print(f"Target downloaded and available in {path}")

    except (OSError, RepositoryError, DownloadError) as e:
        print(f"Failed to download target {target}: {e}")
        return False

    return True


if __name__ == "__main__":
    if not download("myfile.txt"):
        sys.exit(1)

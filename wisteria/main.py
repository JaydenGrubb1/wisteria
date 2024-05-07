import argparse
import os

from rosdistro import get_index, get_index_url, get_cached_distribution
from rosdistro.dependency_walker import DependencyWalker


def main():
    parser = argparse.ArgumentParser(
        description="Dependency snapshotting tool for ROS packages."
    )
    parser.add_argument(
        "-d",
        "--distro",
        type=str,
        dest="distro",
        default="humble",
        help="ROS distribution to use (default: humble)",
        required=False,
    )
    parser.add_argument(
        "-p",
        "--package",
        type=str,
        dest="package",
        default="ros_base",
        help="ROS package to get dependencies for (default: ros_base)",
        required=False,
    )
    parser.add_argument(
        "-t",
        "--type",
        type=str,
        dest="types",
        nargs="+",
        default=[
            "buildtool",
            "buildtool_export",
            "build",
            "build_export",
            "run",
            "test",
            "exec",
        ],
        help="Dependency type to get (default: all)",
        required=False,
    )
    parser.add_argument(
        "-s",
        "--system",
        type=str,
        dest="system",
        choices=["linux", "osx", "win64"],
        default="linux",
        help="System to get dependencies for (default: linux)",
        required=False,
    )
    args = parser.parse_args()

    # TODO get distrubution at specific time
    url = get_index_url()
    index = get_index(url)
    distro = get_cached_distribution(index, args.distro)

    python_version = index.distributions[args.distro]["python_version"]
    os.environ["ROS_PYTHON_VERSION"] = "{0}".format(python_version)
    os.environ["ROS_DISTRO"] = "{0}".format(args.distro)
    if "ROS_ROOT" in os.environ:
        os.environ.pop("ROS_ROOT")
    if "ROS_PACKAGE_PATH" in os.environ:
        os.environ.pop("ROS_PACKAGE_PATH")

    walker = DependencyWalker(distro, os.environ)

    deps = walker.get_recursive_depends(
        pkg_name=args.package,
        depend_types=args.types,
        ros_packages_only=True,
        ignore_pkgs=None,
    )
    deps.add(args.package)
    deps = sorted(deps)

    max_len = max([len(dep) for dep in deps])
    print("{0:{2}} {1}".format("Package", "Version", max_len + 2))

    for dep in deps:
        pkg = distro.release_packages[dep]
        repo = distro.repositories[pkg.repository_name].release_repository
        version = repo.version
        print("{0:{2}} {1}".format(dep, version, max_len + 2))


if __name__ == "__main__":
    main()

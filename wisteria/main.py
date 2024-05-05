import argparse
import os

from rosdistro import get_index, get_index_url, get_cached_distribution
from rosdistro.dependency_walker import DependencyWalker

_depends_type = [
    "buildtool",
    "buildtool_export",
    "build",
    "build_export",
    "run",
    "test",
    "exec",
]

def main():
    parser = argparse.ArgumentParser(description="Dependency snapshotting tool for ROS packages.")
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
    args = parser.parse_args()

    index = get_index(get_index_url())
    distro = get_cached_distribution(index, args.distro)

    # TODO: Is this necessary?
    python_version = index.distributions[args.distro]["python_version"]
    os.environ["ROS_PYTHON_VERSION"] = "{0}".format(python_version)
    os.environ["ROS_DISTRO"] = "{0}".format(args.distro)
    if "ROS_ROOT" in os.environ:
        os.environ.pop("ROS_ROOT")
    if "ROS_PACKAGE_PATH" in os.environ:
        os.environ.pop("ROS_PACKAGE_PATH")

    walker = DependencyWalker(distro, os.environ)

    dependencies = walker.get_recursive_depends(
        pkg_name=args.package,
        depend_types=_depends_type,
        ros_packages_only=False,
        ignore_pkgs=None,
        limit_depth=1,
    )

    for dep in dependencies:
        print(dep)

if __name__ == "__main__":
    main()

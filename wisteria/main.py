import argparse
import os
import yaml

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
    parser.add_argument(
        "--no-rpe",
        action="store_true",
        dest="no_rpe",
        default=False,
        help="Do not propogate resolution errors",
        required=False,
    )
    args = parser.parse_args()

    with open("robostack.yaml", "r") as f:
        conda_index = yaml.safe_load(f)

    def resolve_pkg(name):
        if name in conda_index:
            if "robostack" in conda_index[name]:
                if args.system in conda_index[name]["robostack"]:
                    return conda_index[name]["robostack"][args.system]
                else:
                    return conda_index[name]["robostack"]

        return None

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

    visited = {}
    conda_deps = []

    def walk_dependencies(name):
        if name in visited:
            return visited[name]

        if not name in distro.release_packages:
            # TODO check conda index
            conda = resolve_pkg(name)
            if conda is not None:
                print("\033[93m{0} => {1}\033[0m".format(name, conda))
                conda_deps.extend(conda)
                visited[name] = True
                return True
            else:
                print("\033[91m{0} => could not be resolved\033[0m".format(name))
                if args.no_rpe:
                    visited[name] = True
                    return True
                else:
                    visited[name] = False
                    return False

        dependencies = walker.get_recursive_depends(
            pkg_name=name,
            depend_types=args.types,
            ros_packages_only=False,
            ignore_pkgs=None,
            limit_depth=1,
        )

        for dep in dependencies:
            if not walk_dependencies(dep):
                print("\033[91m{0} could not be resolved\033[0m".format(name))
                return False

        # process ROS package
        pkg = distro.release_packages[name]
        repo = distro.repositories[pkg.repository_name].release_repository
        version = repo.version
        print("{0} ({1})".format(name, version))

        visited[name] = True
        return True

    print("ROS DEPENDENCIES:")
    walk_dependencies(args.package)

    print()
    print("CONDA DEPENDENCIES:")

    conda_deps = list(set(conda_deps))
    for dep in conda_deps:
        print(dep)


if __name__ == "__main__":
    main()

import argparse
import os

from rosdistro import get_index, get_index_url, get_cached_distribution
from rosdistro.dependency_walker import DependencyWalker

# from rosdistro.manifest_provider import get_release_tag


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

    # dependencies = walker.get_recursive_depends(
    #     pkg_name=args.package,
    #     depend_types=args.types,
    #     ros_packages_only=False,
    #     ignore_pkgs=None,
    #     limit_depth=1,
    # )

    # for dep in dependencies:
    #     version = "unknown"
    #     try:
    #         pkg = distro.release_packages[dep]
    #         repo = distro.repositories[pkg.repository_name].release_repository
    #         # tag = get_release_tag(repo, dep)
    #         # tag is in the form of "release/{distro}/{pkg}/{version}"
    #         # IDK if tag is needed for anything
    #         version = repo.version
    #     except Exception as e:
    #         pass
    #     print("{0} ({1})".format(dep, version))

    visited = {}

    def walk_dependencies(name):
        if name in visited:
            return visited[name]

        if not name in distro.release_packages:
            # TODO check conda index
            print("\033[93m{0}\033[0m".format(name))
            visited[name] = True
            return True

        dependencies = walker.get_recursive_depends(
            pkg_name=name,
            depend_types=args.types,
            ros_packages_only=False,
            ignore_pkgs=None,
            limit_depth=1,
        )

        for dep in dependencies:
            if not walk_dependencies(dep):
                return False

        # process ROS package
        pkg = distro.release_packages[name]
        repo = distro.repositories[pkg.repository_name].release_repository
        version = repo.version
        print("{0} ({1})".format(name, version))

        visited[name] = True
        return True

    walk_dependencies(args.package)


if __name__ == "__main__":
    main()

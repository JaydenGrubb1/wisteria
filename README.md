Dependency snapshotting tool for ROS packages.

## Flags

| Flag | Default Value | Description |
| --- | --- | ---|
| -p / --package | all | What package/s to snapshot |
| -d / --distro | humble | What ROS distribution to snapshot from |
| -t / --type | [buildtool, buildtool_export, build, build_export, run, test, exec] | The type of dependencies (ROS only) to additionally snapshot |
| -s / --system | linux | The operating system to snapshot for |
| -o / --output | snapshot.yaml | Where to store the output file |
| -q / --quiet | false | Disables output to the command line |
| -h / --help | false | Displays this help information |

## Dependencies

- rosdistro
- pyyaml
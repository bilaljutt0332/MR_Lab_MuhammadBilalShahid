Question#1:-

Node: A process that performs computation (e.g., a controller or sensor driver).
Topic: A named communication channel for streaming messages between nodes.
Package: A folder containing ROS 2 code, dependencies, and build information.
Workspace: A folder containing one or more packages and build outputs.

Question#2:-

Sourcing loads the necessary environment variables (like $PATH and $PYTHONPATH) into your terminal so it can locate ROS 2 executables and libraries.
If you don't source the workspace, your terminal will return "command not found" or fail to recognize your custom packages, as it has no map of where the ROS files are stored.

Question#3:-

The purpose of colcon build is to compile and link all the source code in your ROS 2 workspace into usable executables and libraries. It automates the build process for multiple packages simultaneously, ensuring dependencies are handled in the correct order.
Running this command generates four primary folders in your workspace directory:

1- build/: Stores intermediate files (like object files) created during the compilation process for each package.

2- install/: Contains the final executables, libraries, and the crucial setup.bash scripts needed to run your code.

3- log/: Holds text files detailing the build history and any errors or warnings encountered during compilation.

4- local_setup.*: (Usually inside install/) These scripts allow you to source only your local workspace without re-sourcing the entire ROS 2 underlay.

Question#4:-

The entry_points in setup.py acts as a translator that maps a custom command name to a specific Python function in your code. When you run colcon build, it creates a small executable script in your install/ folder based on this mapping.

Instead of manually running python3 my_script.py, you can simply type your chosen command (like talker) in the terminal. The script then automatically triggers the designated function (usually main()) within your package.

Question#5:-

[ Publisher Node ]                [ Topic ]                [ Subscriber Node ]
  +--------------------+       +---------------------+       +----------------------+
  |                    |       |                     |       |                      |
  |  /telemetry_node   | ----> |    /sensor_data     | ----> |    /display_node     |
  |                    |       |                     |       |                      |
  +--------------------+       +---------------------+       +----------------------+
     (Sends Message)             (Data Pipeline)              (Receives Message)
     

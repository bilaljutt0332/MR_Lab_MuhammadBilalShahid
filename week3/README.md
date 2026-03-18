The objective of this lab was to successfully set up a ROS 2 workspace and develop a custom Python package named my_turtle_package to
 control a mobile robot simulator. Following the workspace initialization and the creation of a dedicated src directory, I developed
 a Python node titled move_turtle.py to interface with the turtlesim simulation environment. The implementation involved programming
 the turtle to execute specific geometric trajectories, including square, triangular, and circular patterns, by publishing velocity
 commands to the /turtle1/cmd_vel topic. Furthermore, the project scope was expanded to demonstrate multi-robot coordination by utilizing
 the /spawn service to generate three independent turtles, each moving in distinct patterns simultaneously. To ensure precise positioning
 as suggested by the lab requirements, I also implemented logic to move the turtle to specific (x, y) coordinates using appropriate ROS 2
 service calls. All source code, including the package.xml dependencies and setup.py entry points, was managed via Git and pushed to a
 GitHub repository for version control and deliverable submission.

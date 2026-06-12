from setuptools import setup

package_name = 'vision_follower'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='student',
    maintainer_email='student@example.com',
    description='Vision-based target tracking nodes for tasks 1-5',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Format: 'executable_name = package_name.module_name:function'
            'task1 = vision_follower.task1_image_subscriber:main',
            'task2 = vision_follower.task2_color_segmentation:main',
            'task3 = vision_follower.task3_centroid_detection:main',
            'task4 = vision_follower.task4_proportional_control:main',
            'task5 = vision_follower.task5_object_tracking:main',
        ],
    },
)

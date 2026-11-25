from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'mission_manager_pkg'

setup(
    name=package_name,
    version='0.1.0',
    # states 하위 패키지까지 자동 포함
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='you@example.com',
    description='자동 전이 상태머신 기반 미션 매니저.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            # ros2 run mission_manager_pkg mission_manager
            'mission_manager = mission_manager_pkg.mission_manager_node:main',
        ],
    },
)

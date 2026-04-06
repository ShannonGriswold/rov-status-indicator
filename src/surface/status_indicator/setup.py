from glob import glob
import os
from pathlib import Path

from setuptools import find_packages, setup

PACKAGE_NAME = 'status_indicator'

setup(
    name=PACKAGE_NAME,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + PACKAGE_NAME]),
        ('share/' + PACKAGE_NAME, ['package.xml']),
        (
            str(Path('share') / PACKAGE_NAME / 'launch'),
            [str(path) for path in Path('launch').glob('*launch.[pxy][yma]*')],
        )
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='shannon',
    maintainer_email='svg33@case.edu',
    description='Status Indicator for the ROV',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': ['status_indicator = status_indicator.status_indicator:main',
                            'bridge = status_indicator.bridge:main'],
    },
)

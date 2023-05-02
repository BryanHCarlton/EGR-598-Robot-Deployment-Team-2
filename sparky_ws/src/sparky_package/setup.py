from setuptools import setup

package_name = 'sparky_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ay93',
    maintainer_email='alex_yes_nav@hotmail.com',
    description='Sparky Detector',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sparky_node = sparky_package.sparky_node:main'
        ],
    },
)

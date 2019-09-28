#!/usr/bin/env python3
import sys
__version__ = '0.0.2'

from setuptools import setup, find_packages

# We do not support Python <3.4
if sys.version_info < (3, 6):
    print("Unfortunately, your python version is not supported!\n"
          "Please upgrade at least to Python 3.6!", file=sys.stderr)
    sys.exit(1)

install_requires = [
    'colorlog',
    'pyyaml',
    'websocket_client',
    'requests',
    'facebook-wda'
]

entry_points = {
        'console_scripts': [
        'minitest=minium.framework.loader:main',
        'miniruntest=minium.framework.loader:main',
        'minireport=minium.framework.report:main',
        'mininative=minium.native.nativeapp:start_server'
    ],
}


config_path = "wechatdriver/version.json"
package_data = {
    'minium': ["framework/dist/*",
               config_path,
               "framework/dist/*/*",
               'native/*/*', 'native/minative/*/*',
               'native/*/*/*/*',
               'native/*/*/*/*/*',
               'native/*/*/*/*/*/*'],
    'framework': ['dist/*', 'dist/*/*'],
    'native': ['minative/*', 'minative/*/*', 'minative/*/*/*', 'minative/*/*/*/*', 'minative/*/*/*/*/*'],
}

exclude_package_data = {
    '': ["*pyc", "readme.md", "build.py"]
}

if __name__ == "__main__":
    setup(name="minium",
          version=__version__,
          license="MIT",
          url="https://git.code.oa.com/minium/driver.git",
          packages=find_packages(),
          description='Minium is the best MiniProgram auto test framework.',
          long_description="""""",
          package_data=package_data,
          exclude_package_data=exclude_package_data,
          entry_points=entry_points,
          install_requires=install_requires,
          setup_requires=['setuptools'],
          python_requires='>=3.6'
          )

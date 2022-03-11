#from distutils.core import setup
from setuptools import setup

import cmdl_backupu


# Get the long description from the README file
def read(fname):
    return open(fname).read()

setup(
    name='backupu',
    version=cmdl_backupu.__version__,
    packages=['cmdl_backupu', ],
    scripts=['cmdl_backupu/backupu.py', ],
    entry_points={'console_scripts': ['backupu = cmdl_backupu.backupu:main']},
    #long_description=read('README.md'),
    #long_description_content_type="text/markdown",
    url='',
    license='',
    author='G. Golyshev',
    author_email='g.golyshev@gmail.com',
    description='backup, full or inc, and copy work',
    #long_description=read('README'),
    # install_requires=[
    #     're >= 2.2', 'pandas >= 0.22.0', 'argparse >=1.1', 'numpy>=1.1', 'python_dateutil>=2.5'
    # ],
    # python_requires='>=3.3'
)
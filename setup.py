import codecs
import os
from platform import system
from setuptools import setup, find_packages

from plan_tools import NAME, VERSION

this_dir = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(this_dir, 'README.md'), encoding='utf-8') as i_file:
    long_description = i_file.read()

setup(
    name=NAME,
    version=VERSION,
    packages=find_packages(exclude=['test', 'tests', 'test.*']),
    url='https://github.com/Myoldmopar/PlanTools',
    license='ModifiedBSD',
    author='Edwin Lee, for NREL, for United States Department of Energy',
    description='A set of tools to help with Pip Links And Nonsense',
    long_description=long_description,
    long_description_content_type='text/markdown',
    test_suite='nose.collector',
    tests_require=['nose'],
    keywords='energyplus',
    include_package_data=True,  # use /MANIFEST.in file for declaring package data
    install_requires=[],
    entry_points={
        'console_scripts': [
            'plan_tool=plan_tools.runner:cli',
        ],
    },
    python_requires='>=3.5',
)

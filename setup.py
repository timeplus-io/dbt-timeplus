#!/usr/bin/env python

import os
import re

from setuptools import find_namespace_packages, setup


this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md')) as f:
    long_description = f.read()


# get this from a separate file
def _dbt_proton_version():
    _version_path = os.path.join(
        this_directory, 'dbt', 'adapters', 'proton', '__version__.py'
    )
    _version_pattern = r'''version\s*=\s*["'](.+)["']'''
    with open(_version_path) as f:
        match = re.search(_version_pattern, f.read().strip())
        if match is None:
            raise ValueError(f'invalid version at {_version_path}')
        return match.group(1)


package_name = 'dbt-proton'
package_version = _dbt_proton_version()
description = '''The Timeplus Proton plugin for dbt (data build tool)'''

dbt_version = '1.8.7'
dbt_minor = '.'.join(dbt_version.split('.')[0:2])

if not package_version.startswith(dbt_minor):
    raise ValueError(
        f'Invalid setup.py: package_version={package_version} must start with '
        f'dbt_version={dbt_minor}'
    )


setup(
    name=package_name,
    version=package_version,

    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Jove Zhong',
    author_email='jove@timeplus.com',
    url='https://github.com/timeplus-io/dbt-proton',
    license='Apache 2.0 License',

    packages=find_namespace_packages(include=['dbt', 'dbt.*']),
    package_data={
        'dbt': [
            'include/proton/dbt_project.yml',
            'include/proton/macros/*.sql',
            'include/proton/macros/**/*.sql',
        ]
    },
    install_requires=[
        f'dbt-core=={dbt_version}',
        'proton-driver>=0.2.10',
    ],
    python_requires=">=3.10",
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)

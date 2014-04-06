#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='pasticcio',
    version='0.1',
    author='Daniel Kertesz',
    author_email='daniel@spatof.org',
    license='BSD',
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'SQLAlchemy',
        'hashids==0.8.4',
    ],
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pasticcio = pasticcio.main:main',
        ],
    },
)
            

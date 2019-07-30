#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='pasticcio',
    version='0.1',
    description="A very simple pastebin web application",
    author='Daniel Kertesz',
    author_email='daniel@spatof.org',
    license='BSD',
    install_requires=[
        "Flask==1.0.2",
        'Flask-SQLAlchemy==1.0',
        'Flask-WTF==0.9.5',
        'Flask-Babel==0.9',
        'SQLAlchemy>=0.9',
        'hashids==0.8.4',
        'Pygments==1.6',
    ],
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pasticcio = pasticcio.main:main',
        ],
    },
    scripts=['scripts/pasticcio-cli'],
)
            

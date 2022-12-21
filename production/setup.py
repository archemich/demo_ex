"""Setup as package"""
import pathlib

from pkg_resources import parse_requirements
from setuptools import setup

with pathlib.Path('requirements.txt').open() as reqs_file:
    install_requires = [str(reqs) for reqs in parse_requirements(reqs_file)]

setup(
    name='demo_ex',
    description='Examination task',
    author='Mikhail Neprin',
    author_email='neprin@sfedu.ru',
    setup_requires=['setuptools_scm'],
    use_scm_version={'root': '../..',
                     'relative_to': __file__},
    packages=['demo_ex'],
    install_requires=install_requires,
    python_requires='>3.10',
    entry_points={
        'console_scripts': [
            'demo_ex = demo_ex.main:main'
        ]
    }
)

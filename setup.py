#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="django-multisite-plus",
    version="0.7.2",
    author="Divio AG",
    author_email="info@divio.com",
    url="https://github.com/divio/django-multisite-plus",
    license="BSD",
    description="An extension to django-multisite that eases local development.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    entry_points="""
        [console_scripts]
        django-multisite-plus=django_multisite_plus.cli:main
    """,
)

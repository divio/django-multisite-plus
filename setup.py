#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="django-multisite-plus",
    version="0.7.1",
    author="Divio AG",
    author_email="info@divio.com",
    url="https://github.com/divio/django-multisite-plus",
    license="BSD",
    description="An extension to django-multisite that eases local development.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "django>=2",
        "django-multisite>=1.4.0",
        "djangocms-multisite>=0.2.2",  # Note: this is divio/djangocms-multisite, not nephila/djangocms-multisite
        "aldryn_addons",
        "click",
        "psycopg2>=2.5",
        "yurl",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points="""
        [console_scripts]
        django-multisite-plus=django_multisite_plus.cli:main
    """,
)
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

from django_multisite_plus import __version__


setup(
    name='django-multisite-plus',
    version=__version__,
    author='Divio AG',
    author_email='info@divio.com',
    url='https://github.com/divio/django-multisite-plus',
    license='BSD',
    description='An extension to django-multisite that eases local development.',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django-multisite>=1.4.0',
        'djangocms-multisite>=0.2.1',
        'Django>=1.8',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

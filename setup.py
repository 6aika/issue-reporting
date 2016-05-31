# encoding=utf8

from setuptools import setup, find_packages

setup(
    name='issue-reporting',
    version='0.0.0',
    url='http://github.com/6aika/issue-reporting',
    license='MIT',
    packages=find_packages('.', include=[
        'issues',
        'issues.*',
        'issues*.*',
    ]),
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    install_requires=[l for l in open("./requirements.txt") if l and not l.startswith("#")],
    zip_safe=False,
)

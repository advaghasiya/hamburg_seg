# Copyright (c) OpenMMLab. All rights reserved.
import os
import os.path as osp
import platform
import shutil
import sys
import warnings
from setuptools import find_packages, setup


def readme():
    with open('README.md', encoding='utf-8') as f:
        content = f.read()
    return content


if __name__ == '__main__':
    setup(
        name='hamburgseg',
        # description='Open MMLab Semantic Segmentation Toolbox and Benchmark',
        long_description=readme(),
        long_description_content_type='text/markdown',
        keywords='computer vision, semantic segmentation',
        # url='http://github.com/open-mmlab/mmsegmentation',
        packages=find_packages(exclude=('configs', 'tools', 'demo')),
        include_package_data=True,
        install_requires=[
        'yapf==0.40.1'
        ],
        ext_modules=[],
        zip_safe=False)

from setuptools import setup, find_packages

name = 'tapdance'
version = '0.0.1'

DESCRIPTION = '''\
JTAG debug generator written in magma\
'''

with open('README.md', 'r') as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name=name,
    version=version,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    keywords = ['verilog', 'systemverilog', 'system-verilog', 'generator',
                'jtag', 'debug', 'tap', 'register'],
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'magma-lang',
        'mantle',
        'fault',
        'pyyaml'
    ],
    license='MIT',
    url=f'https://github.com/sgherbst/{name}',
    author='Stanford University',
    python_requires='>=3.7',
    download_url = f'https://github.com/sgherbst/{name}/archive/v{version}.tar.gz',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
        'License :: OSI Approved :: Apache Software License',
        f'Programming Language :: Python :: 3.7'
    ],
    include_package_data=True,
    zip_safe=False
)

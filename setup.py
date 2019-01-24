from setuptools import setup, find_packages

setup(
    name='amzsrcp',
    url='https://github.com/jenslaufer/amzsrcp',
    author='Jens Laufer',
    author_email='jenslaufer@gmail.com',
    packages=find_packages(),
    install_requires=['requests', 'argparse'],
    version='0.0.1',
    license='MIT',
    description='Tools to scrp Amz',
)

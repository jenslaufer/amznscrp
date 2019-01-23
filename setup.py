from setuptools import setup

setup(
    
    name='amzsrcp',
    url='https://github.com/jenslaufer/amzsrcp',
    author='Jens Laufer',
    author_email='jenslaufer@gmail.com',
    packages=['amznscrp'],
    install_requires=['urllib','re','requests','argparse','string'],
    version='0.1',
    license='MIT',
    description='Tools to scrp Amz',
)
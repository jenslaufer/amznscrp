from setuptools import setup, find_packages

setup(
    name='amznscrp',
    url='https://github.com/jenslaufer/amznscrp.git',
    author='Jens Laufer',
    author_email='jenslaufer@gmail.com',
    packages=find_packages(),  # ['amznscrp'],
    install_requires=['requests', 'bottlenose',
                      'lxml',
                      'scikit-learn',
                      'pandas', 'numpy', 'get_smarties'
                      ],
    version='0.0.1',
    license='MIT',
    description='Tools to scrp Amz',
)

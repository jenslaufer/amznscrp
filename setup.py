from setuptools import setup, find_packages

setup(
    name='amznscrp',
    url='https://github.com/jenslaufer/amznscrp.git',
    author='Jens Laufer',
    author_email='jenslaufer@gmail.com',
    packages=['amznscrp'],  # find_packages()
    install_requires=['requests', 'bottlenose',
                      'lxml',
                      'scikit-learn',
                      'pandas', 'numpy', 'get_smarties',
                      'pyuseragent', 'scrpproxies'
                      ],
    version='0.2.0',
    license='MIT',
    description='Tools to scrp Amz',
    include_package_data=True
)

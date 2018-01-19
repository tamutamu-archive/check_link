from setuptools import setup


requires = ["requests>=2.14.2", "beautifulsoup4"]


setup(
    name='check_link',
    version='0.1',
    description='Check that it checks all links.',
    url='https://github.com/tamutamu/check_link.git',
    author='tamutamu',
    author_email='tamutamu731@gmail.com',
    license='MIT',
    keywords='python3',
    packages=[
        "check_link"
    ],
    install_requires=requires,
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
)

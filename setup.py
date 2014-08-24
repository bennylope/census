from setuptools import setup

long_description = open('README.rst').read()


with open("census/__init__.py", "r") as module_file:
    for line in module_file:
        if line.startswith("__version__"):
            version_string = line.split("=")[1]
            version = version_string.strip().replace("'", "")

setup(
    name="census",
    version=version,
    # py_modules=['census'],
    author="Jeremy Carbaugh",
    author_email='jcarbaugh@sunlightfoundation.com',
    license="BSD",
    url="http://github.com/sunlightlabs/census",
    long_description=long_description,
    packages=['census'],
    include_package_data=True,
    description="A wrapper for the US Census Bureau's API",
    platforms=["any"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    install_requires=['requests>=1.0.0'],
    test_suite='tests',
)

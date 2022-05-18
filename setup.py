#!/usr/bin/env python
import re
import sys
import pathlib


try:
    from setuptools import setup
    from setuptools.command.test import test as TestCommand
    from setuptools.command.build_ext import build_ext
    from setuptools.extension import Extension


    class PyTest(TestCommand):
        def finalize_options(self):
            TestCommand.finalize_options(self)
            self.test_args = []
            self.test_suite = True

        def run_tests(self):
            # import here, because outside the eggs aren't loaded
            import pytest
            errno = pytest.main(self.test_args)
            sys.exit(errno)

except ImportError:

    from distutils.core import setup, Extension
    from distutils.command.build_ext import build_ext


    def PyTest(x):
        x


class custom_build_ext(build_ext):
    """
    NOTE: This code was originally taken from tornado.

    Allows C extension building to fail.

    The C extension speeds up crc16, but is not essential.
    """

    warning_message = """
********************************************************************
{target} could not
be compiled. No C extensions are essential for aredis to run,
although they do result in significant speed improvements for
websockets.
{comment}

Here are some hints for popular operating systems:

If you are seeing this message on Linux you probably need to
install GCC and/or the Python development package for your
version of Python.

Debian and Ubuntu users should issue the following command:

    $ sudo apt-get install build-essential python-dev

RedHat and CentOS users should issue the following command:

    $ sudo yum install gcc python-devel

Fedora users should issue the following command:

    $ sudo dnf install gcc python-devel

If you are seeing this message on OSX please read the documentation
here:

https://api.mongodb.org/python/current/installation.html#osx
********************************************************************
"""

    def run(self):
        try:
            super().run()
        except Exception as e:
            self.warn(e)
            self.warn(
                self.warning_message.format(
                    target="Extension modules",
                    comment=(
                        "There is an issue with your platform configuration "
                        "- see above."
                    )
                )
            )

    def build_extension(self, ext):
        try:
            super().build_extension(ext)
        except Exception as e:
            self.warn(e)
            self.warn(
                self.warning_message.format(
                    target=f"The {ext.name} extension ",
                    comment=(
                        "The output above this warning shows how the "
                        "compilation failed."
                    ),
                )
            )


_ROOT_DIR = pathlib.Path(__file__).parent

long_description = pathlib.Path(str(_ROOT_DIR / 'README.rst')).read_text()
with open(str(_ROOT_DIR / 'aredis' / '__init__.py')) as f:
    str_regex = r"['\"]([^'\"]*)['\"]"
    try:
        version = re.findall(f"^__version__ = {str_regex}$", f.read(), re.MULTILINE)[0]
    except IndexError:
        raise RuntimeError("Unable to find version in __init__.py")

setup(
    name='aredis',
    version=version,
    description='Python async client for Redis key-value store',
    long_description=long_description,
    url='https://github.com/NoneGG/aredis',
    author='Jason Chen',
    author_email='847671011@qq.com',
    maintainer='Jason Chen',
    maintainer_email='847671011@qq.com',
    keywords=['Redis', 'key-value store', 'asyncio'],
    license='MIT',
    packages=['aredis', 'aredis.commands'],
    python_requires=">=3.5",
    extras_require={'hiredis': ['hiredis>=0.2.0']},
    tests_require=['pytest',
                   'pytest_asyncio>=0.5.0'],
    cmdclass={
        'test': PyTest,
        'build_ext': custom_build_ext
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    ext_modules=[
        Extension(name='aredis.speedups',
                  sources=['aredis/speedups.c']),
    ],
    # The good news is that the standard library always
    # takes the precedence over site packages,
    # so even if a local contextvars module is installed,
    # the one from the standard library will be used.
    install_requires=[
        'contextvars;python_version<"3.7"'
    ]
)

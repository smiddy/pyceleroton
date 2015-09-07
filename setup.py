from setuptools import setup, find_packages
setup(
      name="pyceleroton",
      description="An API for the celeroton frequency converters.",
      version="0.1.0",
      platforms=["win-amd64", 'win32'],
      author="Markus J Schmidt",
      author_email='schmidt@ifd.mavt.ethz.ch',
      license="GNU GPLv3+",
      url="https://github.com/smiddy/pyceleroton",
      packages=find_packages(),
      install_requires=['pyserial>=2.7']
      )

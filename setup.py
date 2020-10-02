from setuptools import setup, find_packages

setup(name="alpha_shapes",
      packages=find_packages(),
      install_requires=['numpy',
                        'shapely',
                        'matplotlib'],
      )

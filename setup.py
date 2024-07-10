from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

description = "reconstruct the shape of a 2D point cloud."

setup(name="alpha_shapes",
      description=description,
      author="Panagiotis Zestanakis",
      author_email="panosz@gmail.com",
      packages=find_packages(),
      version='1.1.1',
      install_requires=['numpy',
                        'shapely',
                        'matplotlib'],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Science/Research",
          "Topic :: Scientific/Engineering",
          "Topic :: Scientific/Engineering :: Information Analysis",
      ],
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/panosz/alpha_shapes",
      python_requires='>=3.8',
      )

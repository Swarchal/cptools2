from setuptools import setup


def read_requirements():
    with open("requirements.txt", "r") as f:
        return [i.strip() for i in f.readlines()]


setup(name="cptools2",
      version=0.1,
      url="https://github.com/swarchal/cptools2",
      description="Tools for running CellProfiler on HPC setups",
      author="Scott Warchal",
      license="MIT",
      packages=["cptools2"],
      tests_require=["pytest"],
      python_requires=">=3.5",
      entry_points={
          "console_scripts": ["cptools2 = cptools2.__main__:main"]
          },
      install_requires=read_requirements())

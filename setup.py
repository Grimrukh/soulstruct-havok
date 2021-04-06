from setuptools import setup

try:
    with open("README.md") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "<README.md not found>"


def _get_version():
    with open("VERSION") as vfp:
        return vfp.read().strip()


setup(
    name="soulstruct",
    version=_get_version(),
    packages=["soulstruct"],
    description="Havok tools extension for Soulstruct.",
    long_description=long_description,
    author="Scott Mooney (Grimrukh)",
    author_email="grimrukh@gmail.com",
    url="https://github.com/grimrukh/soulstruct-havok",
)

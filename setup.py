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
    name="soulstruct-havok",
    version=_get_version(),
    packages=["soulstruct_havok"],
    description="Havok tools extension for Soulstruct.",
    long_description=long_description,
    install_requires=["colorama", "numpy", "scipy"],
    author="Scott Mooney (Grimrukh)",
    author_email="grimrukh@gmail.com",
    url="https://github.com/Grimrukh/soulstruct-havok",
)

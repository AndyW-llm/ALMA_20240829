from setuptools import setup

install_requires = []
requirements_file = "./requirements.txt"
with open(requirements_file, encoding="utf-8") as requirements_file:
    reqs = [r.strip() for r in requirements_file.readlines()]
    reqs = [r for r in reqs if r and r[0] != "#"]
    for r in reqs:
        install_requires.append(r)

setup(
    name="O1A_assessment",
    version="0.1",
    packages=["O1A_assessment"],
    install_requires=install_requires,
    url='https://github.com/AndyW-llm/ALMA_20240829/',
    license='',
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)
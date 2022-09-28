from setuptools import setup, find_packages


setup(
    name='gerund',
    version='0.1.0',
    author='maxwell flitton',
    author_email='maxwellflitton@gmail.com',
    packages=find_packages(exclude=("tests",)),
    scripts=[],
    url="https://github.com/OasisLMF/gerund",
    description='basic terminal command package',
    long_description="basic terminal command package",
    package_data={'': ['script.sh']},
    include_package_data=True,
    install_requires=[
        "pyyaml",
        "termcolor",
        # "requests==2.28.1"
    ],
    entry_points={
        "console_scripts": [
            "gerund=gerund.entry_points.run_config:main"
        ]
    },
)

from setuptools import setup

setup(
    name='snapshotanalyzer-30000',
    version='0.1',
    author='Aman Singh',
    author_email='aman.singh2406@live.com',
    description='Snapshotanalyzer-30000 is a tool to make snapshots of ec2 instances. It can list start and stop them.',
    license="GPL V3.0",
    packages=['shotty'],
    url="https://github.com/Aman2406/snapshotanalyzer-30000",
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points="""
    [console_scripts]
    shotty=shotty.shotty:click
    """,
)

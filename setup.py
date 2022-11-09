from setuptools import setup


with open('README.md', 'r') as f:
    readme = f.read()


setup(
    name='ejustian-cli',
    description='''
                \rA command line interface app that allows EJUST students to manage all their stuff.
                ''',
    long_description=readme,
    long_description_content_type='text/markdown',
    version='0.1.0',
    author='Abdelrahman Abdelkhalek',
    author_email='abdelrahman0w@gmail.com',
    packages=[
        'ej_cli', 'ej_cli.sis', 'ej_cli.loader',
        'ej_cli.map', 'ej_cli.wifi', 'ej_cli.kanban',
        'ej_cli.saved', 'ej_cli.attendance'
    ],
    entry_points={
        'console_scripts': [
            'ej = ej_cli.__main__:main'
        ]
    },
    include_package_data=True,
    python_requires=">=3.8.*",
    install_requires=[
        "requests", "beautifulsoup4",
        "lxml", "inquirer",
        "tabulate", "python-kanban",
    ],
    license='MIT',
)

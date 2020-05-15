from setuptools import setup

requires = [
    'pandas',
    'geopandas',
]

setup(
    name="SCSolver",
    version="1.0.1",
    description="Solveur pour le jeu Saute-Canton (https://sautecanton.fr/)",
    url="https://github.com/Epithumia/SCSolver",
    packages=['scsolver'],
    install_requires=requires,
    entry_points={
        'console_scripts': ['scsolver=scsolver.scsolver:main'],
    }
)

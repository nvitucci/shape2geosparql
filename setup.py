import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='shape2geosparql',
    version='0.1.1',
    author='Nicola Vitucci',
    author_email='nicola.vitucci@gmail.com',
    description='Convert shapefiles to GeoSPARQL',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nvitucci/shape2geosparql',
    license='MIT',
    install_requires=['rdflib',
                      'gdal',
                      'click'],
    extras_require={
        'tests': ['pytest'],
    },
    packages=setuptools.find_packages(),
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    python_requires='>=3.0',
    entry_points={
        'console_scripts': [
            'shape2geosparql = shape2geosparql.scripts.s2g_script:main'
        ]
    }
)

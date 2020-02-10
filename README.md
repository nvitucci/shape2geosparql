# shape2geosparql

A library for converting shapefiles to GeoSPARQL.

### Install

The `GDAL` library should already be installed on the system. On Fedora:

```bash
$ sudo yum install gdal-devel
```

On other systems:
- Ubuntu: https://mothergeo-py.readthedocs.io/en/latest/development/how-to/gdal-ubuntu-pkg.html#install-gdal-ogr
- Windows: https://sandbox.idre.ucla.edu/sandbox/tutorials/installing-gdal-for-windows

You only need to install the core library, as the Python bindings will be installed with `shape2geosparql`.

Once GDAL is installed:

```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install shape2geosparql
```

Should there be any problems in installing the `GDAL` Python library, try to run this first:

```bash
$ pip install gdal==$(gdal-config --version)
```

or insert the GDAL version number in place of `$(gdal-config --version)`. 

### Usage

Download and extract a shapefile, for example from:

- https://dati.trentino.it/dataset/stazioni-treno-open-data
- https://hifld-geoplatform.opendata.arcgis.com/datasets/american-red-cross-chapter-facilities

Then, from `python`, `IPython` or `Jupyter`:

```python
from shape2geosparql import convert

converter = convert('FILENAME.shp')
print(converter.write().decode()) 
```

You can also run the `shape2geosparql` command:

```bash
$ shape2geosparql FILENAME.shp

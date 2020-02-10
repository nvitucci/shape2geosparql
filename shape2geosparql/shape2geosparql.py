import os

from osgeo import ogr, osr
from rdflib import Graph, Literal, Namespace, RDF

GEO_NS = Namespace('http://www.opengis.net/ont/geosparql#')
SF_NS = Namespace('http://www.opengis.net/ont/sf#')
W3GEO_NS = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
S2G_NS = Namespace('http://github.com/nvitucci/shape2geosparql/ontology#')

ONTO_DIC = {
    u'curve': u'Curve',
    u'geometrycollection': u'GeometryCollection',
    u'line': u'Line',
    u'linearring': u'LinearRing',
    u'linestring': u'LineString',
    u'multicurve': u'MultiCurve',
    u'multilinestring': u'MultiLineString',
    u'multipoint': u'MultiPoint',
    u'multipolygon': u'MultiPolygon',
    u'multisurface': u'MultiSurface',
    u'point': u'Point',
    u'polygon': u'Polygon',
    u'polyhedralsurface': u'PolyhedralSurface',
    u'surface': u'Surface',
    u'tin': u'TIN',
    u'triangle': u'Triangle'
}


class Converter:
    def __init__(self, orig_path, graph):
        self.orig_path = orig_path
        self.graph = graph

    def write(self, outfile=None, outformat='nt'):
        return self.graph.serialize(destination=outfile, format=outformat)


class MissingFile(IOError):
    pass


def check_files(shapefile, ignore_prj=False):
    """Checks that the main files (.shp, .shx, .dbf, .prj)
    are present and accessible."""

    if not os.path.exists(shapefile):
        raise MissingFile('Missing .shp file')

    shape_base_name = os.path.splitext(shapefile)[0]

    shx = shape_base_name + '.shx'
    dbf = shape_base_name + '.dbf'
    prj = shape_base_name + '.prj'

    if not os.path.exists(shx):
        raise MissingFile('Missing .shx file')
    elif not os.path.exists(dbf):
        raise MissingFile('Missing .dbf file')
    elif not os.path.exists(prj) and not ignore_prj:
        raise MissingFile('Missing .prj file')


def get_features(infile):
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(4326)

    shape = ogr.Open(infile)
    layer = shape.GetLayer()

    source_sr = layer.GetSpatialRef()

    coord_transf = osr.CoordinateTransformation(source_sr, wgs84) if not source_sr.IsSame(wgs84) else None

    for feature_index in range(layer.GetFeatureCount()):
        feature = layer.GetFeature(feature_index)

        if coord_transf is not None:
            feature.geometry().Transform(coord_transf)

        yield feature_index, feature


def convert(infile, data_ns=None, schema_ns=None, include_wgs84=True, include_wkt=True,
            include_gml=False, include_json=True):
    check_files(infile)

    if data_ns is None:
        data_ns = Namespace('http://www.example.org/shape2geosparql/%s/data/' %
                            os.path.splitext(os.path.basename(infile))[0])
    else:
        data_ns = Namespace(data_ns)

    if schema_ns is None:
        schema_ns = Namespace('http://www.example.org/shape2geosparql/%s/ontology/' %
                              os.path.splitext(os.path.basename(infile))[0])
    else:
        schema_ns = Namespace(schema_ns)

    g = Graph()

    for feature_index, feature in get_features(infile):
        feature_id = data_ns[str(feature_index)]

        g.add((feature_id, RDF['type'], SF_NS['Feature']))

        for field in range(feature.GetFieldCount()):
            g.add((feature_id,
                   schema_ns[feature.GetFieldDefnRef(field).GetName().lower()],
                   Literal(feature.GetField(field))))

        geometry = feature.geometry()

        geom_id = data_ns[str(feature_index) + '_geom']
        g.add((feature_id, GEO_NS['hasGeometry'], geom_id))
        g.add((geom_id, RDF['type'], SF_NS['Geometry']))

        geom_type = geometry.GetGeometryName().lower()
        g.add((geom_id, RDF['type'], SF_NS[ONTO_DIC[geom_type]]))

        if include_wgs84:
            if geom_type == 'point':
                # NOTE: not sure whether to use the xsd:float literal or not, see http://www.w3.org/2003/01/geo/
                g.add((geom_id, W3GEO_NS['long'], Literal(geometry.GetX())))
                g.add((geom_id, W3GEO_NS['lat'], Literal(geometry.GetY())))

        if include_wkt:
            g.add((geom_id, GEO_NS['asWKT'], Literal(geometry.ExportToWkt(), datatype=GEO_NS['wktLiteral'])))

        if include_gml:
            g.add((geom_id, GEO_NS['asGML'], Literal(geometry.ExportToGML(), datatype=GEO_NS['gmlLiteral'])))

        # Uses local namespace
        if include_json:
            g.add((geom_id, S2G_NS['asGeoJson'], Literal(geometry.ExportToJson())))

    return Converter(orig_path=infile, graph=g)

import os, sys, rdflib
from rdflib import RDF, RDFS, OWL
import osgeo
from osgeo import ogr, osr

class MissingFile(Exception):
	pass

def check_files(shapefile, ignore_prj=True):
	'''Checks that the main files (.shp, .shx, .dbf, .prj) 
	are present and accessible.'''

	if not os.path.exists(shapefile):
		raise MissingFile('Missing .shp file')

	shapeBaseName = shapefile.split('.shp')[0]

	shx = shapeBaseName + '.shx'
	dbf = shapeBaseName + '.dbf'
	prj = shapeBaseName + '.prj'

	if not os.path.exists(shx):
		raise MissingFile('Missing .shx file')
	elif not os.path.exists(dbf):
		raise MissingFile('Missing .dbf file')
	elif not os.path.exists(prj) and not ignore_prj:
		raise MissingFile('Missing .prj file')

def make_rdf(infile, outfile, data_ns=None, schema_ns=None): 
	check_files(infile)

	use_wgs84 = True
	use_wkt = True
	use_gml = False
	use_json = True

	onto_dic = {
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
	 u'triangle': u'Triangle'}

	if data_ns == None:
		data_ns = rdflib.Namespace('http://www.example.org/shape2geosparql/' + os.path.basename(infile).split('.shp')[0] + '/data/')
	else:
		data_ns = rdflib.Namespace(data_ns)

	if schema_ns == None:
		schema_ns = rdflib.Namespace('http://www.example.org/shape2geosparql/' + os.path.basename(infile).split('.shp')[0] + '/ontology/')
	else:
		schema_ns = rdflib.Namespace(schema_ns)
	geo = rdflib.Namespace('http://www.opengis.net/ont/geosparql#')
	sf = rdflib.Namespace('http://www.opengis.net/ont/sf#')
	w3geo = rdflib.Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
	custom_geo = rdflib.Namespace('https://github.com/nvitucci/shape2geosparql/ontology#')
	
	wgs84 = osr.SpatialReference()
	wgs84.ImportFromEPSG(4326)
	
	# epsg3003 = osr.SpatialReference()
	# epsg3003.ImportFromEPSG(3003)
	# tr = osgeo.osr.CoordinateTransformation(epsg3003, wgs84)
	
	shape = osgeo.ogr.Open(infile)
	layer = shape.GetLayer()
	
	g = rdflib.Graph()
	
	for feature in range(layer.GetFeatureCount()):
		f = layer.GetFeature(feature)
	
		f_id_txt = str(feature)
		f_id = data_ns[f_id_txt]
	
		# TODO: Should properties really be lowercased?
		for field in range(f.GetFieldCount()):
			g.add((f_id, schema_ns[f.GetFieldDefnRef(field).GetName().lower()], rdflib.Literal(f.GetField(field))))
	
		geometry = f.geometry()
		geometry.TransformTo(wgs84)
	
		geom_id = data_ns[f_id_txt + '_geom']
		g.add((f_id, sf['hasGeometry'], geom_id))
	
		geom_type = geometry.GetGeometryName().lower()
		g.add((geom_id, RDF['type'], sf[onto_dic[geom_type]]))

		if use_wgs84:
			if geom_type == 'point':
				# NOTE: not sure whether to use the xsd:float literal or not, see http://www.w3.org/2003/01/geo/
				g.add((geom_id, w3geo['long'], rdflib.Literal(geometry.GetX())))
				g.add((geom_id, w3geo['lat'], rdflib.Literal(geometry.GetY())))

		if use_wkt:
			g.add((geom_id, geo['asWKT'], rdflib.Literal(geometry.ExportToWkt(), datatype=geo['wktLiteral'])))

		if use_gml:
			g.add((geom_id, geo['asGML'], rdflib.Literal(geometry.ExportToGML(), datatype=geo['gmlLiteral'])))
	
		# NOTE: experimental
		if use_json:
			g.add((geom_id, custom_geo['asGeoJson'], rdflib.Literal(geometry.ExportToJson())))
	
	outfile = open(outfile, 'w')
	outfile.write(g.serialize(format='nt'))
	outfile.close()

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print 'Too few parameters.'
		sys.exit(-1)

	infile = sys.argv[1]

	make_rdf(infile, infile.split('.shp')[0] + '.nt')
	

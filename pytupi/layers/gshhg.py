
from osgeo import ogr
import shapefile


class GSHHG:

    def __init__(self, file):
        self.file = file
        self.shape = shapefile.Reader(file)
        self.shapes = self.shape.shapes()
        self.total_shapes = len(self.shapes)
        self.range_shapes = range(self.total_shapes)

        self.bbox_cache = []
        self.polygon_cache = []
        self.polygon_ogr_cache = []
        self.relevant_index_set = None

        for i in self.range_shapes:
            self.bbox_cache.append(self.shapes[i].bbox)
            self.polygon_cache.append(self.shapes[i].points)
            self.polygon_ogr_cache.append(self._create_ogr_polygon(self.shapes[i].points))

    def _create_ogr_point(self, point):
        ogr_point = ogr.Geometry(ogr.wkbPoint)
        ogr_point.AddPoint(point[0], point[1])
        return ogr_point

    def _lines(self, polygon):
        p0 = polygon[-1]
        for p1 in polygon:
            yield p0, p1
            p0 = p1

    def _create_ogr_polygon(self, polygon):
        ring = ogr.Geometry(ogr.wkbLinearRing)
        for line_point in self._lines(polygon):
            ring.AddPoint(line_point[0][0], line_point[0][1])
            ring.AddPoint(line_point[1][0], line_point[1][1])
        ogr_poly = ogr.Geometry(ogr.wkbPolygon)
        ogr_poly.AddGeometry(ring)
        return ogr_poly

    def getShapes(self):
        return self.shapes

    def getPoints(self, shape_index):
        return self.shapes[shape_index].points

    def isOverLand(self, point_lon_lat):
        point_ogr_lon_lat = self._create_ogr_point(point_lon_lat)
        loop_set = self.relevant_index_set
        if loop_set is None:
            loop_set = self.range_shapes
        for i in loop_set:
            polygon_ogr = self.polygon_ogr_cache[i]
            if polygon_ogr.Contains(point_ogr_lon_lat):
                return True
        return False

    def buildRelevantSet(self, bbox):
        self.relevant_index_set = []
        polygon_bbox = self._create_ogr_polygon(bbox)
        for i in self.range_shapes:
            polygon_ogr = self._create_ogr_polygon(self.polygon_cache[i])
            if polygon_bbox.Intersects(polygon_ogr):
                self.relevant_index_set.append(i)

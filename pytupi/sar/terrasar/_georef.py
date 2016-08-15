
from xml.dom import minidom
import datetime


class GeoRef:

    TAG_GEOLOCATION_GRID = 'geolocationGrid'
    TAG_NUMBER_GRID_POINTS = 'numberOfGridPoints'
    TAG_NUMBER_TOTAL = 'total'
    TAG_NUMBER_AZIMUTH = 'azimuth'
    TAG_NUMBER_RANGE = 'range'
    TAG_SPACING_GRID_POINTS = 'spacingOfGridPoints'
    TAG_SPACING_AZIMUTH = 'azimuth'
    TAG_SPACING_RANGE = 'range'
    TAG_tREFERENCE_TIME_UTC = 'tReferenceTimeUTC'
    TAG_tauREFERENCE_TIME = 'tauReferenceTime'
    TAG_GRID_POINT = 'gridPoint'
    TAG_POINT_T = 't'
    TAG_POINT_TAU = 'tau'
    TAG_POINT_LAT = 'lat'
    TAG_POINT_LON = 'lon'
    TAG_POINT_INC = 'inc'
    TAG_POINT_ELEV = 'elev'
    TAG_POINT_HEIGHT = 'height'

    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.locGrid = {}
        xmldoc = minidom.parse(self.xml_file)

        geoObj = xmldoc.getElementsByTagName(self.TAG_GEOLOCATION_GRID)[0]
        numberGridObj = geoObj.getElementsByTagName(self.TAG_NUMBER_GRID_POINTS)[0]
        self.locGrid[self.TAG_NUMBER_GRID_POINTS] = self._getNumberGridPoints(numberGridObj)

        spaceGridObj = geoObj.getElementsByTagName(self.TAG_SPACING_GRID_POINTS)[0]
        self.locGrid[self.TAG_SPACING_GRID_POINTS] = self._getSpacingNumberGrid(spaceGridObj)

        self.locGrid[self.TAG_tREFERENCE_TIME_UTC] = self._getTReferenceTimeUTC(geoObj)
        self.locGrid[self.TAG_tauREFERENCE_TIME] = self._getTauReferenceTime(geoObj)

        num_range = self.locGrid[self.TAG_NUMBER_GRID_POINTS][self.TAG_NUMBER_RANGE]
        num_azimuth = self.locGrid[self.TAG_NUMBER_GRID_POINTS][self.TAG_NUMBER_AZIMUTH]

        self.locGrid[self.TAG_GRID_POINT] = [[{} for a in range(num_azimuth)] for r in range(num_range)]
        gridPoints = geoObj.getElementsByTagName(self.TAG_GRID_POINT)

        for gridPoint in gridPoints:
            iaz = long(gridPoint.getAttribute("iaz"))
            irg = long(gridPoint.getAttribute("irg"))
            point = {}
            point[self.TAG_POINT_T] = self._getPointT(gridPoint)
            point[self.TAG_POINT_TAU] = self._getPointTau(gridPoint)
            point[self.TAG_POINT_LAT] = self._getPointLat(gridPoint)
            point[self.TAG_POINT_LON] = self._getPointLon(gridPoint)
            point[self.TAG_POINT_INC] = self._getPointInc(gridPoint)
            point[self.TAG_POINT_ELEV] = self._getPointElev(gridPoint)
            point[self.TAG_POINT_HEIGHT] = self._getPointHeight(gridPoint)
            self.locGrid[self.TAG_GRID_POINT][irg - 1][iaz - 1] = point

    def _getNumberGridPoints(self, xml):
        numberGrid = {}
        numberGrid[self.TAG_NUMBER_TOTAL] = long(xml.getElementsByTagName(self.TAG_NUMBER_TOTAL)[0].firstChild.nodeValue)
        numberGrid[self.TAG_NUMBER_AZIMUTH] = long(xml.getElementsByTagName(self.TAG_NUMBER_AZIMUTH)[0].firstChild.nodeValue)
        numberGrid[self.TAG_NUMBER_RANGE] = long(xml.getElementsByTagName(self.TAG_NUMBER_RANGE)[0].firstChild.nodeValue)
        return numberGrid

    def _getSpacingNumberGrid(self, xml):
        spaceGrid = {}
        spaceGrid[self.TAG_SPACING_AZIMUTH] = float(xml.getElementsByTagName(self.TAG_SPACING_AZIMUTH)[0].firstChild.nodeValue)
        spaceGrid[self.TAG_SPACING_RANGE] = float(xml.getElementsByTagName(self.TAG_SPACING_RANGE)[0].firstChild.nodeValue)
        return spaceGrid

    def _getTReferenceTimeUTC(self, xml):
        return xml.getElementsByTagName(self.TAG_tREFERENCE_TIME_UTC)[0].firstChild.nodeValue

    def _getTauReferenceTime(self, xml):
        return float(xml.getElementsByTagName(self.TAG_tauREFERENCE_TIME)[0].firstChild.nodeValue)

    def _getPointT(self, xml):
        return float(xml.getElementsByTagName(self.TAG_POINT_T)[0].firstChild.nodeValue)

    def _getPointTau(self, xml):
        return float(xml.getElementsByTagName(self.TAG_POINT_TAU)[0].firstChild.nodeValue)

    def _getPointLat(self, xml):
        return float(xml.getElementsByTagName(self.TAG_POINT_LAT)[0].firstChild.nodeValue)

    def _getPointLon(self, xml):
        return float(xml.getElementsByTagName(self.TAG_POINT_LON)[0].firstChild.nodeValue)

    def _getPointInc(self, xml):
        return float(xml.getElementsByTagName(self.TAG_POINT_INC)[0].firstChild.nodeValue)

    def _getPointElev(self, xml):
        return float(xml.getElementsByTagName(self.TAG_POINT_ELEV)[0].firstChild.nodeValue)

    def _getPointHeight(self, xml):
        return float(xml.getElementsByTagName(self.TAG_POINT_HEIGHT)[0].firstChild.nodeValue)

    def getLatLonGrid(self):
        parserGrid = self.locGrid[self.TAG_GRID_POINT]
        x_grid_size = len(parserGrid)
        y_grid_size = len(parserGrid[0])
        grid = [[[parserGrid[x][y][self.TAG_POINT_LAT], parserGrid[x][y][self.TAG_POINT_LON]]
                 for y in range(y_grid_size)] for x in range(x_grid_size)]
        return grid

    def getIncGrid(self):
        parserGrid = self.locGrid[self.TAG_GRID_POINT]
        x_grid_size = len(parserGrid)
        y_grid_size = len(parserGrid[0])
        grid = [[[parserGrid[x][y][self.TAG_POINT_INC]]
                 for y in range(y_grid_size)] for x in range(x_grid_size)]
        return grid

    def getSpacingGridAzimuth(self):
        return self.locGrid[self.TAG_SPACING_GRID_POINTS][self.TAG_SPACING_AZIMUTH]

    def getSpacingGridRange(self):
        return self.locGrid[self.TAG_SPACING_GRID_POINTS][self.TAG_SPACING_RANGE]

    def getTReferenceTimeUTC(self):
        temp_utc_str = self.locGrid[self.TAG_tREFERENCE_TIME_UTC]
        return datetime.datetime.strptime(temp_utc_str, self.DATE_FORMAT)

    def getTauReferenceTime(self):
        return self.locGrid[self.TAG_tauREFERENCE_TIME]


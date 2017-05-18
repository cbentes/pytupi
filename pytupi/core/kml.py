

def generate_kml_start_str():
    """ Generates the header for a KML file
    """
    kml_str = r'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    kml_str += r'<kml xmlns="http://www.opengis.net/kml/2.2" ' \
               r'xmlns:gx="http://www.google.com/kml/ext/2.2" ' \
               r'xmlns:atom="http://www.w3.org/2005/Atom" ' \
               r'xmlns:xal="urn:oasis:names:tc:ciq:xsdschema:xAL:2.0">'

    kml_str += '<Document>'
    return kml_str


def generate_kml_end_str():
    """ Generates the footer for a KML file
    """
    kml_str = '</Document>'
    kml_str += '</kml>'
    return kml_str


def generate_kml_placemark_from_point(point_latlon, color = None):
    """ Generates a placemark representation for a point [lat, lon]
    """
    if color is None:
        color = 'ff0000ff'
    lat = point_latlon[0]
    lon = point_latlon[1]
    d = 0.0008
    kml_str = '<Placemark>'
    kml_str += '<name>Point</name>'
    kml_str += '<Style>'
    kml_str += '<geomColor> %s </geomColor>' % color
    kml_str += '<geomScale>3</geomScale>'
    kml_str += '</Style>'
    kml_str += '<LineString>'
    kml_str += '<coordinates>%f,%f,0 %f,%f,0 %f,%f,0 %f,%f,0 %f,%f,0 </coordinates>' % \
               (lon-d, lat-d, lon+d, lat-d, lon+d, lat+d, lon-d, lat+d, lon-d, lat-d)
    kml_str += '</LineString>'
    kml_str += '</Placemark>'
    return kml_str


def generate_kml_fom_points(points):
    """ Generates a kml description from a list of (lat,lon) points
    """
    kml_str = generate_kml_start_str()
    for point in points:
        lat = point[0]
        lon = point[1]
        kml_str += '<Placemark>'
        kml_str += '<name>P</name>'
        kml_str += '<Style>'
        kml_str += '<geomColor>ff0000ff</geomColor>'
        kml_str += '<geomScale>3</geomScale>'
        kml_str += '</Style>'
        kml_str += '<LineString>'
        d = 0.0001
        kml_str += '<coordinates>%f,%f,0 %f,%f,0 %f,%f,0 %f,%f,0 %f,%f,0 </coordinates>' % (lon-d, lat-d, lon+d, lat-d, lon+d, lat+d, lon-d, lat+d, lon-d, lat-d)
        kml_str += '</LineString>'
        kml_str += '<description>&lt;![CDATA['
        kml_str += '&lt;b&gt;Heading:&lt;/b&gt;&amp;nbsp;147 &lt;br/&gt;'
        kml_str += '&lt;b&gt;SpeedOverGround:&lt;/b&gt;&amp;nbsp; ? kn&lt;br/&gt;'
        kml_str += '&lt;b&gt;Longitude:&lt;/b&gt;&amp;nbsp;  %f &lt;br/&gt;' % lon
        kml_str += '&lt;b&gt;Latitude:&lt;/b&gt;&amp;nbsp;  %f &lt;br/&gt;' % lat
        kml_str += '</description>'
        kml_str += '</Placemark>'
    kml_str += generate_kml_end_str()
    return kml_str


def generate_kml_timed_point(point_latlon, utc_time, heading, ship_name, ship_mmsi, ship_imo, ship_type, color):
    """ Generates a placemark representation for a point [lat, lon] with time information
    """
    lat = point_latlon[0]
    lon = point_latlon[1]
    year = utc_time.year
    month = utc_time.month
    day = utc_time.day
    hh = utc_time.hour
    mm = utc_time.minute
    ss = utc_time.second
    kml_str = '<Placemark>'
    kml_str += '<Style>'
    kml_str += '<IconStyle>'
    kml_str += '<color>%s</color>' % color
    kml_str += '<scale>0.6</scale>'
    kml_str += '<heading>%s</heading>' % (heading - 180.0)
    kml_str += '<Icon>'
    kml_str += '<href>http://maps.google.com/mapfiles/kml/pal5/icon6.png</href>'
    kml_str += '</Icon>'
    kml_str += '</IconStyle>'
    kml_str += '<LabelStyle>'
    kml_str += '<scale>1.5</scale>'
    kml_str += '</LabelStyle>'
    kml_str += '</Style>'
    kml_str += '<TimeStamp>'
    kml_str += '<when>%d-%02d-%02dT%02d:%02d:%02dZ</when>' % (year, month, day, hh, mm, ss)
    kml_str += '</TimeStamp>'
    kml_str += '<styleUrl>#golf-balloon-style</styleUrl>'
    kml_str += '<ExtendedData>'
    kml_str += '<Data name="ship_name">'
    kml_str += '<value> %s </value>' % ship_name
    kml_str += '</Data>'
    kml_str += '<Data name="ship_mmsi">'
    kml_str += '<value> %s </value>' % ship_mmsi
    kml_str += '</Data>'
    kml_str += '<Data name="ship_imo">'
    kml_str += '<value> %s </value>' % ship_imo
    kml_str += '</Data>'
    kml_str += '<Data name="ship_type">'
    kml_str += '<value> %s </value>' % ship_type
    kml_str += '</Data>'
    kml_str += '</ExtendedData>'
    kml_str += '<Point>'
    kml_str += '<coordinates>%f,%f</coordinates>' % (lon, lat)
    kml_str += '</Point>'
    kml_str += '</Placemark>'
    return kml_str


def save_kml_string_to_file(kml_file_path, kml_str):
    """ Save a KML String to a KML file for a given path
    """
    with open(kml_file_path, 'w') as kml_temp:
        kml_temp.write(kml_str)
    return

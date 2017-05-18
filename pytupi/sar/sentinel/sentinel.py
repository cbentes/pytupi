import os
import datetime

import numpy as np
import gdal
from PIL import Image
import xmltodict


class Sentinel(object):
    """ Sentinel 1A 1B representation
    """

    __version__ = 'v1.0_r2'

    def __init__(self, base_dir):

        self.base_dir = base_dir
        self.base_name_id = os.path.basename(base_dir)
        self.sentinel_input_file = os.path.join(base_dir, 'manifest.safe')
        self.object_files = self._decode_manifest()

    def _decode_manifest(self):
        with open(self.sentinel_input_file, 'r') as f:
            manifest_tree = xmltodict.parse(f.read())
        object_files = {}
        for dataObject in manifest_tree['xfdu:XFDU']['dataObjectSection']['dataObject']:
            key = dataObject['@repID']
            if key not in object_files:
                object_files[key] = []
            object_files[key].append(dataObject['byteStream']['fileLocation']['@href'])
        return object_files

    def _load_tiff_image(self, img_file_name):
        dataset = gdal.Open(img_file_name, gdal.GA_ReadOnly)
        band = dataset.GetRasterBand(1)
        dataArray = band.ReadAsArray()
        return dataArray

    def _convert_str_to_date(self, time_str):
        data_format = "%Y-%m-%dT%H:%M:%S.%f"
        datetime_obj = datetime.datetime.strptime(time_str, data_format)
        return datetime_obj

    def get_sensor_name(self):
        return 'Sentinel'

    def get_product_indexes(self):
        """ Product indexes
        """
        product_indexes = {}
        for i, p in enumerate(self.object_files['s1Level1ProductSchema']):
            id_name = os.path.basename(p).split('-')[0:4]
            id_name = self.base_name_id + '.{0}-{1}-{2}-{3}'.format(id_name[0], id_name[1], id_name[2], id_name[3])
            product_indexes[i] = id_name
        return product_indexes

    def process(self, product_index):
        # Retrieve file locations
        self.image_file = os.path.join(self.base_dir, self.object_files['s1Level1MeasurementSchema'][product_index])
        self.calibration_file = os.path.join(self.base_dir, self.object_files['s1Level1CalibrationSchema'][product_index])
        self.metadata_file = os.path.join(self.base_dir,  self.object_files['s1Level1ProductSchema'][product_index])
        self.quicklook_file = os.path.join(self.base_dir, self.object_files['s1Level1QuickLookSchema'][0])
        self.quick_img = np.asarray(Image.open(self.quicklook_file))

        # Build metadata tree fom XML
        self.metadata_tree = None
        with open(self.metadata_file, 'r') as f:
            self.metadata_tree = xmltodict.parse(f.read())

        self.productType = self.metadata_tree['product']['adsHeader']['productType']
        assert self.productType in ['SLC', 'GRD']
        self.polarisation = self.metadata_tree['product']['adsHeader']['polarisation']
        self.swath = self.metadata_tree['product']['adsHeader']['swath']
        self.mode = self.metadata_tree['product']['adsHeader']['mode']
        self.rangePixelSpacing = float(self.metadata_tree['product']['imageAnnotation']['imageInformation']['rangePixelSpacing'])
        self.azimuthPixelSpacing = float(self.metadata_tree['product']['imageAnnotation']['imageInformation']['azimuthPixelSpacing'])
        self.azimuthTimeInterval = float(self.metadata_tree['product']['imageAnnotation']['imageInformation']['azimuthTimeInterval'])
        self.slantRangeTime = float(self.metadata_tree['product']['imageAnnotation']['imageInformation']['slantRangeTime'])
        self.productFirstLineUtcTime = self._convert_str_to_date(self.metadata_tree['product']['imageAnnotation']['imageInformation']['productFirstLineUtcTime'])
        self.productLastLineUtcTime = self._convert_str_to_date(self.metadata_tree['product']['imageAnnotation']['imageInformation']['productLastLineUtcTime'])
        self.rangeSamplingRate = float(self.metadata_tree['product']['generalAnnotation']['productInformation']['rangeSamplingRate'])
        self.slantRangeTime = float(self.metadata_tree['product']['imageAnnotation']['imageInformation']['slantRangeTime'])

        # Reads the geogrid data table
        self.azimuth_time_table = []
        self.range_time_table = []
        self.range_index_table = []
        self.datagrid_table = []
        for geolocationGridPoint in self.metadata_tree['product']['geolocationGrid']['geolocationGridPointList']['geolocationGridPoint']:
            azimuthTime = self._convert_str_to_date(geolocationGridPoint['azimuthTime'])
            slantRangeTime = float(geolocationGridPoint['slantRangeTime'])
            pixel = long(geolocationGridPoint['pixel'])
            lat = float(geolocationGridPoint['latitude'])
            lon = float(geolocationGridPoint['longitude'])
            inc = float(geolocationGridPoint['incidenceAngle'])
            grid = {'lon': lon, 'lat': lat, 'inc': inc}
            self.azimuth_time_table.append(azimuthTime)
            self.range_time_table.append(slantRangeTime)
            self.range_index_table.append(pixel)
            self.datagrid_table.append(grid)

    def get_image(self):
        img = self.get_raw_image()
        if self.productType == 'GRD':
            return img
        else:
            return self._deburst_image(img)

    def get_raw_image(self):
        # return self._load_tiff_image(self.image_file)[::-1]
        return self._load_tiff_image(self.image_file)

    def _deburst_image(self, img):
        """ Deburst image using azimuth time
        """
        print '... start debursting process ...'
        # Read relevant metadata
        burst_list = []
        for burst in self.metadata_tree['product']['swathTiming']['burstList']['burst']:
            azimuthTime = self._convert_str_to_date(burst['azimuthTime'])
            firstValidSample = [long(n) for n in burst['firstValidSample']['#text'].split(' ')]
            lastValidSample = [long(n) for n in burst['lastValidSample']['#text'].split(' ')]
            burst_list.append({'azimuthTime': azimuthTime, 'firstValidSample': firstValidSample, 'lastValidSample': lastValidSample })

        linesPerBurst = long(self.metadata_tree['product']['swathTiming']['linesPerBurst'])
        samplesPerBurst = long(self.metadata_tree['product']['swathTiming']['samplesPerBurst'])

        i_burst = img[0:linesPerBurst][:]
        deburst_array = [i_burst]
        deburst_time_array = [burst_list[0]['azimuthTime']]

        for i in range(1, len(burst_list)):
            i_burst = img[i*linesPerBurst:(i+1)*linesPerBurst][:]
            #Find number of invalid lines
            invalid_lines = 0
            for v in burst_list[i]['firstValidSample']:
                if v != -1:
                    break
                invalid_lines += 1
            deburst_array.append(i_burst[invalid_lines::][:])
            deburst_time_array.append(burst_list[i]['azimuthTime'] + datetime.timedelta(0, invalid_lines*self.azimuthTimeInterval))

        def find_pixel_index(start_time, search_time):
            diff_time = (search_time - start_time)
            pixel_index = long(round(diff_time.total_seconds()/self.azimuthTimeInterval))
            return pixel_index

        first_start_time = deburst_time_array[0]
        img_deburst = deburst_array[0]
        # Cut the image in the overlapped position
        for i in range(1, len(burst_list)):
            index_to_cut = find_pixel_index(first_start_time, deburst_time_array[i])
            img_deburst = img_deburst[0:index_to_cut, :]
            img_deburst = np.concatenate((img_deburst, deburst_array[i]), axis=0)

        print '... done ...'
        return img_deburst

    @staticmethod
    def _bilinear(x, y, f):
        r1 = (1-x) * f[0] + x * f[1]
        r2 = (1-x) * f[3] + x * f[2]
        p = (1-y) * r1 + y * r2
        return p

    def getGeoLocation(self, x, y):
        """ GeoLocate the point (x,y) to (lat,lon)
        """
        y_time = datetime.timedelta(0, y*self.azimuthTimeInterval) + self.productFirstLineUtcTime

        # Find range period
        range_period = 0
        for i in range(1, len(self.range_index_table)):
            if self.range_index_table[i] == self.range_index_table[0]:
                range_period = i
                break

        # Calculate the azimuth index
        azimuth_period = len(self.range_index_table)/range_period
        a_index = 0
        for i in range(0, len(self.azimuth_time_table), range_period):
            if y_time <= self.azimuth_time_table[i]:
                break
            a_index = i/range_period

        # Calculate the range index
        r_index = 0
        for i in range(range_period):
            if x <= self.range_index_table[a_index*range_period + i]:
                break
            r_index = i
        quad_a = max(min(a_index, azimuth_period-2), 0)
        quad_r = max(min(r_index, range_period-2), 0)

        # Get fractions
        r_min = self.range_index_table[(quad_a + 0)*range_period + (quad_r + 0)]
        r_max = self.range_index_table[(quad_a + 0)*range_period + (quad_r + 1)]
        x_frac = (x - r_min)/(r_max - r_min)
        a_max = self.azimuth_time_table[(quad_a + 1)*range_period + (quad_r + 1)]
        a_min = self.azimuth_time_table[(quad_a + 0)*range_period + (quad_r + 0)]
        y_frac = ((y_time - a_min).total_seconds())/((a_max - a_min).total_seconds())

        # Retrieve grid points to bi-linear interpolation
        p1 = self.datagrid_table[(quad_a + 0)*range_period + (quad_r + 0)]
        p2 = self.datagrid_table[(quad_a + 0)*range_period + (quad_r + 1)]
        p3 = self.datagrid_table[(quad_a + 1)*range_period + (quad_r + 1)]
        p4 = self.datagrid_table[(quad_a + 1)*range_period + (quad_r + 0)]
        bi_lon = Sentinel._bilinear(x_frac, y_frac, [p1['lon'], p2['lon'], p3['lon'], p4['lon']])
        bi_lat = Sentinel._bilinear(x_frac, y_frac, [p1['lat'], p2['lat'], p3['lat'], p4['lat']])
        return [bi_lat, bi_lon]

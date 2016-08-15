
import datetime
import calendar


class Product:

    def __init__(self, xml_dict):
        self.xml_dict = xml_dict

    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    def get_number_of_rows(self):
        dataInfo = self.xml_dict['level1Product']['productInfo']['imageDataInfo']
        return long(dataInfo['imageRaster']['numberOfRows'])

    def get_number_of_cols(self):
        dataInfo = self.xml_dict['level1Product']['productInfo']['imageDataInfo']
        return long(dataInfo['imageRaster']['numberOfColumns'])

    def get_row_spacing(self):
        dataInfo = self.xml_dict['level1Product']['productInfo']['imageDataInfo']
        return float(dataInfo['imageRaster']['rowSpacing']['#text'])

    def get_col_spacing(self):
        dataInfo = self.xml_dict['level1Product']['productInfo']['imageDataInfo']
        return float(dataInfo['imageRaster']['columnSpacing']['#text'])

    def get_range_resolution(self):
        dataInfo = self.xml_dict['level1Product']['productInfo']['imageDataInfo']
        return float(dataInfo['imageRaster']['groundRangeResolution'])

    def get_azimuth_resolution(self):
        dataInfo = self.xml_dict['level1Product']['productInfo']['imageDataInfo']
        return float(dataInfo['imageRaster']['azimuthResolution'])

    def get_azimuth_looks(self):
        dataInfo = self.xml_dict['level1Product']['productInfo']['imageDataInfo']
        return float(dataInfo['imageRaster']['azimuthLooks'])

    def get_range_looks(self):
        dataInfo = self.xml_dict['level1Product']['productInfo']['imageDataInfo']
        return float(dataInfo['imageRaster']['rangeLooks'])

    def get_azimuth_time(self):
        """ Returns UTC time
        """
        sceneInfo = self.xml_dict['level1Product']['productInfo']['sceneInfo']
        start = sceneInfo['start']['timeUTC']
        stop = sceneInfo['stop']['timeUTC']
        start = self._get_timestamp_from_string(start, self.DATE_FORMAT)
        stop = self._get_timestamp_from_string(stop, self.DATE_FORMAT)
        return [start, stop]

    def get_range_time(self):
        sceneInfo = self.xml_dict['level1Product']['productInfo']['sceneInfo']
        start = float(sceneInfo['rangeTime']['firstPixel'])
        stop = float(sceneInfo['rangeTime']['lastPixel'])
        return [start, stop]

    def get_range_size(self):
        return self.get_number_of_cols()

    def get_azimuth_size(self):
        return self.get_number_of_rows()

    def get_scene_info_center_coord_azimuth_time(self):
        """ Return UTC time
        """
        time_str = self.xml_dict['level1Product']['productInfo']['sceneInfo']['sceneCenterCoord']['azimuthTimeUTC']
        utc_timestamp = self._get_timestamp_from_string(time_str, self.DATE_FORMAT)
        return utc_timestamp

    def get_cal_factor(self):
        cal_factor_str = self.xml_dict['level1Product']['calibration']['calibrationConstant']['calFactor']
        return float(cal_factor_str)

    def get_BBOX(self):
        bbox = []
        bbox_data_list = self.xml_dict['level1Product']['productInfo']['sceneInfo']['sceneCornerCoord']
        for bbox_data in bbox_data_list:
            lat = float(bbox_data['lat'])
            lon = float(bbox_data['lon'])
            bbox.append(lon)
            bbox.append(lat)
        return bbox

    @staticmethod
    def _get_timestamp_from_string(date_string, date_format):
        datetime_obj = datetime.datetime.strptime(date_string, date_format)
        timestamp = calendar.timegm(datetime_obj.timetuple()) + datetime_obj.microsecond/1e6
        return timestamp

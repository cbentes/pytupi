import os
import struct

import numpy as np
from tqdm import trange
from bs4 import BeautifulSoup
import xmltodict

from .. import sarsensor
import _product
import _georef
import _tsximage

# Reference:
#
# Level 1B Product Format Specifications
# http://www.intelligence-airbusds.com/files/pmedia/public/r460_9_030201_level-1b-product-format-specification_1.3.pdf
#


class TerraSARX(sarsensor.SARSensor):
    """ TerraSAR-X representation
    """

    def __init__(self, base_tsx_dir):

        self.base_name = os.path.basename(base_tsx_dir)
        self.base_dir = base_tsx_dir
        self.main_xml = os.path.join(self.base_dir, '{0}.xml'.format(self.base_name))
        self.georef_xml = os.path.join(self.base_dir, 'ANNOTATION', 'GEOREF.xml')

        handler = open(self.main_xml, 'r').read()
        main_dict = xmltodict.parse(handler)
        self.product = _product.Product(main_dict)

        # TODO: Complete geo_dict
        # handler = open(self.georef_xml, 'r').read()
        # geo_dict = xmltodict.parse(handler)
        self.georef = _georef.GeoRef(self.georef_xml)

        self._load_metadata()

    def _load_metadata(self):
        handler = open(self.main_xml, 'r').read()
        soup = BeautifulSoup(handler, "html.parser")
        prod = soup.find('productcomponents')
        self.img_files = []
        for s_img in prod.findAll('imagedata'):
            path = s_img.path.string
            pollayer = s_img.pollayer.string
            filename = s_img.filename.string
            img_data = {'path': path,
                        'pollayer': pollayer,
                        'filename': filename,
                        'layerindex': s_img.attrs['layerindex']}
            self.img_files.append(img_data)
        s_imgdata = soup.find('imagedatainfo')
        self.img_type = s_imgdata.imagedataformat.string

    def _load_cos(self, img_data):
        img_path = img_data['path']
        img_name = img_data['filename']
        img_index = img_data['layerindex']
        input_file = os.path.join(self.base_dir, img_path, img_name)
        file_size = os.path.getsize(input_file)
        gb_unit = 1024.0 ** 3
        print 'Image {0} idx:{1} [{2:.2f} GB]'.format(img_name, img_index, file_size / gb_unit)
        img_map = None
        with open(input_file, 'rb') as f:
            header_unpacker = struct.Struct('>lllll')
            dt = np.dtype([('r', '>i2'), ('i', '>i2')])
            burst_count = 0
            long_size = 4
            total_bytes = 7 * long_size
            header = f.read(total_bytes)
            header = header_unpacker.unpack_from(header)
            range_size = header[2]
            data_range_size = range_size + 2
            header_total_bytes = 4 * data_range_size * long_size
            f.seek(0, 0)
            header = f.read(header_total_bytes)
            while len(header) > 0:
                header = header_unpacker.unpack_from(header)
                azimuth_size = header[3]
                burst_count += 1
                data_burst = np.ndarray(shape=(azimuth_size, data_range_size), dtype=dt)
                for i in trange(azimuth_size, leave=True):
                    temp = np.fromfile(f, count=data_range_size, dtype=dt)
                    data_burst[i][:] = temp
                img_map = np.vstack((img_map, data_burst)) if img_map else data_burst
                header = f.read(header_total_bytes)
        return img_map

    def load_all(self):
        imgs = []
        for img_data in self.img_files:
            img = self._load_cos(img_data)
            imgs.append(img)
        return imgs

    def get_sensor_name(self):
        return 'TerraSAR-X'

    def get_number_channels(self):
        return len(self.img_files)

    def get_image_type(self):
        return self.img_type

    def get_image(self, channel=0):
        return self._build_sar_image(channel)

    def _build_sar_image(self, channel):
        img_data = self.img_files[channel]
        img = self._load_cos(img_data)
        sar_img = _tsximage.TSXImage()
        sar_img.img = img
        sar_img.shape = img.shape
        sar_img.center_timestamp = self.product.get_scene_info_center_coord_azimuth_time()
        sar_img.row_spacing = self.product.get_row_spacing()
        sar_img.col_spacing = self.product.get_col_spacing()
        sar_img.cal_factor = self.product.get_cal_factor()
        sar_img.azimuth_size = self.product.get_azimuth_size()
        sar_img.azimuth_grid_spacing = self.georef.getSpacingGridAzimuth()
        sar_img.range_size = self.product.get_range_size()
        sar_img.range_grid_spacing = self.georef.getSpacingGridRange()
        sar_img.range_time = self.product.get_range_time()
        sar_img.azimuth_time = self.product.get_azimuth_time()
        sar_img.latlon_grid = self.georef.getLatLonGrid()
        sar_img.inc_grid = self.georef.getIncGrid()
        sar_img.range_resolution = self.product.get_range_resolution()
        sar_img.azimuth_resolution = self.product.get_azimuth_resolution()
        sar_img.cal_factor = self.product.get_cal_factor()
        return sar_img

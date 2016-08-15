
import numpy as np
import scipy.optimize as optimize

from .. import sarimage


class TSXImage(sarimage.SARImage):

    def __init__(self):
        self.img = None
        self.shape = None
        self.center_timestamp = None
        self.row_spacing = None
        self.col_spacing = None
        self.cal_factor = None
        self.range_size = None
        self.azimuth_size = None
        self.range_grid_spacing = None
        self.azimuth_grid_spacing = None
        self.range_time = None
        self.azimuth_time = None
        self.latlon_grid = None
        self.inc_grid = None
        self.range_resolution = None
        self.azimuth_resolution = None
        self.cal_factor = None

    def get_shape(self):
        return self.shape

    def get_incidence_angle(self, x, y):
        """ Convert (x,y) from image coordinate to incidence angle
        """
        geogrid_tau_pos, geogrid_t_pos = self._get_geogrid_tau_and_t_pos(x, y)
        inc = self._t_tau_to_inc(geogrid_tau_pos, geogrid_t_pos)
        return inc

    def convert_to_img_coordinates(self, lon, lat):
        """ Convert (lat,lon) to image coordinate (x,y)
        """
        def cost_function(xy):
            x = xy[0]
            y = xy[1]
            t_lon, t_lat = self.convert_to_geo_coordinates(x, y)
            cost = (lat - t_lat)**2 + (lon - t_lon)**2
            return cost
        x0y0 = [self.range_size/2, self.azimuth_size/2]
        xyop = optimize.fmin(cost_function, x0y0, xtol=1e-5, disp=False)
        x_best = int(round(xyop[0]))
        y_best = int(round(xyop[1]))
        return [x_best, y_best]

    def convert_to_geo_coordinates(self, x, y):
        """ Convert (x,y) from image coordinate to (lon, lat)
        """
        geogrid_tau_pos, geogrid_t_pos = self._get_geogrid_tau_and_t_pos(x, y)
        lon = self._t_tau_to_lon(geogrid_tau_pos, geogrid_t_pos)
        lat = self._t_tau_to_lat(geogrid_tau_pos, geogrid_t_pos)
        return [lon, lat]

    def get_center_timestamp(self):
        return self.center_timestamp

    def get_row_spacing(self):
        return self.row_spacing

    def get_col_spacing(self):
        return self.col_spacing

    def get_roi(self, x0, y0, x1, y1):
        """
            -   x0, x1 = range indexes, where x1 > x0
            -   y0, y1 = azimuth indexes, where y1 > y0
        """
        sub_roi = self.img[y0:y1, x0:x1]
        size_y, size_x = sub_roi.shape
        result = np.ndarray(shape=(size_y, size_x), dtype=np.complex)
        for j in xrange(size_y):
            for i in range(size_x):
                result[j][i] = complex(sub_roi[j][i]['r'], sub_roi[j][i]['i'])
        return result

    def _get_geogrid_tau_and_t_pos(self, x, y):
        range_step = self._calculate_range_grid_step()
        azimuth_step = self._calculate_azimuth_grid_step()
        geogrid_tau_pos = x/range_step
        geogrid_t_pos = y/azimuth_step
        return [geogrid_tau_pos, geogrid_t_pos]

    def _t_tau_to_lat(self, x, y):
        """ Convert (y,x)=(t,tau) to Latitude
        """
        x_grid_size = len(self.latlon_grid)
        y_grid_size = len(self.latlon_grid[0])
        quad_x = min(int(x), x_grid_size-2)
        quad_y = min(int(y), y_grid_size-2)
        f = []
        quad_x = quad_x if quad_x > 0 else 0
        quad_y = quad_y if quad_y > 0 else 0
        f.append(self.latlon_grid[quad_x+0][quad_y+0][0])
        f.append(self.latlon_grid[quad_x+1][quad_y+0][0])
        f.append(self.latlon_grid[quad_x+1][quad_y+1][0])
        f.append(self.latlon_grid[quad_x+0][quad_y+1][0])
        bi_lat = self._bilinear(x-quad_x, y-quad_y, f)
        return bi_lat

    def _t_tau_to_lon(self, x, y):
        """ Convert (y,x)=(t,tau) to Longitude
        """
        x_grid_size = len(self.latlon_grid)
        y_grid_size = len(self.latlon_grid[0])
        quad_x = min(int(x), x_grid_size-2)
        quad_y = min(int(y), y_grid_size-2)
        f = list()
        quad_x = quad_x if quad_x > 0 else 0
        quad_y = quad_y if quad_y > 0 else 0
        f.append(self.latlon_grid[quad_x+0][quad_y+0][1])
        f.append(self.latlon_grid[quad_x+1][quad_y+0][1])
        f.append(self.latlon_grid[quad_x+1][quad_y+1][1])
        f.append(self.latlon_grid[quad_x+0][quad_y+1][1])
        bi_lon = self._bilinear(x-quad_x, y-quad_y, f)
        return bi_lon

    def _t_tau_to_inc(self, x, y):
        """ Convert (y,x)=(t,tau) to Incidence angle
        """
        quad_x = int(x)
        quad_y = int(y)
        f = list()
        f.append(self.inc_grid[quad_x+0][quad_y+0][0])
        f.append(self.inc_grid[quad_x+1][quad_y+0][0])
        f.append(self.inc_grid[quad_x+1][quad_y+1][0])
        f.append(self.inc_grid[quad_x+0][quad_y+1][0])
        inc = self._bilinear(x-quad_x, y-quad_y, f)
        return inc

    @staticmethod
    def _bilinear(x, y, f):
        r1 = (1-x) * f[0] + x * f[1]
        r2 = (1-x) * f[3] + x * f[2]
        p = (1-y) * r1 + y * r2
        return p

    def _calculate_range_grid_step(self):
        start_range_time = self.range_time[0]
        end_range_time = self.range_time[1]
        delta = end_range_time - start_range_time
        step = (self.range_size * self.range_grid_spacing) / delta
        return step

    def _calculate_azimuth_grid_step(self):
        start_time = self.azimuth_time[0]
        end_time = self.azimuth_time[1]
        diff = end_time - start_time
        step = (self.azimuth_size * self.azimuth_grid_spacing) / diff
        return step


class ROIFrame:

    def __init__(self, offset_x, offset_y, roi_size_x, roi_size_y):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.roi_size_x = roi_size_x
        self.roi_size_y = roi_size_y
        global_center_x = offset_x + (roi_size_x/2)
        global_center_y = offset_y + (roi_size_y/2)
        self.roi_center_global = (int(global_center_x), int(global_center_y))
        self.roi_center_local = (int(roi_size_x/2), int(roi_size_y/2))

    def transform_points_local(self, global_points):
        local_points = []
        for p in global_points:
            x_local = p[0] - self.offset_x
            y_local = p[1] - self.offset_y
            local_points.append(tuple([x_local, y_local]))
        return local_points

    def transform_points_global(self, local_points):
        global_points = []
        for p in local_points:
            x_global = p[0] + self.offset_x
            y_global = p[1] + self.offset_y
            global_points.append(tuple([x_global, y_global]))
        return global_points

    def cut_image_roi(self, img):
        img_roi = img[self.offset_y:self. offset_y +self.roi_size_y,
                  self.offset_x:self. offset_x +self.roi_size_x]
        return img_roi.copy()

    def __str__(self):
        return "ROI frame ({0}, {1}, {2}, {3})".format(self.offset_x, self.offset_y,
                                                       self.roi_size_x, self.roi_size_y)


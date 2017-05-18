import abc


class SARSensor(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_sensor_name(self):
        pass

    @abc.abstractmethod
    def get_image(self, channel):
        pass

    @abc.abstractmethod
    def get_number_channels(self):
        pass

    @abc.abstractmethod
    def get_image_type(self):
        pass

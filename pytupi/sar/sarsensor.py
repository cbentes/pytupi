
class SARSensor:

    def get_sensor_name(self):
        raise NotImplementedError('Method not implemented')

    def get_image(self, channel):
        raise NotImplementedError('Method not implemented')

    def get_number_channels(self):
        raise NotImplementedError('Method not implemented')

    def get_image_type(self):
        raise NotImplementedError('Method not implemented')

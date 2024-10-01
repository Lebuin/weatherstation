class Base:
    def __init__(self, name):
        self.name = name


    def get_value(self, request):
        data = request.args.get(self.name, None)
        if data is None or data == '-9999':
            raise ValueError(f'Parameter {self.name} not found')
        return self.parse(data)


    def parse(self, data):
        return data


class String(Base):
    pass


class Integer(Base):
    def parse(self, data):
        return int(data)



class Temperature(Base):
    # Unit: celcius
    def parse(self, data):
        return round((float(data) - 32) / 1.8, 1)


class Humidity(Base):
    # Unit: %
    def parse(self, data):
        return int(data)


class WindDirection(Base):
    # Unit: degrees
    def parse(self, data):
        return int(data)


class WindSpeed(Base):
    # Unit: km/h
    def parse(self, data):
        return round(float(data) * 1.60934, 0)


class Rain(Base):
    # Unit: mm
    def parse(self, data):
        return round(float(data) * 25.4, 1)


class SolarRadiation(Base):
    # Unit: W/m^2
    def parse(self, data):
        return float(data)


class UV(Base):
    # Unit: index
    def parse(self, data):
        return float(data)


class Pressure(Base):
    # Unit: hPa
    def parse(self, data):
        return round(float(data) * 33.8639, 1)


class Battery(Base):
    def parse(self, data):
        if int(data) == 1:
            return 'low'
        else:
            return ''

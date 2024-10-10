from logger.transforms.transform import Transform
from logger.utils.das_record import DASRecord
import logging

class NormalizeLatLonTransform(Transform):
    """
    Simple example of a custom data transformation.
    """
    def __init__(self, kwargs):
        """
        Look for these keys in the kwargs dict:
        latitude
        n_or_s
        longitude
        e_or_w
        """
        self.latitude = kwargs.get('latitude', None)
        self.n_or_s = kwargs.get('n_or_s', None)
        self.longitude = kwargs.get('longitude', None)
        self.e_or_w = kwargs.get('e_or_w', None)

        self.signed_latitude = None
        self.signed_longitude = None

    def transform(self, record):
        """Take unsigned lat, NorS, unsigned lon, EorW, and transform it into signed lat and signed lon 
        """
        # Check that we've got the right record type - it should be a
        # single record.
        if not record or type(record) is not dict:
            logging.warning(f'Improper type for record: {type(record)}',)
            return None
        
        # Do we have enough values to emit a record? If not, go home.
        if any(prop is None for prop in (self.latitude, self.n_or_s, self.longitude, self.e_or_w)):
            logging.debug('Not all required values present - skipping')
            return None
        
        # Normalize lat and long
        if self.n_or_s == 'N':
            self.signed_latitude = self.latitude
        elif self.n_or_s == 'S':
            self.signed_latitude = self.latitude * -1
        else:
            logging.warning(f'Invalid value for n_or_s: {self.n_or_s}')
        if self.e_or_w == 'E':
            self.signed_longitude = self.longitude
        elif self.e_or_w == 'W':
            self.signed_longitude = self.longitude * -1
        else:
            logging.warning(f'Invalid value for e_or_w: {self.e_or_w}')

        # Add new fields
        if type(record) is DASRecord:
            record.fields['signed_latitude'] = self.signed_latitude
            record.fields['signed_longitude'] = self.signed_longitude
        elif type(record) is dict:
            record['signed_latitude'] = self.signed_latitude
            record['signed_longitude'] = self.signed_longitude
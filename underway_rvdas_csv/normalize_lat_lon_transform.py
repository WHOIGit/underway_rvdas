from logger.transforms.transform import Transform
import logging

class NormalizeLatLonTransform(Transform):
    """
    Simple example of a custom data transformation.
    """
    def __init__(self):
        self.signed_latitude = None
        self.signed_longitude = None

    def transform(self, record):
        """
        Take unsigned lat, NorS, unsigned lon, EorW, and transform it into signed lat and signed lon 
        """

        # Check that we've got the right record type - it should be a single record
        if not isinstance(record, dict):
            logging.warning(f'Improper type for record: {type(record)}')
            return None


        # Check if all required fields are present
        fields = record['fields']
        required_fields = ['GPSLatitude', 'GPSNorS', 'GPSLongitude', 'GPSEorW']
        if not all(field in fields for field in required_fields):
            logging.warning(f'Missing required fields in record: {fields.keys()}')
            return None

        # Normalize lat and long
        if fields['GPSNorS'] == 'N':
            self.signed_latitude = fields['GPSLatitude']
        elif fields['GPSNorS'] == 'S':
            self.signed_latitude = -fields['GPSLatitude']
        else:
            logging.warning(f'Invalid value for GPSNorS: {fields['GPSNorS']}')
            return None
        
        if fields['GPSEorW'] == 'E':
            self.signed_longitude = fields['GPSLongitude']
        elif fields['GPSEorW'] == 'W':
            self.signed_longitude = -fields['GPSLongitude']
        else:
            logging.warning(f'Invalid value for GPSEorW: {fields['GPSEorW']}')
            return None

        # Add new fields
        fields['SignedLatitude'] = self.signed_latitude
        fields['SignedLongitude'] = self.signed_longitude

        return record
import logging
from util.utils import path

geo_ids = {
    'usa': '103644278',
    'eg': '106155005',
}


# kriss_account = AQEDAVObq0oDED4UAAABkmeREVcAAAGSi52VV1YAl4WMpgvZdb5o5OrqR-qDV6p444wFo12xQKZgxqrNXakJ2UibTxIhgfeu43zbrWnom5t4NmX4zMOEkAdXqMv9otORFi_38HeDlnmqVdoTuxWdfKCt
# my_account = AQEDAVLyOtoDpJV1AAABkga6Gq4AAAGSgquPI00ARegtWIeIAq23i9Vf8FakelW5IrhuRuWoEMwviIG5A38eGJeMXBP7xYwS2Y5yvXKWep47rCIbuorXfUJzTOIHZNAx1Yrk60bLqpzdLx_ZXv_AyQxH
settings = {
    "LI_AT": "AQEDAVLyOtoDpJV1AAABkga6Gq4AAAGSgquPI00ARegtWIeIAq23i9Vf8FakelW5IrhuRuWoEMwviIG5A38eGJeMXBP7xYwS2Y5yvXKWep47rCIbuorXfUJzTOIHZNAx1Yrk60bLqpzdLx_ZXv_AyQxH",
    "endpoint": 'https://www.linkedin.com',
    "LOGGING_LEVEL": logging.INFO,
    "VERBOSE": False,
    "PROXIES": None,
    "DATABASE": path('.db', 'profiles.db'),
}

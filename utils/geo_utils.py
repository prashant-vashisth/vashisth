from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz

def get_geo_details(pob):
    """Get verified location data with error handling"""
    geolocator = Nominatim(user_agent="professional_vedic_astrology")
    try:
        location = geolocator.geocode(pob, timeout=10)
        if not location:
            raise ValueError("Location not found")
        
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
        
        return {
            'lat': round(location.latitude, 4),
            'lon': round(location.longitude, 4),
            'tz': timezone_str,
            'address': location.address
        }
    except Exception as e:
        raise ValueError(f"Geocoding error: {str(e)}")

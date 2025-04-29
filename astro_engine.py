import swisseph as swe
from datetime import datetime
import geopy
from geopy.geocoders import Nominatim
import pytz

# Set ephemeris path to swisseph files (or default)
swe.set_ephe_path('/usr/share/ephe')  # adjust if needed on your system

# Helper to get lat/lon
def get_lat_lon(place_name):
    geolocator = Nominatim(user_agent="vedic_astro_app")
    location = geolocator.geocode(place_name)
    return (location.latitude, location.longitude)

# Calculate Lagna and planetary positions
def calculate_chart(dob, tob, pob):
    # Get lat/lon
    latitude, longitude = get_lat_lon(pob)
    
    # Combine date and time
    birth_dt = datetime.strptime(f"{dob} {tob}", "%d-%m-%Y %I:%M %p")
    
    # Convert local to UTC
    timezone = pytz.timezone('Asia/Kolkata')  # adjust if needed
    birth_dt_utc = timezone.localize(birth_dt).astimezone(pytz.utc)
    
    julday = swe.julday(birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day, 
                        birth_dt_utc.hour + birth_dt_utc.minute / 60.0)
    
    # Calculate ascendant (Lagna)
    ascendant = swe.houses_ex(julday, latitude, longitude, b'A')[0][0]
    
    # Calculate planets
    planets = {}
    planet_names = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    planet_ids = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN, swe.MEAN_NODE]

    for idx, pid in enumerate(planet_ids):
        lon, _ = swe.calc_ut(julday, pid)
        if idx == 7:  # Rahu/Ketu special
            rahu = lon[0]
            ketu = (rahu + 180) % 360
            planets['Rahu'] = rahu
            planets['Ketu'] = ketu
        else:
            planets[planet_names[idx]] = lon[0]
    
    return {
        "ascendant": ascendant,
        "planets": planets,
        "latitude": latitude,
        "longitude": longitude,
        "julday": julday
    }

# Calculate Mahadasha and Antardasha
def get_current_dasha(julday):
    # Get Moon position
    moon_lon, _ = swe.calc_ut(julday, swe.MOON)
    
    # Nakshatra calculation
    nakshatra = moon_lon[0] / (360 / 27)
    nakshatra_index = int(nakshatra)
    
    # Vimshottari dasha sequence
    dasha_sequence = [
        'Ketu', 'Venus', 'Sun', 'Moon', 'Mars',
        'Rahu', 'Jupiter', 'Saturn', 'Mercury'
    ]
    
    # Find Mahadasha lord
    mahadasha_lord = dasha_sequence[(nakshatra_index % 9)]
    
    # Simplified (real Dasha timing calculation can be added later)
    antardasha_lord = "To be calculated"  # for now

    return {
        "current_mahadasha": mahadasha_lord,
        "current_antardasha": antardasha_lord
    }

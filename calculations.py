import swisseph as swe
import pytz
from datetime import datetime
from .astro_constants import PLANET_STRENGTHS, SIGN_NAMES
from .geo_utils import get_geo_details
from .dasha_calculator import calculate_vimshottari_dasha

def calculate_planetary_strength(planet_name, planet_sign):
    """Determine if planet is exalted or debilitated"""
    if planet_name not in PLANET_STRENGTHS:
        return ''
    
    strength = PLANET_STRENGTHS[planet_name]
    if planet_sign == strength['exalted']:
        return 'E'
    elif planet_sign == strength['debilitated']:
        return 'D'
    return ''

def calculate_vedic_chart(dob, tob, pob):
    """Calculate standard North Indian chart with all corrections"""
    try:
        # Get geographic details
        geo = get_geo_details(pob)
        print(f"\n📍 Location: {geo['address']}")
        print(f"   Coordinates: {geo['lat']}°N, {geo['lon']}°E")
        print(f"   Timezone: {geo['tz']}")

        # Convert to datetime with timezone
        local_tz = pytz.timezone(geo['tz'])
        birth_dt = local_tz.localize(datetime.strptime(f"{dob} {tob}", "%d-%m-%Y %I:%M %p"))
        utc_dt = birth_dt.astimezone(pytz.utc)
        
        # Calculate Julian day
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                        utc_dt.hour + utc_dt.minute/60 + utc_dt.second/3600)

        # 1. Calculate Lagna and houses
        houses = swe.houses(jd, geo['lat'], geo['lon'], b'W')[0]  # Whole sign houses
        lagna_pos = houses[0]
        lagna_sign = int(lagna_pos // 30) + 1
        lagna_degree = round(lagna_pos % 30, 2)

        # 2. Calculate planetary positions
        planets = {
            'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS,
            'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER, 'Venus': swe.VENUS,
            'Saturn': swe.SATURN, 'Rahu': swe.MEAN_NODE, 'Ketu': swe.MEAN_NODE
        }

        planet_data = {}
        for name, num in planets.items():
            # Get precise position (true nodes for Rahu/Ketu)
            flags = swe.FLG_SWIEPH | (swe.FLG_TRUEPOS if name in ['Rahu', 'Ketu'] else 0)
            pos = swe.calc_ut(jd, num, flags)[0][0]
            
            # Convert to sidereal
            ayanamsa = swe.get_ayanamsa(jd)
            sid_pos = (pos - ayanamsa) % 360
            sign = int(sid_pos // 30) + 1
            degree = round(sid_pos % 30, 2)
            
            # House assignment
            house = (sign - lagna_sign) % 12 + 1
            
            # Retrograde and strength
            retrograde = swe.calc_ut(jd, num, flags)[0][3] < 0
            strength = calculate_planetary_strength(name, sign)
            
            planet_data[name] = {
                'position': sid_pos,
                'sign': sign,
                'degree': degree,
                'house': house,
                'retrograde': retrograde,
                'strength': strength
            }

        # 3. Adjust Rahu/Ketu to be exactly 180° apart
        planet_data['Ketu']['position'] = (planet_data['Rahu']['position'] + 180) % 360
        planet_data['Ketu']['sign'] = int(planet_data['Ketu']['position'] // 30) + 1
        planet_data['Ketu']['degree'] = round(planet_data['Ketu']['position'] % 30, 2)
        planet_data['Ketu']['house'] = (planet_data['Ketu']['sign'] - lagna_sign) % 12 + 1
        planet_data['Ketu']['strength'] = calculate_planetary_strength('Ketu', planet_data['Ketu']['sign'])

        # 4. Calculate Dasha periods - THIS IS THE CRITICAL FIX
        # In the planet calculation section:
        # After calculating planetary positions:
        # After calculating planetary positions:
        moon_long = planet_data['Moon']['position'] % 360
        print(f"\n=== MOON POSITION VERIFICATION ===")
        print(f"Absolute Moon longitude: {planet_data['Moon']['position']}°")
        print(f"Normalized Moon longitude: {moon_long}°")
        print(f"Moon in {SIGN_NAMES[planet_data['Moon']['sign']-1]} sign")
        print(f"Moon degree: {planet_data['Moon']['degree']}°")
        print(f"Moon house: {planet_data['Moon']['house']}")

        dashas = calculate_vimshottari_dasha(birth_dt, moon_long)
        return {
            'planets': planet_data,
            'lagna': {
                'position': lagna_pos,
                'sign': lagna_sign,
                'degree': lagna_degree
            },
            'houses': houses,
            'geo': geo,
            'datetime': {
                'local': birth_dt.strftime("%d-%m-%Y %I:%M %p"),
                'utc': utc_dt.strftime("%d-%m-%Y %H:%M UTC")
            },
            'dashas': dashas  # Now properly defined
        }

    except Exception as e:
        import traceback
        print(f"\nDEBUG TRACEBACK: {traceback.format_exc()}")  # Detailed error
        raise ValueError(f"Chart calculation error: {str(e)}")
from datetime import datetime, timedelta
import pytz
from .astro_constants import DASHA_PERIODS, DASHA_ORDER, SIGN_NAMES,PLANET_COLORS,PLANET_STRENGTHS

def calculate_vimshottari_dasha(birth_dt, moon_longitude):
    """Accurate Vimshottari Dasha calculation that properly covers current date"""
    print("\n=== DASHA CALCULATION DEBUG ===")
    print(f"Birth Date (UTC): {birth_dt}")
    print(f"Moon Longitude: {moon_longitude}°")

    # Constants
    NAKSHATRA_LENGTH = 13.333333333333334  # 13°20'
    TOTAL_YEARS = 120  # Total Vimshottari cycle
    current_date = datetime.now(pytz.utc)
    print(f"Current Date (UTC): {current_date}")

    # Calculate nakshatra and elapsed time
    nakshatra_num = int(moon_longitude / NAKSHATRA_LENGTH)
    remainder = moon_longitude % NAKSHATRA_LENGTH
    current_md_planet = DASHA_ORDER[nakshatra_num % 9]
    md_period = DASHA_PERIODS[current_md_planet]
    elapsed_in_dasha = (remainder / NAKSHATRA_LENGTH) * md_period

    print(f"\nMoon in nakshatra {nakshatra_num + 1} ({current_md_planet} mahadasha)")
    print(f"Elapsed in current dasha: {elapsed_in_dasha:.2f} years")

    # Calculate the complete dasha sequence until we cover current date
    dashas = []
    planet_index = nakshatra_num % 9
    period_start = birth_dt - timedelta(days=elapsed_in_dasha*365.25)
    
    # Calculate until we have periods covering current date + buffer
    while True:
        planet = DASHA_ORDER[planet_index % 9]
        period = DASHA_PERIODS[planet]
        period_end = period_start + timedelta(days=period*365.25)

        # Mahadasha period (your original working logic)
        dashas.append({
            'type': 'Mahadasha',
            'planet': planet,
            'start': period_start,
            'end': period_end,
            'duration_years': period
        })

        print(f"\nMahadasha: {planet} ({period} years)")
        print(f"From: {period_start} to {period_end}")
        print(f"Current date in range? {period_start <= current_date < period_end}")

        # Calculate Antardashas for ALL Mahadashas (not just current)
        ad_order = DASHA_ORDER[planet_index:] + DASHA_ORDER[:planet_index]
        ad_start = period_start
        
        for ad_planet in ad_order:
            ad_period = (DASHA_PERIODS[ad_planet] * period) / TOTAL_YEARS
            ad_end = ad_start + timedelta(days=ad_period*365.25)
            
            is_current_ad = (ad_start <= current_date < ad_end)
            
            dashas.append({
                'type': 'Antardasha',
                'planet': ad_planet,
                'start': ad_start,
                'end': ad_end,
                'duration_years': ad_period,
                'parent': planet,
                'is_current': is_current_ad  # Flag for current antardasha
            })
            
            print(f"  Antardasha: {ad_planet} ({ad_period:.2f} years)")
            print(f"  From: {ad_start} to {ad_end}")
            print(f"  Current AD? {is_current_ad}")

            # Calculate Pratyantardashas ONLY if this is current Antardasha
            if is_current_ad:
                pd_start = ad_start
                for pd_planet in ad_order:
                    pd_period = (DASHA_PERIODS[pd_planet] * ad_period) / TOTAL_YEARS
                    pd_end = pd_start + timedelta(days=pd_period*365.25)
                    
                    dashas.append({
                        'type': 'Pratyantardasha',
                        'planet': pd_planet,
                        'start': pd_start,
                        'end': pd_end,
                        'duration_years': pd_period,
                        'parent': ad_planet,
                        'is_current': (pd_start <= current_date < pd_end)
                    })
                    
                    print(f"    Pratyantardasha: {pd_planet} ({pd_period:.2f} years)")
                    print(f"    From: {pd_start} to {pd_end}")
                    print(f"    Current PD? {pd_start <= current_date < pd_end}")
                    
                    pd_start = pd_end
            
            ad_start = ad_end

        # Break if we've calculated enough periods
        if period_end > current_date + timedelta(days=365*5):  # 5 year buffer
            break

        period_start = period_end
        planet_index += 1

    return dashas


def get_dasha_display_text(dashas, selected_type, current_date):
    """Find the current running period with exact date comparison"""
    current_date = current_date.astimezone(pytz.utc)
    print(f"\nChecking for current {selected_type} at {current_date}")

    # First pass: Check explicitly marked current periods
    for d in dashas:
        if d.get('is_current', False) and d['type'].lower() == selected_type.lower():
            start = d['start'].astimezone(pytz.utc) if d['start'].tzinfo else pytz.utc.localize(d['start'])
            end = d['end'].astimezone(pytz.utc) if d['end'].tzinfo else pytz.utc.localize(d['end'])
            duration = (end - current_date).days/365.25
            
            if d['type'] == 'Mahadasha':
                return (f"Current Mahadasha: {d['planet']}\n"
                       f"From: {start.strftime('%d-%m-%Y')} to {end.strftime('%d-%m-%Y')}\n"
                       f"Remaining: {duration:.2f} years")
            
            elif d['type'] == 'Antardasha':
                return (f"Current Antardasha: {d['planet']} in {d['parent']} MD\n"
                       f"From: {start.strftime('%d-%m-%Y')} to {end.strftime('%d-%m-%Y')}\n"
                       f"Remaining: {duration:.2f} years")
            
            elif d['type'] == 'Pratyantardasha':
                return (f"Current Pratyantardasha: {d['planet']} in {d['parent']} AD\n"
                       f"From: {start.strftime('%d-%m-%Y')} to {end.strftime('%d-%m-%Y')}\n"
                       f"Remaining: {duration:.2f} years")

    # Fallback: Check all periods if no marked current period found
    for d in dashas:
        if d['type'].lower() != selected_type.lower():
            continue

        start = d['start'].astimezone(pytz.utc) if d['start'].tzinfo else pytz.utc.localize(d['start'])
        end = d['end'].astimezone(pytz.utc) if d['end'].tzinfo else pytz.utc.localize(d['end'])

        if start <= current_date < end:
            duration = (end - current_date).days/365.25
            return (f"Current {d['type']}: {d['planet']} "
                   f"({start.strftime('%d-%m-%Y')} to {end.strftime('%d-%m-%Y')}) "
                   f"[{duration:.1f} years remaining]")

    return f"No current {selected_type} found"

def display_dashas(dashas):
    """Display complete dasha information"""
    current_date = datetime.now(pytz.utc)
    
    print("\n=== Vimshottari Dasha Periods ===")
    print(f"Current Date: {current_date.strftime('%d-%m-%Y %H:%M %Z')}")
    
    # Current periods
    print("\nCURRENT PERIODS:")
    print(f"  {get_dasha_display_text(dashas, 'Mahadasha', current_date)}")
    print(f"  {get_dasha_display_text(dashas, 'Antardasha', current_date)}")
    print(f"  {get_dasha_display_text(dashas, 'Pratyantardasha', current_date)}")
    
    # Upcoming Mahadashas
    print("\nUPCOMING MAHADASHAS:")
    mahadashas = [d for d in dashas if d['type'] == 'Mahadasha'][1:4]  # Next 3
    for md in mahadashas:
        print(f"  {md['planet']}: {md['start'].strftime('%d-%m-%Y')} to {md['end'].strftime('%d-%m-%Y')} ({md['duration_years']:.2f} years)")
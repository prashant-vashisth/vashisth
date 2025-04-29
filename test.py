def calculate_vimshottari_dasha(birth_dt, moon_longitude):
    """Complete Vimshottari Dasha calculation with all three levels"""
    print("\n=== DASHA CALCULATION DEBUG ===")
    print(f"Birth Date (UTC): {birth_dt}")
    print(f"Moon Longitude: {moon_longitude}°")
    
    # Constants
    NAKSHATRA_LENGTH = 13.333333333333334  # 13°20'
    TOTAL_YEARS = 120  # Vimshottari cycle
    current_date = datetime.now(pytz.utc)
    print(f"Current Date (UTC): {current_date}")

    # Calculate nakshatra and initial periods
    nakshatra_num = int(moon_longitude / NAKSHATRA_LENGTH)
    remainder = moon_longitude % NAKSHATRA_LENGTH
    current_md_planet = DASHA_ORDER[nakshatra_num % 9]
    md_period = DASHA_PERIODS[current_md_planet]
    elapsed_in_dasha = (remainder / NAKSHATRA_LENGTH) * md_period
    elapsed_in_days = elapsed_in_dasha * 365.25  # Convert years to days

    print(f"\nInitial Calculation:")
    print(f"Moon in nakshatra {nakshatra_num + 1} ({current_md_planet} mahadasha)")
    print(f"Elapsed in current dasha: {elapsed_in_days:.2f} days ({elapsed_in_dasha:.2f} years)")

    # Calculate complete dasha sequence
    dashas = []
    planet_index = nakshatra_num % 9
    period_start = birth_dt - timedelta(days=elapsed_in_days)
    
    # Calculate until we cover current date + buffer
    while len(dashas) < 12:  # Enough to cover 120+ years
        planet = DASHA_ORDER[planet_index % 9]
        period = DASHA_PERIODS[planet]
        md_end = period_start + timedelta(days=period*365.25)

        # Mahadasha period
        md_data = {
            'type': 'Mahadasha',
            'planet': planet,
            'start': period_start,
            'end': md_end,
            'duration_years': period
        }
        dashas.append(md_data)
        print(f"\nMahadasha: {planet} ({period} years)")
        print(f"From: {period_start} to {md_end}")

        # Calculate Antardashas for this Mahadasha
        ad_order = DASHA_ORDER[planet_index:] + DASHA_ORDER[:planet_index]
        ad_start = period_start
        
        for ad_planet in ad_order:
            ad_period = (DASHA_PERIODS[ad_planet] * period) / TOTAL_YEARS
            ad_end = ad_start + timedelta(days=ad_period*365.25)
            
            ad_data = {
                'type': 'Antardasha',
                'planet': ad_planet,
                'start': ad_start,
                'end': ad_end,
                'duration_years': ad_period,
                'parent': planet
            }
            dashas.append(ad_data)
            print(f"  Antardasha: {ad_planet} ({ad_period:.2f} years)")
            print(f"  From: {ad_start} to {ad_end}")

            # Calculate Pratyantardashas for CURRENT Antardasha only
            if planet == current_md_planet and ad_start <= current_date < ad_end:
                pd_start = ad_start
                for pd_planet in ad_order:
                    pd_period = (DASHA_PERIODS[pd_planet] * ad_period) / TOTAL_YEARS
                    pd_end = pd_start + timedelta(days=pd_period*365.25)
                    
                    pd_data = {
                        'type': 'Pratyantardasha',
                        'planet': pd_planet,
                        'start': pd_start,
                        'end': pd_end,
                        'duration_years': pd_period,
                        'parent': ad_planet
                    }
                    dashas.append(pd_data)
                    print(f"    Pratyantardasha: {pd_planet} ({pd_period:.2f} years)")
                    print(f"    From: {pd_start} to {pd_end}")
                    
                    pd_start = pd_end
            
            ad_start = ad_end
        
        # Move to next mahadasha
        period_start = md_end
        planet_index += 1
        
        # Stop if we've calculated enough periods
        if md_end > current_date + timedelta(days=365*5):
            break

    return dashas


def get_dasha_display_text(dashas, selected_type, current_date):
    """Find current running period with precise date matching"""
    current_date = current_date.astimezone(pytz.utc)
    print(f"\nChecking for current {selected_type} at {current_date}")

    for d in dashas:
        if d['type'].lower() != selected_type.lower():
            continue

        start = d['start'].astimezone(pytz.utc) if d['start'].tzinfo else pytz.utc.localize(d['start'])
        end = d['end'].astimezone(pytz.utc) if d['end'].tzinfo else pytz.utc.localize(d['end'])

        print(f"\nPeriod: {d['planet']} {d['type']}")
        print(f"Range: {start} to {end}")
        print(f"Current date in range? {start <= current_date < end}")

        if start <= current_date < end:
            duration = d['duration_years']
            remaining = (end - current_date).days/365.25
            
            if d['type'] == 'Mahadasha':
                return (f"Current Mahadasha: {d['planet']}\n"
                       f"Period: {start.strftime('%d-%m-%Y')} to {end.strftime('%d-%m-%Y')}\n"
                       f"Remaining: {remaining:.2f} years")
            
            elif d['type'] == 'Antardasha':
                return (f"Current Antardasha: {d['planet']} in {d['parent']} MD\n"
                       f"Period: {start.strftime('%d-%m-%Y')} to {end.strftime('%d-%m-%Y')}\n"
                       f"Remaining: {remaining:.2f} years")
            
            elif d['type'] == 'Pratyantardasha':
                return (f"Current Pratyantardasha: {d['planet']} in {d['parent']} AD\n"
                       f"Period: {start.strftime('%d-%m-%Y')} to {end.strftime('%d-%m-%Y')}\n"
                       f"Remaining: {remaining:.2f} years")

    return f"No current {selected_type} period found"
import pytz
import swisseph as swe
from utils.calculations import calculate_vedic_chart
from utils.dasha_calculator import display_dashas
from utils.chart_plotter import plot_vedic_chart
from utils.astro_constants import SIGN_NAMES

def main(test_mode=False):
    print("PROFESSIONAL VEDIC ASTROLOGY CALCULATOR")
    print("="*50)
    
    if test_mode:
        # Hardcoded test values
        dob = "14-01-1984"
        tob = "03:45 PM"
        pob = "Amroha, India"
        print(f"\nTEST MODE ACTIVATED WITH:")
        print(f"Date of Birth: {dob}")
        print(f"Time of Birth: {tob}")
        print(f"Place of Birth: {pob}\n")
    else:
        dob = input("Date of Birth (DD-MM-YYYY): ")
        tob = input("Time of Birth (HH:MM AM/PM): ")
        pob = input("Place of Birth (City, Country): ")

    try:
        # Calculate the chart
        chart_data = calculate_vedic_chart(dob, tob, pob)
        
        if not chart_data:
            raise ValueError("Failed to calculate chart data")

        # Display basic chart info
        print("\n=== VEDIC CHART SUMMARY ===")
        print(f"Lagna (Ascendant): {chart_data['lagna']['sign']}-{SIGN_NAMES[chart_data['lagna']['sign']-1]} {chart_data['lagna']['degree']:.1f}°")
        
        # Display planetary positions
        print("\nPLANETARY POSITIONS:")
        for planet, data in chart_data['planets'].items():
            retr = " (R)" if data['retrograde'] else ""
            strength = f" {data['strength']}" if data['strength'] else ""
            print(f"{planet:<8}: {data['degree']:.1f}° in {data['sign']}-{SIGN_NAMES[data['sign']-1]} (House {data['house']}){strength}{retr}")

        # Display Dasha periods
        display_dashas(chart_data['dashas'])
        
        # Plot the chart
        plot_vedic_chart(chart_data)
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("Please check your inputs and try again.")

if __name__ == "__main__":
    # Initialize Swiss Ephemeris settings
    swe.set_ephe_path()
    swe.set_sid_mode(swe.SIDM_LAHIRI)  # Lahiri ayanamsa
    swe.set_topo(0, 0, 0)  # Ground level observation
    
    # Run in test mode (change to False for normal operation)
    main(test_mode=True)
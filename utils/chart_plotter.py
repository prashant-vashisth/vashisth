import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime
import pytz
from .astro_constants import SIGN_NAMES, PLANET_COLORS

# Check for Dropdown widget availability
try:
    from matplotlib.widgets import Dropdown
    HAS_DROPDOWN = True
except ImportError:
    HAS_DROPDOWN = False
    print("Note: Your matplotlib version doesn't support Dropdown widget. Using text display only.")

def plot_vedic_chart(chart_data):
    """Create professional North Indian style chart with dasha info panel"""
    planets = chart_data['planets']
    lagna_sign = chart_data['lagna']['sign']
    current_date = datetime.now(pytz.utc)
    
    # Get current dasha periods
    dashas = chart_data['dashas']
    current_md = next((d for d in dashas if d['type'] == 'Mahadasha' and 
                      d['start'] <= current_date < d['end']), None)
    current_ad = next((d for d in dashas if d['type'] == 'Antardasha' and 
                      d['start'] <= current_date < d['end']), None)
    current_pd = next((d for d in dashas if d['type'] == 'Pratyantardasha' and 
                      d['start'] <= current_date < d['end']), None)

    # Create figure with saffron background
    fig = plt.figure(figsize=(16, 10), facecolor='#FF9933')  # Saffron background
    plt.style.use('default')
    
    # Main chart axes (smaller and left-aligned)
    ax = fig.add_axes([0.05, 0.1, 0.6, 0.8], facecolor='#FFF8E7')  # Light saffron
    
    # Dasha info panel (right side)
    dasha_ax = fig.add_axes([0.7, 0.1, 0.25, 0.8], facecolor='#FFCC66')  # Darker saffron
    dasha_ax.axis('off')
    
    # Chart configuration
    house_width = 2.5  # Reduced from original 3
    house_height = 2    # Reduced from original 2.5
    houses_per_row = 4
    
    # Draw houses and place planets (your existing code)
    for house_num in range(1, 13):
        row = (house_num - 1) // houses_per_row
        col = (house_num - 1) % houses_per_row
        x = col * house_width
        y = (2 - row) * house_height
        
        # House rectangle with alternating colors
        rect = patches.Rectangle(
            (x, y), house_width, house_height,
            linewidth=2, edgecolor='#333333',
            facecolor='#FFE4B5' if house_num % 2 == 1 else '#FFD700'  # Saffron variants
        )
        ax.add_patch(rect)
        
        # House label with sign name
        sign_num = (lagna_sign + house_num - 2) % 12
        ax.text(x + house_width/2, y + house_height - 0.3, 
                f"House {house_num}\n{SIGN_NAMES[sign_num]}", 
                ha='center', va='center', fontweight='bold', fontsize=9)
        
        # Place planets in this house (your existing code)
        planets_in_house = [p for p in planets.values() if p['house'] == house_num]
        
        for i, planet in enumerate(planets_in_house):
            planet_x = x + house_width/2
            planet_y = y + house_height - 0.8 - (i * 0.5)
            pname = [k for k,v in planets.items() if v == planet][0]
            
            # Planet marker with retrograde indicator
            marker = 'R' if planet['retrograde'] else 'o'
            ax.plot(planet_x, planet_y, marker, markersize=12, 
                   color=PLANET_COLORS[pname], markeredgecolor='black')
            
            # Planet label with degree and strength indicators
            deg_str = f"{planet['degree']:.1f}°" if planet['degree'] % 1 != 0 else f"{int(planet['degree'])}°"
            strength_indicator = planet['strength']
            if planet['retrograde']:
                strength_indicator += 'R' if not strength_indicator else '/R'
            
            label_text = f"{pname[:3]} {deg_str}"
            if strength_indicator:
                label_text += f" ({strength_indicator})"
            
            ax.text(planet_x, planet_y, 
                   label_text, 
                   ha='center', va='center', fontsize=8,
                   bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    # Chart title and info
    ax.set_xlim(0, houses_per_row * house_width)
    ax.set_ylim(0, 3 * house_height)
    ax.axis('off')
    
    title_text = (
        f"North Indian Vedic Chart\n"
        f"Lagna: {SIGN_NAMES[lagna_sign-1]} {chart_data['lagna']['degree']:.1f}° | "
        f"Born: {chart_data['datetime']['local']} ({chart_data['datetime']['utc']})\n"
        f"Location: {chart_data['geo']['address']} ({chart_data['geo']['lat']}°N, {chart_data['geo']['lon']}°E)"
    )
    ax.set_title(title_text, pad=20, fontsize=12, color='#8B0000')  # Dark red
    
    # Dasha information panel
    dasha_title = dasha_ax.text(0.5, 0.95, "Current Dasha Periods", 
                               ha='center', va='center', fontsize=14, fontweight='bold', color='#8B0000')
    
    # Calculate remaining times
    def get_remaining(end_date):
        remaining_days = (end_date - current_date).days
        years = int(remaining_days / 365.25)
        months = int((remaining_days % 365.25) / 30.44)
        days = int((remaining_days % 365.25) % 30.44)
        return f"{years}y {months}m {days}d"
    
    y_pos = 0.85
    if current_md:
        remaining = get_remaining(current_md['end'])
        md_text = (f"Mahadasha: {current_md['planet']}\n"
                  f"Period: {current_md['start'].strftime('%d-%m-%Y')} to {current_md['end'].strftime('%d-%m-%Y')}\n"
                  f"Remaining: {remaining}")
        dasha_ax.text(0.5, y_pos, md_text, ha='center', va='top', fontsize=11,
                     bbox=dict(facecolor='#FFD700', alpha=0.7), transform=dasha_ax.transAxes)
        y_pos -= 0.15
    
    if current_ad:
        remaining = get_remaining(current_ad['end'])
        ad_text = (f"Antardasha: {current_ad['planet']} in {current_ad['parent']} MD\n"
                  f"Period: {current_ad['start'].strftime('%d-%m-%Y')} to {current_ad['end'].strftime('%d-%m-%Y')}\n"
                  f"Remaining: {remaining}")
        dasha_ax.text(0.5, y_pos, ad_text, ha='center', va='top', fontsize=11,
                     bbox=dict(facecolor='#FFA500', alpha=0.7), transform=dasha_ax.transAxes)
        y_pos -= 0.15
    
    if current_pd:
        remaining = get_remaining(current_pd['end'])
        pd_text = (f"Pratyantardasha: {current_pd['planet']} in {current_pd['parent']} AD\n"
                  f"Period: {current_pd['start'].strftime('%d-%m-%Y')} to {current_pd['end'].strftime('%d-%m-%Y')}\n"
                  f"Remaining: {remaining}")
        dasha_ax.text(0.5, y_pos, pd_text, ha='center', va='top', fontsize=11,
                     bbox=dict(facecolor='#FF8C00', alpha=0.7), transform=dasha_ax.transAxes)
    
    # Add legend
    legend_text = "Indicators: E=Exalted, D=Debilitated, R=Retrograde"
    ax.text(0.5, -0.1, legend_text, 
           ha='center', va='center', transform=ax.transAxes, fontsize=10, color='#8B0000')
    
    plt.show()

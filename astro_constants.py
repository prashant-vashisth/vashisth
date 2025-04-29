# Planetary exaltation and debilitation points (sign numbers)
PLANET_STRENGTHS = {
    'Sun': {'exalted': 1, 'debilitated': 7},    # Aries exalted, Libra debilitated
    'Moon': {'exalted': 2, 'debilitated': 8},   # Taurus exalted, Scorpio debilitated
    'Mars': {'exalted': 4, 'debilitated': 10},  # Cancer exalted, Capricorn debilitated
    'Mercury': {'exalted': 6, 'debilitated': 12}, # Virgo exalted, Pisces debilitated
    'Jupiter': {'exalted': 5, 'debilitated': 11}, # Cancer exalted, Capricorn debilitated
    'Venus': {'exalted': 12, 'debilitated': 6},  # Pisces exalted, Virgo debilitated
    'Saturn': {'exalted': 7, 'debilitated': 1},  # Libra exalted, Aries debilitated
    'Rahu': {'exalted': 3, 'debilitated': 9},    # Gemini exalted, Sagittarius debilitated
    'Ketu': {'exalted': 9, 'debilitated': 3}     # Sagittarius exalted, Gemini debilitated
}

# Vimshottari Dasha periods (in years)
DASHA_PERIODS = {
    'Ketu': 7,
    'Venus': 20,
    'Sun': 6,
    'Moon': 10,
    'Mars': 7,
    'Rahu': 18,
    'Jupiter': 16,
    'Saturn': 19,
    'Mercury': 17
}

# Correct order of planets in Vimshottari Dasha
DASHA_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']

# Sign names
SIGN_NAMES = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"
]

# Planet colors for chart display
PLANET_COLORS = {
    'Sun': '#FFD700', 'Moon': '#C0C0C0', 'Mars': '#FF4500',
    'Mercury': '#32CD32', 'Jupiter': '#FF8C00', 'Venus': '#FFFFFF',
    'Saturn': '#1E90FF', 'Rahu': '#000000', 'Ketu': '#8B4513'
}
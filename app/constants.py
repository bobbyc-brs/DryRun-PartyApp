"""
Copyright (C) 2025 Brighter Sight
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

For inquiries, contact: Info@BrighterSight.ca
"""

"""
Constants used throughout the Party Drink Tracker application.

This module centralizes all constants and magic numbers used in the application,
making them easier to maintain, document, and modify.
"""

# BAC Calculation Constants
ETHANOL_DENSITY_G_PER_ML = 0.789  # Density of ethanol in g/ml
AVERAGE_GENDER_CONSTANT = 0.62  # Average of male (0.68) and female (0.55) constants
MALE_GENDER_CONSTANT = 0.68  # Widmark factor for males
FEMALE_GENDER_CONSTANT = 0.55  # Widmark factor for females
LBS_TO_KG_CONVERSION = 0.453592  # Conversion factor from pounds to kilograms
BAC_METABOLISM_RATE = 0.015  # Average metabolism rate in % per hour
BAC_LEGAL_LIMIT = 0.08  # Legal BAC limit in most jurisdictions (%)
BAC_DISPLAY_CAP = 0.5  # Maximum BAC to display (for visualization purposes)
BAC_DECIMAL_PRECISION = 3  # Number of decimal places for BAC display

# Time Constants
BAC_HISTORY_HOURS = 6  # Number of hours to show in BAC history charts
BAC_INTERVAL_MINUTES = 15  # Interval between BAC calculation points in minutes

# UI Constants
CHART_HEIGHT_INDIVIDUAL = 500  # Height of individual BAC charts in pixels
CHART_HEIGHT_GROUP = 600  # Height of group BAC charts in pixels
DRINK_MARKER_SIZE = 10  # Size of drink markers on BAC charts

# Server Constants
GUEST_PORT = 4000  # Port for guest interface
HOST_PORT = 4001  # Port for host interface

# File Paths
DEFAULT_GUEST_LIST_PATH = "~/guest-list"  # Default path to guest list file
DEFAULT_DRINK_LIST_PATH = "~/drinks/drink-list.csv"  # Default path to drink list file
DEFAULT_DRINKS_DIR = "~/drinks"  # Default path to drinks directory

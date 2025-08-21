"""
Country-based scoring configuration for fair global rewards.

Based on economic factors, data market maturity, and purchasing power parity
to ensure equitable rewards across different regions.
"""

from typing import Dict, Any
import logging

# Country tier definitions based on GDP per capita and data market maturity
COUNTRY_TIERS = {
    # Tier 1 - Premium Markets (1.0x base multiplier)
    # High GDP per capita + mature financial markets
    'US': {'tier': 1, 'name': 'United States', 'gdp_per_capita': 70000, 'data_premium': 'high'},
    'CA': {'tier': 1, 'name': 'Canada', 'gdp_per_capita': 52000, 'data_premium': 'high'},
    'CH': {'tier': 1, 'name': 'Switzerland', 'gdp_per_capita': 95000, 'data_premium': 'high'},
    'NO': {'tier': 1, 'name': 'Norway', 'gdp_per_capita': 85000, 'data_premium': 'high'},
    'AU': {'tier': 1, 'name': 'Australia', 'gdp_per_capita': 55000, 'data_premium': 'high'},
    'DK': {'tier': 1, 'name': 'Denmark', 'gdp_per_capita': 68000, 'data_premium': 'high'},
    'LU': {'tier': 1, 'name': 'Luxembourg', 'gdp_per_capita': 130000, 'data_premium': 'high'},
    'SG': {'tier': 1, 'name': 'Singapore', 'gdp_per_capita': 65000, 'data_premium': 'high'},
    'IE': {'tier': 1, 'name': 'Ireland', 'gdp_per_capita': 85000, 'data_premium': 'high'},
    'QA': {'tier': 1, 'name': 'Qatar', 'gdp_per_capita': 70000, 'data_premium': 'high'},
    'AE': {'tier': 1, 'name': 'United Arab Emirates', 'gdp_per_capita': 45000, 'data_premium': 'high'},
    
    # Tier 2 - Developed Markets (0.8x base multiplier)
    # Strong economies but slightly lower data premiums
    'GB': {'tier': 2, 'name': 'United Kingdom', 'gdp_per_capita': 46000, 'data_premium': 'medium-high'},
    'DE': {'tier': 2, 'name': 'Germany', 'gdp_per_capita': 48000, 'data_premium': 'medium-high'},
    'FR': {'tier': 2, 'name': 'France', 'gdp_per_capita': 43000, 'data_premium': 'medium-high'},
    'JP': {'tier': 2, 'name': 'Japan', 'gdp_per_capita': 40000, 'data_premium': 'medium-high'},
    'KR': {'tier': 2, 'name': 'South Korea', 'gdp_per_capita': 35000, 'data_premium': 'medium-high'},
    'NL': {'tier': 2, 'name': 'Netherlands', 'gdp_per_capita': 53000, 'data_premium': 'medium-high'},
    'SE': {'tier': 2, 'name': 'Sweden', 'gdp_per_capita': 55000, 'data_premium': 'medium-high'},
    'AT': {'tier': 2, 'name': 'Austria', 'gdp_per_capita': 48000, 'data_premium': 'medium-high'},
    'BE': {'tier': 2, 'name': 'Belgium', 'gdp_per_capita': 47000, 'data_premium': 'medium-high'},
    'FI': {'tier': 2, 'name': 'Finland', 'gdp_per_capita': 49000, 'data_premium': 'medium-high'},
    'IT': {'tier': 2, 'name': 'Italy', 'gdp_per_capita': 32000, 'data_premium': 'medium-high'},
    'ES': {'tier': 2, 'name': 'Spain', 'gdp_per_capita': 28000, 'data_premium': 'medium-high'},
    'IL': {'tier': 2, 'name': 'Israel', 'gdp_per_capita': 43000, 'data_premium': 'medium-high'},
    'NZ': {'tier': 2, 'name': 'New Zealand', 'gdp_per_capita': 42000, 'data_premium': 'medium-high'},
    'CZ': {'tier': 2, 'name': 'Czech Republic', 'gdp_per_capita': 25000, 'data_premium': 'medium-high'},
    'PT': {'tier': 2, 'name': 'Portugal', 'gdp_per_capita': 24000, 'data_premium': 'medium-high'},
    'GR': {'tier': 2, 'name': 'Greece', 'gdp_per_capita': 17000, 'data_premium': 'medium-high'},
    'CY': {'tier': 2, 'name': 'Cyprus', 'gdp_per_capita': 27000, 'data_premium': 'medium-high'},
    'MT': {'tier': 2, 'name': 'Malta', 'gdp_per_capita': 29000, 'data_premium': 'medium-high'},
    'IS': {'tier': 2, 'name': 'Iceland', 'gdp_per_capita': 59000, 'data_premium': 'medium-high'},
    'LI': {'tier': 2, 'name': 'Liechtenstein', 'gdp_per_capita': 180000, 'data_premium': 'medium-high'},
    'MC': {'tier': 2, 'name': 'Monaco', 'gdp_per_capita': 170000, 'data_premium': 'medium-high'},
    'SM': {'tier': 2, 'name': 'San Marino', 'gdp_per_capita': 47000, 'data_premium': 'medium-high'},
    'AD': {'tier': 2, 'name': 'Andorra', 'gdp_per_capita': 40000, 'data_premium': 'medium-high'},
    'VA': {'tier': 2, 'name': 'Vatican City', 'gdp_per_capita': 25000, 'data_premium': 'medium-high'},
    
    # Tier 3 - Emerging High (0.6x base multiplier)
    # Growing economies with developing financial sectors
    'BR': {'tier': 3, 'name': 'Brazil', 'gdp_per_capita': 8800, 'data_premium': 'medium'},
    'MX': {'tier': 3, 'name': 'Mexico', 'gdp_per_capita': 9900, 'data_premium': 'medium'},
    'TR': {'tier': 3, 'name': 'Turkey', 'gdp_per_capita': 9500, 'data_premium': 'medium'},
    'PL': {'tier': 3, 'name': 'Poland', 'gdp_per_capita': 15500, 'data_premium': 'medium'},
    'MY': {'tier': 3, 'name': 'Malaysia', 'gdp_per_capita': 11200, 'data_premium': 'medium'},
    'CL': {'tier': 3, 'name': 'Chile', 'gdp_per_capita': 15400, 'data_premium': 'medium'},
    'AR': {'tier': 3, 'name': 'Argentina', 'gdp_per_capita': 10900, 'data_premium': 'medium'},
    'RU': {'tier': 3, 'name': 'Russia', 'gdp_per_capita': 11300, 'data_premium': 'medium'},
    'CN': {'tier': 3, 'name': 'China', 'gdp_per_capita': 12500, 'data_premium': 'medium'},
    'SA': {'tier': 3, 'name': 'Saudi Arabia', 'gdp_per_capita': 23000, 'data_premium': 'medium'},
    'HR': {'tier': 3, 'name': 'Croatia', 'gdp_per_capita': 15700, 'data_premium': 'medium'},
    'EE': {'tier': 3, 'name': 'Estonia', 'gdp_per_capita': 23300, 'data_premium': 'medium'},
    'LV': {'tier': 3, 'name': 'Latvia', 'gdp_per_capita': 17900, 'data_premium': 'medium'},
    'LT': {'tier': 3, 'name': 'Lithuania', 'gdp_per_capita': 19200, 'data_premium': 'medium'},
    'SK': {'tier': 3, 'name': 'Slovakia', 'gdp_per_capita': 19200, 'data_premium': 'medium'},
    'SI': {'tier': 3, 'name': 'Slovenia', 'gdp_per_capita': 25000, 'data_premium': 'medium'},
    'HU': {'tier': 3, 'name': 'Hungary', 'gdp_per_capita': 16800, 'data_premium': 'medium'},
    'RO': {'tier': 3, 'name': 'Romania', 'gdp_per_capita': 12300, 'data_premium': 'medium'},
    'BG': {'tier': 3, 'name': 'Bulgaria', 'gdp_per_capita': 9800, 'data_premium': 'medium'},
    'UY': {'tier': 3, 'name': 'Uruguay', 'gdp_per_capita': 16200, 'data_premium': 'medium'},
    'PA': {'tier': 3, 'name': 'Panama', 'gdp_per_capita': 15600, 'data_premium': 'medium'},
    'CR': {'tier': 3, 'name': 'Costa Rica', 'gdp_per_capita': 12400, 'data_premium': 'medium'},
    'TW': {'tier': 3, 'name': 'Taiwan', 'gdp_per_capita': 33000, 'data_premium': 'medium'},
    'HK': {'tier': 3, 'name': 'Hong Kong', 'gdp_per_capita': 49000, 'data_premium': 'medium'},
    'MO': {'tier': 3, 'name': 'Macau', 'gdp_per_capita': 43000, 'data_premium': 'medium'},
    'BH': {'tier': 3, 'name': 'Bahrain', 'gdp_per_capita': 23000, 'data_premium': 'medium'},
    'KW': {'tier': 3, 'name': 'Kuwait', 'gdp_per_capita': 29000, 'data_premium': 'medium'},
    'OM': {'tier': 3, 'name': 'Oman', 'gdp_per_capita': 15000, 'data_premium': 'medium'},
    'LB': {'tier': 3, 'name': 'Lebanon', 'gdp_per_capita': 8000, 'data_premium': 'medium'},
    'GE': {'tier': 3, 'name': 'Georgia', 'gdp_per_capita': 4700, 'data_premium': 'medium'},
    'AM': {'tier': 3, 'name': 'Armenia', 'gdp_per_capita': 4200, 'data_premium': 'medium'},
    'AZ': {'tier': 3, 'name': 'Azerbaijan', 'gdp_per_capita': 4800, 'data_premium': 'medium'},
    'MD': {'tier': 3, 'name': 'Moldova', 'gdp_per_capita': 3300, 'data_premium': 'medium'},
    
    # Tier 4 - Emerging Standard (0.4x base multiplier)
    # Large populations but lower GDP per capita
    'IN': {'tier': 4, 'name': 'India', 'gdp_per_capita': 2300, 'data_premium': 'medium-low'},
    'TH': {'tier': 4, 'name': 'Thailand', 'gdp_per_capita': 7800, 'data_premium': 'medium-low'},
    'PH': {'tier': 4, 'name': 'Philippines', 'gdp_per_capita': 3500, 'data_premium': 'medium-low'},
    'EG': {'tier': 4, 'name': 'Egypt', 'gdp_per_capita': 3000, 'data_premium': 'medium-low'},
    'ZA': {'tier': 4, 'name': 'South Africa', 'gdp_per_capita': 6000, 'data_premium': 'medium-low'},
    'CO': {'tier': 4, 'name': 'Colombia', 'gdp_per_capita': 6100, 'data_premium': 'medium-low'},
    'PE': {'tier': 4, 'name': 'Peru', 'gdp_per_capita': 6700, 'data_premium': 'medium-low'},
    'ID': {'tier': 4, 'name': 'Indonesia', 'gdp_per_capita': 4300, 'data_premium': 'medium-low'},
    'MA': {'tier': 4, 'name': 'Morocco', 'gdp_per_capita': 3200, 'data_premium': 'medium-low'},
    'JO': {'tier': 4, 'name': 'Jordan', 'gdp_per_capita': 4200, 'data_premium': 'medium-low'},
    'TN': {'tier': 4, 'name': 'Tunisia', 'gdp_per_capita': 3500, 'data_premium': 'medium-low'},
    'DZ': {'tier': 4, 'name': 'Algeria', 'gdp_per_capita': 4000, 'data_premium': 'medium-low'},
    'EC': {'tier': 4, 'name': 'Ecuador', 'gdp_per_capita': 6100, 'data_premium': 'medium-low'},
    'DO': {'tier': 4, 'name': 'Dominican Republic', 'gdp_per_capita': 8500, 'data_premium': 'medium-low'},
    'GT': {'tier': 4, 'name': 'Guatemala', 'gdp_per_capita': 4900, 'data_premium': 'medium-low'},
    'SV': {'tier': 4, 'name': 'El Salvador', 'gdp_per_capita': 4300, 'data_premium': 'medium-low'},
    'HN': {'tier': 4, 'name': 'Honduras', 'gdp_per_capita': 2800, 'data_premium': 'medium-low'},
    'NI': {'tier': 4, 'name': 'Nicaragua', 'gdp_per_capita': 2100, 'data_premium': 'medium-low'},
    'JM': {'tier': 4, 'name': 'Jamaica', 'gdp_per_capita': 5300, 'data_premium': 'medium-low'},
    'UZ': {'tier': 4, 'name': 'Uzbekistan', 'gdp_per_capita': 1700, 'data_premium': 'medium-low'},
    'KZ': {'tier': 4, 'name': 'Kazakhstan', 'gdp_per_capita': 9800, 'data_premium': 'medium-low'},
    'UA': {'tier': 4, 'name': 'Ukraine', 'gdp_per_capita': 4200, 'data_premium': 'medium-low'},
    'BY': {'tier': 4, 'name': 'Belarus', 'gdp_per_capita': 6300, 'data_premium': 'medium-low'},
    'RS': {'tier': 4, 'name': 'Serbia', 'gdp_per_capita': 7400, 'data_premium': 'medium-low'},
    'BA': {'tier': 4, 'name': 'Bosnia and Herzegovina', 'gdp_per_capita': 6100, 'data_premium': 'medium-low'},
    'MK': {'tier': 4, 'name': 'North Macedonia', 'gdp_per_capita': 6100, 'data_premium': 'medium-low'},
    'AL': {'tier': 4, 'name': 'Albania', 'gdp_per_capita': 5400, 'data_premium': 'medium-low'},
    'ME': {'tier': 4, 'name': 'Montenegro', 'gdp_per_capita': 8900, 'data_premium': 'medium-low'},
    'LY': {'tier': 4, 'name': 'Libya', 'gdp_per_capita': 6000, 'data_premium': 'medium-low'},
    'IR': {'tier': 4, 'name': 'Iran', 'gdp_per_capita': 3000, 'data_premium': 'medium-low'},
    'BW': {'tier': 4, 'name': 'Botswana', 'gdp_per_capita': 7200, 'data_premium': 'medium-low'},
    'NA': {'tier': 4, 'name': 'Namibia', 'gdp_per_capita': 4500, 'data_premium': 'medium-low'},
    'SZ': {'tier': 4, 'name': 'Eswatini', 'gdp_per_capita': 4000, 'data_premium': 'medium-low'},
    'LS': {'tier': 4, 'name': 'Lesotho', 'gdp_per_capita': 1200, 'data_premium': 'medium-low'},
    'GA': {'tier': 4, 'name': 'Gabon', 'gdp_per_capita': 8500, 'data_premium': 'medium-low'},
    'GQ': {'tier': 4, 'name': 'Equatorial Guinea', 'gdp_per_capita': 8000, 'data_premium': 'medium-low'},
    'MU': {'tier': 4, 'name': 'Mauritius', 'gdp_per_capita': 11000, 'data_premium': 'medium-low'},
    'SC': {'tier': 4, 'name': 'Seychelles', 'gdp_per_capita': 15000, 'data_premium': 'medium-low'},
    'CV': {'tier': 4, 'name': 'Cape Verde', 'gdp_per_capita': 3500, 'data_premium': 'medium-low'},
    'ST': {'tier': 4, 'name': 'São Tomé and Príncipe', 'gdp_per_capita': 2100, 'data_premium': 'medium-low'},
    'MN': {'tier': 4, 'name': 'Mongolia', 'gdp_per_capita': 4100, 'data_premium': 'medium-low'},
    'KG': {'tier': 4, 'name': 'Kyrgyzstan', 'gdp_per_capita': 1200, 'data_premium': 'medium-low'},
    'TJ': {'tier': 4, 'name': 'Tajikistan', 'gdp_per_capita': 900, 'data_premium': 'medium-low'},
    'TM': {'tier': 4, 'name': 'Turkmenistan', 'gdp_per_capita': 7500, 'data_premium': 'medium-low'},
    'FJ': {'tier': 4, 'name': 'Fiji', 'gdp_per_capita': 6000, 'data_premium': 'medium-low'},
    'PG': {'tier': 4, 'name': 'Papua New Guinea', 'gdp_per_capita': 2700, 'data_premium': 'medium-low'},
    'SB': {'tier': 4, 'name': 'Solomon Islands', 'gdp_per_capita': 2300, 'data_premium': 'medium-low'},
    'VU': {'tier': 4, 'name': 'Vanuatu', 'gdp_per_capita': 3100, 'data_premium': 'medium-low'},
    'TO': {'tier': 4, 'name': 'Tonga', 'gdp_per_capita': 4800, 'data_premium': 'medium-low'},
    'WS': {'tier': 4, 'name': 'Samoa', 'gdp_per_capita': 4000, 'data_premium': 'medium-low'},
    'FM': {'tier': 4, 'name': 'Micronesia', 'gdp_per_capita': 3500, 'data_premium': 'medium-low'},
    'MH': {'tier': 4, 'name': 'Marshall Islands', 'gdp_per_capita': 4000, 'data_premium': 'medium-low'},
    'PW': {'tier': 4, 'name': 'Palau', 'gdp_per_capita': 15000, 'data_premium': 'medium-low'},
    'KI': {'tier': 4, 'name': 'Kiribati', 'gdp_per_capita': 1600, 'data_premium': 'medium-low'},
    'TV': {'tier': 4, 'name': 'Tuvalu', 'gdp_per_capita': 4000, 'data_premium': 'medium-low'},
    'NR': {'tier': 4, 'name': 'Nauru', 'gdp_per_capita': 12000, 'data_premium': 'medium-low'},
    
    # Tier 5 - Developing Markets (0.3x base multiplier)
    # High growth potential but lower current data values
    'NG': {'tier': 5, 'name': 'Nigeria', 'gdp_per_capita': 2100, 'data_premium': 'low'},
    'BD': {'tier': 5, 'name': 'Bangladesh', 'gdp_per_capita': 2500, 'data_premium': 'low'},
    'PK': {'tier': 5, 'name': 'Pakistan', 'gdp_per_capita': 1700, 'data_premium': 'low'},
    'KE': {'tier': 5, 'name': 'Kenya', 'gdp_per_capita': 2000, 'data_premium': 'low'},
    'VN': {'tier': 5, 'name': 'Vietnam', 'gdp_per_capita': 4200, 'data_premium': 'low'},
    'GH': {'tier': 5, 'name': 'Ghana', 'gdp_per_capita': 2400, 'data_premium': 'low'},
    'LK': {'tier': 5, 'name': 'Sri Lanka', 'gdp_per_capita': 3700, 'data_premium': 'low'},
    'ET': {'tier': 5, 'name': 'Ethiopia', 'gdp_per_capita': 900, 'data_premium': 'low'},
    'UG': {'tier': 5, 'name': 'Uganda', 'gdp_per_capita': 800, 'data_premium': 'low'},
    'TZ': {'tier': 5, 'name': 'Tanzania', 'gdp_per_capita': 1100, 'data_premium': 'low'},
    'RW': {'tier': 5, 'name': 'Rwanda', 'gdp_per_capita': 800, 'data_premium': 'low'},
    'ZM': {'tier': 5, 'name': 'Zambia', 'gdp_per_capita': 1200, 'data_premium': 'low'},
    'ZW': {'tier': 5, 'name': 'Zimbabwe', 'gdp_per_capita': 1900, 'data_premium': 'low'},
    'MZ': {'tier': 5, 'name': 'Mozambique', 'gdp_per_capita': 500, 'data_premium': 'low'},
    'MW': {'tier': 5, 'name': 'Malawi', 'gdp_per_capita': 400, 'data_premium': 'low'},
    'BF': {'tier': 5, 'name': 'Burkina Faso', 'gdp_per_capita': 800, 'data_premium': 'low'},
    'ML': {'tier': 5, 'name': 'Mali', 'gdp_per_capita': 900, 'data_premium': 'low'},
    'NE': {'tier': 5, 'name': 'Niger', 'gdp_per_capita': 500, 'data_premium': 'low'},
    'TD': {'tier': 5, 'name': 'Chad', 'gdp_per_capita': 700, 'data_premium': 'low'},
    'SN': {'tier': 5, 'name': 'Senegal', 'gdp_per_capita': 1600, 'data_premium': 'low'},
    'CI': {'tier': 5, 'name': 'Ivory Coast', 'gdp_per_capita': 2300, 'data_premium': 'low'},
    'CM': {'tier': 5, 'name': 'Cameroon', 'gdp_per_capita': 1500, 'data_premium': 'low'},
    'BJ': {'tier': 5, 'name': 'Benin', 'gdp_per_capita': 1300, 'data_premium': 'low'},
    'TG': {'tier': 5, 'name': 'Togo', 'gdp_per_capita': 900, 'data_premium': 'low'},
    'MM': {'tier': 5, 'name': 'Myanmar', 'gdp_per_capita': 1400, 'data_premium': 'low'},
    'KH': {'tier': 5, 'name': 'Cambodia', 'gdp_per_capita': 1700, 'data_premium': 'low'},
    'LA': {'tier': 5, 'name': 'Laos', 'gdp_per_capita': 2500, 'data_premium': 'low'},
    'NP': {'tier': 5, 'name': 'Nepal', 'gdp_per_capita': 1300, 'data_premium': 'low'},
    'AF': {'tier': 5, 'name': 'Afghanistan', 'gdp_per_capita': 500, 'data_premium': 'low'},
    'IQ': {'tier': 5, 'name': 'Iraq', 'gdp_per_capita': 4600, 'data_premium': 'low'},
    'SY': {'tier': 5, 'name': 'Syria', 'gdp_per_capita': 1800, 'data_premium': 'low'},
    'YE': {'tier': 5, 'name': 'Yemen', 'gdp_per_capita': 900, 'data_premium': 'low'},
    'SD': {'tier': 5, 'name': 'Sudan', 'gdp_per_capita': 1100, 'data_premium': 'low'},
    'SS': {'tier': 5, 'name': 'South Sudan', 'gdp_per_capita': 300, 'data_premium': 'low'},
    'LR': {'tier': 5, 'name': 'Liberia', 'gdp_per_capita': 700, 'data_premium': 'low'},
    'SL': {'tier': 5, 'name': 'Sierra Leone', 'gdp_per_capita': 500, 'data_premium': 'low'},
    'GN': {'tier': 5, 'name': 'Guinea', 'gdp_per_capita': 1000, 'data_premium': 'low'},
    'GM': {'tier': 5, 'name': 'Gambia', 'gdp_per_capita': 800, 'data_premium': 'low'},
    'GW': {'tier': 5, 'name': 'Guinea-Bissau', 'gdp_per_capita': 800, 'data_premium': 'low'},
    'BO': {'tier': 5, 'name': 'Bolivia', 'gdp_per_capita': 3500, 'data_premium': 'low'},
    'PY': {'tier': 5, 'name': 'Paraguay', 'gdp_per_capita': 5800, 'data_premium': 'low'},
    'HT': {'tier': 5, 'name': 'Haiti', 'gdp_per_capita': 1800, 'data_premium': 'low'},
    'CU': {'tier': 5, 'name': 'Cuba', 'gdp_per_capita': 9100, 'data_premium': 'low'},
    'VE': {'tier': 5, 'name': 'Venezuela', 'gdp_per_capita': 3500, 'data_premium': 'low'},
    'GY': {'tier': 5, 'name': 'Guyana', 'gdp_per_capita': 8500, 'data_premium': 'low'},
    'SR': {'tier': 5, 'name': 'Suriname', 'gdp_per_capita': 6100, 'data_premium': 'low'},
    'BZ': {'tier': 5, 'name': 'Belize', 'gdp_per_capita': 4800, 'data_premium': 'low'},
    'AG': {'tier': 5, 'name': 'Antigua and Barbuda', 'gdp_per_capita': 16000, 'data_premium': 'low'},
    'BB': {'tier': 5, 'name': 'Barbados', 'gdp_per_capita': 18000, 'data_premium': 'low'},
    'BS': {'tier': 5, 'name': 'Bahamas', 'gdp_per_capita': 32000, 'data_premium': 'low'},
    'DM': {'tier': 5, 'name': 'Dominica', 'gdp_per_capita': 7900, 'data_premium': 'low'},
    'GD': {'tier': 5, 'name': 'Grenada', 'gdp_per_capita': 9200, 'data_premium': 'low'},
    'KN': {'tier': 5, 'name': 'Saint Kitts and Nevis', 'gdp_per_capita': 17000, 'data_premium': 'low'},
    'LC': {'tier': 5, 'name': 'Saint Lucia', 'gdp_per_capita': 10000, 'data_premium': 'low'},
    'VC': {'tier': 5, 'name': 'Saint Vincent and the Grenadines', 'gdp_per_capita': 7800, 'data_premium': 'low'},
    'TT': {'tier': 5, 'name': 'Trinidad and Tobago', 'gdp_per_capita': 16000, 'data_premium': 'low'},
    'AO': {'tier': 5, 'name': 'Angola', 'gdp_per_capita': 2000, 'data_premium': 'low'},
    'CF': {'tier': 5, 'name': 'Central African Republic', 'gdp_per_capita': 500, 'data_premium': 'low'},
    'CG': {'tier': 5, 'name': 'Republic of the Congo', 'gdp_per_capita': 2200, 'data_premium': 'low'},
    'CD': {'tier': 5, 'name': 'Democratic Republic of the Congo', 'gdp_per_capita': 600, 'data_premium': 'low'},
    'DJ': {'tier': 5, 'name': 'Djibouti', 'gdp_per_capita': 3600, 'data_premium': 'low'},
    'ER': {'tier': 5, 'name': 'Eritrea', 'gdp_per_capita': 600, 'data_premium': 'low'},
    'SO': {'tier': 5, 'name': 'Somalia', 'gdp_per_capita': 400, 'data_premium': 'low'},
    'MR': {'tier': 5, 'name': 'Mauritania', 'gdp_per_capita': 1600, 'data_premium': 'low'},
    'KM': {'tier': 5, 'name': 'Comoros', 'gdp_per_capita': 800, 'data_premium': 'low'},
    'MG': {'tier': 5, 'name': 'Madagascar', 'gdp_per_capita': 500, 'data_premium': 'low'},
    'BI': {'tier': 5, 'name': 'Burundi', 'gdp_per_capita': 300, 'data_premium': 'low'},
    'BT': {'tier': 5, 'name': 'Bhutan', 'gdp_per_capita': 3500, 'data_premium': 'low'},
    'MV': {'tier': 5, 'name': 'Maldives', 'gdp_per_capita': 10000, 'data_premium': 'low'},
    'BN': {'tier': 5, 'name': 'Brunei', 'gdp_per_capita': 31000, 'data_premium': 'low'},
    'TL': {'tier': 5, 'name': 'East Timor', 'gdp_per_capita': 1500, 'data_premium': 'low'},
    'NC': {'tier': 5, 'name': 'New Caledonia', 'gdp_per_capita': 38000, 'data_premium': 'low'},
    'PF': {'tier': 5, 'name': 'French Polynesia', 'gdp_per_capita': 18000, 'data_premium': 'low'},
    'KP': {'tier': 5, 'name': 'North Korea', 'gdp_per_capita': 1700, 'data_premium': 'low'},
}

# Tier-based multipliers for scoring
TIER_MULTIPLIERS = {
    1: 1.0,   # Premium markets - full value
    2: 0.8,   # Developed markets - 80% of premium
    3: 0.6,   # Emerging high - 60% of premium  
    4: 0.4,   # Emerging standard - 40% of premium
    5: 0.3,   # Developing markets - 30% of premium
}

# Scarcity bonuses for underrepresented quality markets
SCARCITY_BONUSES = {
    1: 0,     # No scarcity bonus for premium markets
    2: 2,     # Small bonus for developed markets
    3: 5,     # Medium bonus for emerging high
    4: 8,     # Higher bonus for emerging standard
    5: 12,    # Maximum bonus for developing markets
}

# PPP adjustment factors (relative to USD purchasing power)
PPP_ADJUSTMENTS = {
    1: 1.0,   # Premium markets - no adjustment needed
    2: 1.1,   # Slight PPP boost for developed markets
    3: 1.3,   # Moderate PPP boost for emerging high
    4: 1.8,   # Significant PPP boost for emerging standard  
    5: 2.5,   # Maximum PPP boost for developing markets
}


class CountryScoring:
    """Handle country-based scoring calculations for fair global rewards"""
    
    def __init__(self):
        self.countries = COUNTRY_TIERS
        self.tier_multipliers = TIER_MULTIPLIERS
        self.scarcity_bonuses = SCARCITY_BONUSES
        self.ppp_adjustments = PPP_ADJUSTMENTS
    
    def get_country_info(self, country_code: str) -> Dict[str, Any]:
        """Get country information and tier details"""
        
        country_code = country_code.upper() if country_code else 'US'
        
        if country_code not in self.countries:
            # Default to US if country not found
            logging.warning(f"Country code '{country_code}' not found, defaulting to US")
            country_code = 'US'
        
        country_data = self.countries[country_code]
        tier = country_data['tier']
        
        return {
            'country_code': country_code,
            'country_name': country_data['name'],
            'tier': tier,
            'gdp_per_capita': country_data['gdp_per_capita'],
            'data_premium': country_data['data_premium'],
            'base_multiplier': self.tier_multipliers[tier],
            'scarcity_bonus': self.scarcity_bonuses[tier],
            'ppp_adjustment': self.ppp_adjustments[tier]
        }
    
    def calculate_country_adjusted_score(self, base_score: float, country_code: str) -> Dict[str, Any]:
        """Calculate final score with country adjustments"""
        
        country_info = self.get_country_info(country_code)
        
        # Apply base multiplier
        adjusted_score = base_score * country_info['base_multiplier']
        
        # Add scarcity bonus (max 12 points)
        adjusted_score += country_info['scarcity_bonus']
        
        # Cap at 100 points maximum
        final_score = min(adjusted_score, 100.0)
        
        # Calculate Vana score (0.0 to 1.0)
        vana_score = final_score / 100.0
        
        return {
            'original_score': base_score,
            'country_multiplier': country_info['base_multiplier'],
            'scarcity_bonus': country_info['scarcity_bonus'],
            'adjusted_total': adjusted_score,
            'final_score': final_score,
            'vana_score': vana_score,
            'country_info': country_info
        }
    
    def get_tier_summary(self) -> Dict[int, Dict[str, Any]]:
        """Get summary of all country tiers"""
        
        tier_summary = {}
        
        for tier in range(1, 6):
            countries_in_tier = [
                code for code, data in self.countries.items() 
                if data['tier'] == tier
            ]
            
            tier_summary[tier] = {
                'countries': countries_in_tier,
                'base_multiplier': self.tier_multipliers[tier],
                'scarcity_bonus': self.scarcity_bonuses[tier],
                'ppp_adjustment': self.ppp_adjustments[tier],
                'description': self._get_tier_description(tier)
            }
        
        return tier_summary
    
    def _get_tier_description(self, tier: int) -> str:
        """Get description for country tier"""
        
        descriptions = {
            1: "Premium Markets - High GDP, mature financial systems",
            2: "Developed Markets - Strong economies, established data markets", 
            3: "Emerging High - Growing economies, developing financial sectors",
            4: "Emerging Standard - Large populations, lower GDP per capita",
            5: "Developing Markets - High growth potential, early data markets"
        }
        
        return descriptions.get(tier, "Unknown tier")


# Global instance for easy access
country_scoring = CountryScoring()
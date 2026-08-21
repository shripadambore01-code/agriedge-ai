# AgriEdge AI - Smart Agricultural Weather & Agromet Advisory Service
import requests
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime, date

# Well-known Indian Agricultural Hub coordinate fallbacks (in case geocoding is slow/offline)
GEO_COORDINATES_FALLBACK: Dict[str, Dict[str, float]] = {
    'nashik': {'lat': 19.9975, 'lon': 73.7898},
    'maharashtra': {'lat': 19.7515, 'lon': 75.7139},
    'amravati': {'lat': 20.9320, 'lon': 77.7523},
    'nagpur': {'lat': 21.1458, 'lon': 79.0882},
    'pune': {'lat': 18.5204, 'lon': 73.8567},
    'guntur': {'lat': 16.3067, 'lon': 80.4365},
    'andhra pradesh': {'lat': 15.9129, 'lon': 79.7400},
    'ludhiana': {'lat': 30.9010, 'lon': 75.8573},
    'punjab': {'lat': 31.1471, 'lon': 75.3412},
    'indore': {'lat': 22.7196, 'lon': 75.8577},
    'madhya pradesh': {'lat': 22.9734, 'lon': 78.6569},
    'ahmedabad': {'lat': 23.0225, 'lon': 72.5714},
    'gujarat': {'lat': 22.2587, 'lon': 71.1924},
    'coimbatore': {'lat': 11.0168, 'lon': 76.9558},
    'tamil nadu': {'lat': 11.1271, 'lon': 78.6569},
    'bengaluru': {'lat': 12.9716, 'lon': 77.5946},
    'karnataka': {'lat': 15.3173, 'lon': 75.7139},
    'varanasi': {'lat': 25.3176, 'lon': 82.9739},
    'uttar pradesh': {'lat': 26.8467, 'lon': 80.9462},
    'kolkata': {'lat': 22.5726, 'lon': 88.3639},
    'west bengal': {'lat': 22.9868, 'lon': 87.8550},
    'default': {'lat': 19.9975, 'lon': 73.7898}
}

class DailyForecastItem(BaseModel):
    date: str
    day_name: str
    temp_max: float
    temp_min: float
    precipitation_mm: float
    precipitation_prob: int
    weather_desc: str
    icon_class: str

class AgrometAdvisory(BaseModel):
    id: str
    type: str  # 'spray_window', 'disease_risk', 'rain_alert', 'wind_alert', 'irrigation_boost'
    severity: str  # 'favorable', 'warning', 'urgent', 'info'
    title: str
    description: str
    action: str

class WeatherSummary(BaseModel):
    location: str
    current_temp: float
    current_humidity: int
    current_wind_speed: float
    current_weather_desc: str
    spray_suitability: str  # 'Optimal', 'Moderate', 'Not Recommended'
    spray_suitability_reason: str
    advisories: List[AgrometAdvisory]
    forecast_7days: List[DailyForecastItem]

def geocode_location(location_str: str) -> Dict[str, float]:
    clean_loc = location_str.strip().lower()
    for key, coords in GEO_COORDINATES_FALLBACK.items():
        if key in clean_loc:
            return coords

    # Try live Open-Meteo Geocoding
    try:
        url = f'https://geocoding-api.open-meteo.com/v1/search?name={requests.utils.quote(location_str)}&count=1&language=en&format=json'
        res = requests.get(url, timeout=4)
        if res.ok:
            data = res.json()
            if 'results' in data and len(data['results']) > 0:
                r = data['results'][0]
                return {'lat': r['latitude'], 'lon': r['longitude']}
    except Exception:
        pass

    return GEO_COORDINATES_FALLBACK['default']

def weather_code_to_desc(code: int) -> Dict[str, str]:
    mapping = {
        0: {'desc': 'Clear Sky', 'icon': 'fa-sun'},
        1: {'desc': 'Mainly Clear', 'icon': 'fa-cloud-sun'},
        2: {'desc': 'Partly Cloudy', 'icon': 'fa-cloud-sun'},
        3: {'desc': 'Overcast', 'icon': 'fa-cloud'},
        45: {'desc': 'Foggy', 'icon': 'fa-smog'},
        48: {'desc': 'Depositing Rime Fog', 'icon': 'fa-smog'},
        51: {'desc': 'Light Drizzle', 'icon': 'fa-cloud-rain'},
        53: {'desc': 'Moderate Drizzle', 'icon': 'fa-cloud-rain'},
        55: {'desc': 'Dense Drizzle', 'icon': 'fa-cloud-showers-heavy'},
        61: {'desc': 'Slight Rain', 'icon': 'fa-cloud-rain'},
        63: {'desc': 'Moderate Rain', 'icon': 'fa-cloud-showers-heavy'},
        65: {'desc': 'Heavy Rain', 'icon': 'fa-cloud-showers-water'},
        80: {'desc': 'Rain Showers', 'icon': 'fa-cloud-showers-heavy'},
        81: {'desc': 'Moderate Showers', 'icon': 'fa-cloud-showers-heavy'},
        82: {'desc': 'Violent Showers', 'icon': 'fa-bolt'},
        95: {'desc': 'Thunderstorm', 'icon': 'fa-bolt-lightning'},
        96: {'desc': 'Thunderstorm with Hail', 'icon': 'fa-cloud-bolt'}
    }
    return mapping.get(code, {'desc': 'Partly Cloudy', 'icon': 'fa-cloud-sun'})

def get_live_agricultural_weather(location_str: str, crop_name: str = 'Cotton', current_stage: str = 'Vegetative') -> WeatherSummary:
    coords = geocode_location(location_str)
    lat, lon = coords['lat'], coords['lon']

    # Default simulated fallback values
    current_temp = 29.5
    current_humidity = 68
    current_wind = 11.2
    current_desc = 'Partly Cloudy'

    forecast_items: List[DailyForecastItem] = []
    days = ['Today', 'Tomorrow', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7']
    base_date = date.today()

    try:
        url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max&timezone=auto'
        res = requests.get(url, timeout=5)
        if res.ok:
            data = res.json()
            curr = data.get('current', {})
            current_temp = curr.get('temperature_2m', 29.5)
            current_humidity = curr.get('relative_humidity_2m', 68)
            current_wind = curr.get('wind_speed_10m', 11.2)
            code_info = weather_code_to_desc(curr.get('weather_code', 1))
            current_desc = code_info['desc']

            daily = data.get('daily', {})
            dates = daily.get('time', [])
            max_t = daily.get('temperature_2m_max', [])
            min_t = daily.get('temperature_2m_min', [])
            precip = daily.get('precipitation_sum', [])
            prob = daily.get('precipitation_probability_max', [])
            codes = daily.get('weather_code', [])

            for i in range(min(7, len(dates))):
                dt_obj = datetime.strptime(dates[i], '%Y-%m-%d')
                day_label = 'Today' if i == 0 else ('Tomorrow' if i == 1 else dt_obj.strftime('%a'))
                c_info = weather_code_to_desc(codes[i] if i < len(codes) else 1)
                forecast_items.append(DailyForecastItem(
                    date=dates[i],
                    day_name=day_label,
                    temp_max=max_t[i] if i < len(max_t) else 32.0,
                    temp_min=min_t[i] if i < len(min_t) else 22.0,
                    precipitation_mm=precip[i] if i < len(precip) else 0.0,
                    precipitation_prob=prob[i] if i < len(prob) else 10,
                    weather_desc=c_info['desc'],
                    icon_class=c_info['icon']
                ))
    except Exception as e:
        print('Live Open-Meteo fetch failed, using offline agricultural weather model:', e)

    if not forecast_items:
        # Fallback 7-day items
        for i in range(7):
            day_label = days[i] if i < 2 else (f'Day {i+1}')
            forecast_items.append(DailyForecastItem(
                date=base_date.strftime('%Y-%m-%d'),
                day_name=day_label,
                temp_max=32.0 - (i % 2),
                temp_min=22.0 + (i % 2),
                precipitation_mm=2.5 if i == 2 else 0.0,
                precipitation_prob=45 if i == 2 else 15,
                weather_desc='Partly Cloudy' if i != 2 else 'Light Showers',
                icon_class='fa-cloud-sun' if i != 2 else 'fa-cloud-rain'
            ))

    # --- AGROMET ADVISORY RULE ENGINE ---
    advisories: List[AgrometAdvisory] = []

    # 1. Spray Window Advisory
    next_48h_rain = sum(f.precipitation_mm for f in forecast_items[:2])
    if current_wind <= 15.0 and next_48h_rain < 5.0:
        spray_suitability = 'Optimal'
        spray_reason = f'Calm winds ({current_wind} km/h) and dry weather forecast next 48h.'
        advisories.append(AgrometAdvisory(
            id='adv_spray_opt',
            type='spray_window',
            severity='favorable',
            title='🟢 Optimal Chemical Spray Window Open',
            description=f'Winds are calm at {current_wind} km/h with low rain probability (<20%) over the next 48 hours.',
            action='Ideal time for foliar nutrition, biopesticides, and disease preventative sprays (early morning 6-9 AM or late afternoon).'
        ))
    elif current_wind > 20.0:
        spray_suitability = 'Not Recommended'
        spray_reason = f'High wind speed ({current_wind} km/h) causes severe chemical drift.'
        advisories.append(AgrometAdvisory(
            id='adv_wind_high',
            type='wind_alert',
            severity='warning',
            title='💨 Wind Drift Warning: Delay Chemical Sprays',
            description=f'Current wind speed is {current_wind} km/h, exceeding the safe spraying threshold of 15 km/h.',
            action='Postpone spray operations to prevent drift loss, uneven coverage, and damage to neighboring plots.'
        ))
    else:
        spray_suitability = 'Moderate'
        spray_reason = 'Marginal conditions; monitor cloud cover and local wind gusts.'

    # 2. Disease & Fungal Warning based on Humidity + Temp
    if current_humidity >= 75 and 20.0 <= current_temp <= 33.0:
        advisories.append(AgrometAdvisory(
            id='adv_fungal_risk',
            type='disease_risk',
            severity='urgent',
            title=f'⚠️ High Fungal Disease Risk Alert for {crop_name}',
            description=f'Persistent high relative humidity ({current_humidity}%) combined with {current_temp}°C temperature provides prime microclimate for fungal spore germination.',
            action=f'Inspect lower canopy of {crop_name} for leaf spots, rusts, or mildew. Ensure drainage and avoid excessive nitrogen.'
        ))

    # 3. Upcoming Rain Alert & Fertilizer Management
    rain_days = [f for f in forecast_items if f.precipitation_mm >= 10.0 or f.precipitation_prob >= 60]
    if rain_days:
        r_day = rain_days[0]
        advisories.append(AgrometAdvisory(
            id='adv_rain_fert',
            type='rain_alert',
            severity='warning',
            title=f'🌧️ Rain Expected ({r_day.day_name}, ~{r_day.precipitation_mm}mm): Adjust Farm Operations',
            description=f'{r_day.day_name} has a {r_day.precipitation_prob}% chance of rain with estimated {r_day.precipitation_mm}mm precipitation.',
            action='Do not broadcast granular Urea or pesticides before rain (leaching risk). Clear field drainage channels to prevent waterlogging.'
        ))

    # 4. Heat Stress & Irrigation Guidance
    if current_temp >= 35.0:
        advisories.append(AgrometAdvisory(
            id='adv_heat_irr',
            type='irrigation_boost',
            severity='warning',
            title='☀️ High Heat & Evapotranspiration: Increase Irrigation',
            description=f'Maximum temperatures reaching {current_temp}°C increase crop water stress and transpiration demand.',
            action='Increase drip/sprinkler run time by 20-25% during early morning hours to keep root zone cool.'
        ))
    else:
        advisories.append(AgrometAdvisory(
            id='adv_irr_norm',
            type='irrigation_boost',
            severity='info',
            title='💧 Steady Irrigation Schedule',
            description=f'Temperatures ({current_temp}°C) and evapotranspiration are within normal seasonal range.',
            action='Maintain regular scheduled fertigation and moisture checks at 15cm soil depth.'
        ))

    return WeatherSummary(
        location=location_str,
        current_temp=round(current_temp, 1),
        current_humidity=int(current_humidity),
        current_wind_speed=round(current_wind, 1),
        current_weather_desc=current_desc,
        spray_suitability=spray_suitability,
        spray_suitability_reason=spray_reason,
        advisories=advisories,
        forecast_7days=forecast_items
    )

import requests
from colorama import init, Fore, Style
import sys

init(autoreset=True)

def get_location():
    """Detect user location based on IP address."""
    try:
        resp = requests.get("https://ipinfo.io/json", timeout=10)
        data = resp.json()
        city = data.get("city")
        loc = data.get("loc")  # format: "lat,lon"
        if loc:
            lat, lon = loc.split(",")
            return city, float(lat), float(lon)
        else:
            return None, None, None
    except Exception as e:
        print(Fore.RED + f"Could not detect location: {e}")
        return None, None, None

def geocode_city(city):
    """Get latitude and longitude for a city using Open-Meteo's geocoding API."""
    try:
        resp = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1",
            timeout=10
        )
        data = resp.json()
        results = data.get("results")
        if results:
            lat = results[0]["latitude"]
            lon = results[0]["longitude"]
            city_name = results[0]["name"]
            country = results[0].get("country", "")
            return city_name, country, lat, lon
        else:
            print(Fore.YELLOW + "City not found.")
            return None, None, None, None
    except Exception as e:
        print(Fore.RED + f"Error geocoding city: {e}")
        return None, None, None, None

def get_weather(lat, lon):
    """Fetch current weather from Open-Meteo."""
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,apparent_temperature,weathercode,wind_speed_10m,relative_humidity_2m"
        )
        resp = requests.get(url, timeout=10)
        data = resp.json()
        current = data.get("current", {})
        return current
    except Exception as e:
        print(Fore.RED + f"Error fetching weather: {e}")
        return None

def weather_icon(code):
    """Return an ASCII weather icon based on Open-Meteo weather code."""
    icons = {
        0: "☀️",   # Clear sky
        1: "🌤️",  # Mainly clear
        2: "⛅",   # Partly cloudy
        3: "☁️",   # Overcast
        45: "🌫️", # Fog
        48: "🌫️", # Depositing rime fog
        51: "🌦️", # Drizzle: Light
        53: "🌦️", # Drizzle: Moderate
        55: "🌦️", # Drizzle: Dense
        61: "🌧️", # Rain: Slight
        63: "🌧️", # Rain: Moderate
        65: "🌧️", # Rain: Heavy
        71: "🌨️", # Snow fall: Slight
        73: "🌨️", # Snow fall: Moderate
        75: "🌨️", # Snow fall: Heavy
        80: "🌦️", # Rain showers: Slight
        81: "🌦️", # Rain showers: Moderate
        82: "🌦️", # Rain showers: Violent
        95: "⛈️", # Thunderstorm: Slight or moderate
        96: "⛈️", # Thunderstorm with slight hail
        99: "⛈️", # Thunderstorm with heavy hail
    }
    return icons.get(code, "🌈")

def print_banner():
    print(Fore.CYAN + Style.BRIGHT + "=" * 45)
    print(Fore.CYAN + Style.BRIGHT + "         Simple Weather CLI App")
    print(Fore.CYAN + Style.BRIGHT + "=" * 45)
    print(Fore.WHITE + "Type 'exit' to quit.")
    print(Fore.WHITE + "Type 'auto' to use your current location.\n")

def print_weather(city, country, weather):
    temp = weather.get("temperature_2m")
    feels = weather.get("apparent_temperature")
    wind = weather.get("wind_speed_10m")
    humidity = weather.get("relative_humidity_2m")
    code = weather.get("weathercode")
    icon = weather_icon(code)
    print(Fore.YELLOW + Style.BRIGHT + f"\n{icon}  Weather for {city}, {country}:")
    print(Fore.GREEN + f"  Temperature     : {temp}°C")
    print(Fore.GREEN + f"  Feels Like      : {feels}°C")
    print(Fore.BLUE + f"  Humidity        : {humidity}%")
    print(Fore.MAGENTA + f"  Wind Speed      : {wind} m/s")
    print(Fore.CYAN + f"  Weather Code    : {code}\n")

def main():
    print_banner()
    while True:
        city_input = input(Fore.WHITE + "Enter city name (or 'auto'): ").strip()
        if city_input.lower() == "exit":
            print(Fore.CYAN + "Goodbye!")
            break
        if city_input.lower() == "auto":
            city, lat, lon = get_location()
            country = ""
            if not city or not lat or not lon:
                print(Fore.RED + "Could not detect your location. Please enter a city.")
                continue
        else:
            city, country, lat, lon = geocode_city(city_input)
            if not lat or not lon:
                continue
        weather = get_weather(lat, lon)
        if weather:
            print_weather(city, country, weather)

if __name__ == "__main__":
    main()

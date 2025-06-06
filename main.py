import requests
import sys
from colorama import init, Fore, Style

init(autoreset=True)

def print_banner():
    banner = f"""
{Fore.CYAN + Style.BRIGHT}=============================================
            🌤️  Weather CLI App
=============================================
{Fore.WHITE}Commands:
  ➤ Enter a city name to get weather
  ➤ Type 'auto' to use your current location
  ➤ Type 'exit' to quit the app
"""
    print(banner)

def get_location():
    """Detect user location based on IP address using ipinfo.io"""
    try:
        response = requests.get("https://ipinfo.io/json", timeout=10)
        data = response.json()
        city = data.get("city", "")
        loc = data.get("loc", "")
        if loc:
            lat, lon = map(float, loc.split(","))
            return city, "", lat, lon
    except Exception as e:
        print(Fore.RED + f"⚠️  Location detection failed: {e}")
    return None, None, None, None

def geocode_city(city):
    """Use Open-Meteo API to convert city name to coordinates"""
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        response = requests.get(url, timeout=10)
        data = response.json()
        if results := data.get("results"):
            city_name = results[0]["name"]
            country = results[0].get("country", "")
            lat = results[0]["latitude"]
            lon = results[0]["longitude"]
            return city_name, country, lat, lon
        else:
            print(Fore.YELLOW + "⚠️  City not found.")
    except Exception as e:
        print(Fore.RED + f"⚠️  Geocoding failed: {e}")
    return None, None, None, None

def get_weather(lat, lon):
    """Fetch current weather from Open-Meteo"""
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,apparent_temperature,weathercode,wind_speed_10m,relative_humidity_2m"
        )
        response = requests.get(url, timeout=10)
        data = response.json()
        return data.get("current")
    except Exception as e:
        print(Fore.RED + f"⚠️  Weather fetch failed: {e}")
        return None

def weather_icon(code):
    """Map weather codes to icons"""
    icons = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️", 45: "🌫️", 48: "🌫️",
        51: "🌦️", 53: "🌦️", 55: "🌦️", 61: "🌧️", 63: "🌧️", 65: "🌧️",
        71: "🌨️", 73: "🌨️", 75: "🌨️", 80: "🌦️", 81: "🌦️", 82: "🌦️",
        95: "⛈️", 96: "⛈️", 99: "⛈️"
    }
    return icons.get(code, "🌈")

def display_weather(city, country, weather):
    """Format and display weather data"""
    print(Fore.YELLOW + Style.BRIGHT + f"\n📍 Weather for {city}, {country}")
    print("  " + "-" * 30)
    print(f"  {weather_icon(weather.get('weathercode', 0))}  Temperature     : {weather.get('temperature_2m')}°C")
    print(f"  🌡️  Feels Like      : {weather.get('apparent_temperature')}°C")
    print(f"  💧  Humidity        : {weather.get('relative_humidity_2m')}%")
    print(f"  💨  Wind Speed      : {weather.get('wind_speed_10m')} m/s")
    print(f"  🔢  Weather Code    : {weather.get('weathercode')}")
    print("  " + "-" * 30 + "\n")

def main():
    print_banner()
    while True:
        user_input = input(Fore.GREEN + "🔍 Enter city ('auto' or 'exit'): ").strip().lower()
        if user_input == "exit":
            print(Fore.CYAN + "👋 Goodbye!")
            break

        if user_input == "auto":
            city, country, lat, lon = get_location()
            if not lat or not lon:
                print(Fore.RED + "⚠️  Could not detect location. Try manual entry.\n")
                continue
        else:
            city, country, lat, lon = geocode_city(user_input)
            if not lat or not lon:
                continue

        weather = get_weather(lat, lon)
        if weather:
            display_weather(city, country, weather)
        else:
            print(Fore.RED + "⚠️  Could not retrieve weather.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.CYAN + "\n👋 Exiting gracefully...")
        sys.exit()

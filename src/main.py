import csv
import sys

import requests

from aggregator import aggregate_weather_data
from api_keys import API_KEYS
from preferences import *

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def internet_connection():
    """Check if the internet connection is available"""
    try:
        response = requests.get("https://example.org", timeout=10)
        return True
    except requests.ConnectionError as e:
        return False

"""Menu, What to say more...."""
def menu():
    """Display the main menu and return the user's choice."""
    print("\nSelect an option:")
    print("1) Get Weather Data")
    print("2) Change APIs")
    print("3) Modify Your Preferences")
    print("4) Exit")
    return input()

def modify_preferences():
    """The user can Add and Delete city from the Preferences."""
    preferences = load_preferences()

    while True:
        print("\nPreferred Cities:")
        for i, city in enumerate(preferences, 1):
            print(f"{i}) {city}")

        print("\nOptions:")
        print("1) Add a city")
        print("2) Delete a city")
        print("3) Return to main menu")
        choice = input()

        if choice == "1":
            new_city = input("What is the name of the city?: ").strip()
            if new_city and new_city not in preferences:
                preferences.append(new_city)
                save_preferences(preferences)
                print(f"{new_city} has beenadded to preferences.")
            else:
                print("City already exists or invalid input.")
        elif choice == "2":
            try:
                city_index = int(input("Enter the number of the city to delete: ").strip()) - 1
                if 0 <= city_index < len(preferences):
                    removed_city = preferences.pop(city_index)
                    save_preferences(preferences)
                    print(f"{removed_city} succesfully removed from preferences.")
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    if not internet_connection():
        logging.error("In order to continue, you need to have an internet connection.")
        sys.exit()

    data_sources = {
        "OpenWeatherMap": API_KEYS["OpenWeatherMap"],
        "VisualCrossing": API_KEYS["VisualCrossing"],
        "WeatherAPI": API_KEYS["WeatherAPI"]
    }

    while True:
        choice = menu()
        if choice == "1":
            preferences = load_preferences()
            if preferences:
                print("\nPreferred Cities:")
                for i, city in enumerate(preferences, 1):
                    print(f"{i}) {city}")
                print("0) Enter a new city")
                try:
                    city_choice = int(input("Choose a city or enter 0 to type a new city: ").strip())
                    if city_choice == 0:
                        city = input("Enter a city name: ").strip()
                    elif 1 <= city_choice <= len(preferences):
                        city = preferences[city_choice - 1]
                    else:
                        print("Invalid choice. Returning to main menu.")
                        continue
                except ValueError:
                    print("Invalid input. Returning to main menu.")
                    continue
            else:
                city = input("Enter a city name: ").strip()

            logging.info(f"Fetching weather data for {city}...")
            aggregated_data = aggregate_weather_data(city, data_sources)

            if aggregated_data["avg_current_temp"] is not None:
                print(f"\nWeather Data for {city}:")
                print(f"Current Temperature: {aggregated_data['avg_current_temp']}°C")
                print(f"Highest Temperature: {aggregated_data['avg_high_temp']}°C")
                print(f"Lowest Temperature: {aggregated_data['avg_low_temp']}°C")
                print(f"Humidity: {aggregated_data['avg_humidity']}%")
                print(f"Air Quality Index (AQI): {', '.join(map(str, aggregated_data['aqi']))}")
                print(f"Sunrise: {aggregated_data['sunrise']}")
                print(f"Sunset: {aggregated_data['sunset']}")
            else:
                print(f"\nNo weather data is available for {city}.")
        elif choice == "2":
            print("Changing API keys...")
            with open("api.csv", mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["API", "Key"])
                for api in ["Open Weather Map", "Visual Crossing", "Weather API"]:
                    key = input(f"Enter your new API key for {api}: ").strip()
                    writer.writerow([api, key])
            print("API keys hsve been updated successfully.")
        elif choice == "3":
            print("Accessing preferences...")
            modify_preferences()
        elif choice == "4":
            print("Goodbye.")
            break
        else:
            print("Unrecognized choice. Please try again.")


if __name__ == "__main__":
    main()

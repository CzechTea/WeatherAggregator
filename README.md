# WeatherAggregator
Created for an Alpha project by Petr Kočovský at SPŠE JEČNÁ

WeatherAggregator is a Python program designed to aggregate multiple Weather APIs into one forecast.

### Data Collection
The main point of this program is to collect data simultaneously data from Open Weather Map, Visual Checking, WeatherAPI

### Data Normalization
The structures of those forecasts may be formatted slightly differently. Fear not! This program will normalize the data and combine it into one structure.

### Data Average
Have you ever checked those forecasts on multiple websites and got that it will be 2°C, 6°C, and 4°C? What to choose? The program will calculate an average Temperature based on those data.

### Preferences
You might use this program to only check the weather in your place. This program can save your preferences and once you ask for a weather forecast, you can choose your favourite place!

## Setup
To use this program. You need

- An Internet Connection
- WeatherAPI API key (you get it by signing in. It's Free!)
- Open Weather Map API key (you get it by signing in. It's Free!)
- Visual Crossing API key (you get it by signing in. It's Free!)
- Python Interpreter (You should already have that...)

The program will ask for the APIs, and if they are correct (They should be...), then you're free to go!

### Used packages
logging,requests,sys,csv,os,unittest,concurrent



## Data example

Weather Data for Ostrava:

Current Temperature: 3°C

Highest Temperature: 4°C

Lowest Temperature: 2°C

Humidity: 76%

Air Quality Index (AQI): 1

Sunrise: 07:41:49

Sunset: 15:47:34

## Sources
My head (Ouch it hurts)

StackOverflow: https://stackoverflow.com/

ChatGPT: https://chatgpt.com/

Bed (I got this idea when I was in bed)




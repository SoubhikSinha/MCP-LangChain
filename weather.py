import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP("Weather") # "Weather" is the name of the MCP server

@mcp.tool()
async def get_weather(city: str) -> str:
    """
    Get the current real weather for a city using the Open-Meteo API (no API key needed).
    Args:
        city (str): The city name
    Returns:
        str: Current weather conditions for the city
    """
    async with httpx.AsyncClient() as client:

        # Step 1: Geocode the city name → lat/lon
        geo_resp = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
        )
        geo_data = geo_resp.json()

        if not geo_data.get("results"):
            return f"Could not find location data for '{city}'. Please check the city name."

        result = geo_data["results"][0]
        lat = result["latitude"]
        lon = result["longitude"]
        resolved_name = result.get("name", city)
        country = result.get("country", "")

        # Step 2: Fetch current weather from Open-Meteo
        weather_resp = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "weather_code",
                    "wind_speed_10m",
                ],
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
            },
        )
        w = weather_resp.json().get("current", {})

    # WMO weather code → description mapping
    wmo_codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Icy fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
    }
    condition = wmo_codes.get(w.get("weather_code", -1), "Unknown")

    return (
        f"Current weather in {resolved_name}, {country}:\n"
        f"  Condition    : {condition}\n"
        f"  Temperature  : {w.get('temperature_2m')}°F "
        f"(feels like {w.get('apparent_temperature')}°F)\n"
        f"  Humidity     : {w.get('relative_humidity_2m')}%\n"
        f"  Wind Speed   : {w.get('wind_speed_10m')} mph"
    )

# To start the server, run this script.
# The server will run on http://[IP_ADDRESS]/mcp
if __name__ == "__main__":
    mcp.run(transport="streamable-http") # streamable-http --> this is the recommended transport for FastAPI
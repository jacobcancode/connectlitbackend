import requests

# API endpoint
url = "https://auto.dev/api/engines"

# Optional headers if an API key is required (replace 'your_api_key' with the actual key)
headers = {
    "Authorization": "Bearer your_api_key",  # Uncomment if an API key is needed
    # Add any other headers here if necessary
}

try:
    # Make the GET request
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the JSON response
    engines = response.json()

    # Extract the first five engine types (assuming the API returns a list of engine objects)
    first_five_engines = engines[:5]
    for i, engine in enumerate(first_five_engines, start=1):
        print(f"Engine {i}: {engine['engine_type']}")

except requests.exceptions.RequestException as e:
    print(f"Error fetching data from API: {e}")

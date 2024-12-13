import requests

# Define the endpoint
url = "https://auto.dev/api/engines"

# Parameters for the request
params = {
    "verbose": "yes"  # Includes additional details in the response
}

try:
    # Make the GET request
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the response
    data = response.json()

    # Extract the first 5 engines
    first_five_engines = data[:5]
    
    # Print the engine types
    for i, engine in enumerate(first_five_engines, start=1):
        engine_type = engine.get("engine_type", "Unknown")
        print(f"Engine {i}: {engine_type}")

except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")

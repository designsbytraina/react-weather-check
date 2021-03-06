# Import Flask
from flask import Flask, render_template, request, jsonify
# Import requests library to make call to Accuweather API
import requests
# Import os to get API_KEY which was sourced from secrets.sh
from secrets import ACCUWEATHER_API_KEY

# Import our weather UI helper functions
from weather_ui import get_ui_attributes

# Always keep your API Key secret
API_KEY = ACCUWEATHER_API_KEY

# "__name__" is a special Python variable for the name of the current module
# Flask wants to know this to know what any imported things are relative to.
app = Flask(__name__)

##################################
# ROUTING
##################################

# Establish routing for home page.
@app.route('/')
def index():
    """Home page."""

    return render_template('index.html')


@app.route('/get-weather.json', methods=["POST"])
def get_weather():
    """Make request to Accuweather API and display result to user."""

    # Get form variable from ajax request
    location = request.form.get('location')

    # Define payload for query to Accuweather API
    payload = {'apikey':API_KEY, 'q':location, 'language':'en-us'}

    # Make request to Accuweather API and save response object
    # See documentation: http://developer.accuweather.com/accuweather-locations-api/apis/get/locations/v1/search
    response = requests.get('http://dataservice.accuweather.com/locations/v1/search',
                                 params=payload)

    # Process the JSON object into a list of results
    response_list = response.json()

    if not response_list:
        # TODO: render invalid UI due to empty response
        pass

    # Process JSON returned and index into object's Key attribute
    location_key = response_list[0]['Key']

    # Make call to helper function to get the current weather with location_key
    weather_obj = get_current_weather(location_key)

    if not weather_obj:
        # TODO: render invalid UI due to empty response
        return jsonify({})

    # Make call to helper function to get the UI parameters to render
    ui_attributes = get_ui_attributes(
        weather_obj['description'].lower(),
        weather_obj['is_day'],
        weather_obj['temp'],
    )

    weather_ui = {
        'weather_obj':weather_obj,
        'ui_attributes':ui_attributes
    }

    return jsonify(weather_ui)

# Process weather data using the location key passed as a parameter from show_results()
def get_current_weather(location):
    """Get current weather data."""

    # Define payload for query to Accuweather API
    payload = {'apikey': API_KEY}

    # Make request to Current Conditions API and save response object
    # See http://developer.accuweather.com/accuweather-current-conditions-api/apis/get/currentconditions/v1/%7BlocationKey%7D
    # for documentation.
    response = requests.get('http://dataservice.accuweather.com/currentconditions/v1/%s' % location,
                                 params=payload)

    # Process the JSON object into a list of results
    response_list = response.json()

    # If there is no weather data, we return an empty dictionary
    if not response_list:
        return {}

    # Define variables using attributes returned in response
    description = response_list[0]['WeatherText']
    is_daytime = response_list[0]['IsDayTime']
    curr_temp = response_list[0]['Temperature']['Imperial']['Value']

    # Return these to the caller
    return {
        'is_day': is_daytime,
        'description': description,
        'temp': curr_temp
    }


##################################
# Necessary to get application running.
if __name__ == '__main__':
    # debug=True gives us error messages in the browser and also "reloads" our
    # web app if we change the code.
    app.run(debug=False, host='0.0.0.0', port=5000)

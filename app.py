from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key'


API_KEY = 'aa2e86ab0525a613a23e73ac9717dffe' 
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_BASE_URL = "http://api.openweathermap.org/data/2.5/forecast"

def get_recommendations(weather_data):
    temp = weather_data['main']['temp']
    weather_desc = weather_data['weather'][0]['description'].lower()
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    recommendations = {
        'clothing': [],
        'accessories': [],
        'activities': [],
        'health_tips': []
    }
    
    # Temperature based recommendations
    if temp < 0:
        recommendations['clothing'].extend([
            'Heavy winter coat or parka',
            'Thermal underwear or base layer',
            'Wool sweater or fleece',
            'Insulated pants',
            'Warm socks (preferably wool)'
        ])
        recommendations['accessories'].extend([
            'Warm winter hat (covers ears)',
            'Insulated gloves or mittens',
            'Thick scarf or neck warmer',
            'Winter boots with good grip'
        ])
        recommendations['health_tips'].extend([
            'Stay hydrated despite cold',
            'Watch for signs of hypothermia',
            'Limit time outdoors'
        ])
    elif temp < 10:
        recommendations['clothing'].extend([
            'Warm coat or jacket',
            'Warm sweater or fleece',
            'Long-sleeve thermal shirt',
            'Warm pants or jeans',
            'Warm socks'
        ])
        recommendations['accessories'].extend([
            'Light gloves',
            'Beanie or warm hat',
            'Scarf'
        ])
        recommendations['health_tips'].append('Layer your clothing for better insulation')
    elif temp < 20:
        recommendations['clothing'].extend([
            'Light jacket or windbreaker',
            'Long-sleeve shirt or light sweater',
            'Comfortable pants or jeans',
            'Regular socks'
        ])
        recommendations['accessories'].append('Light scarf for wind protection')
    elif temp < 25:
        recommendations['clothing'].extend([
            'T-shirt or short-sleeve shirt',
            'Light pants or capris',
            'Light fabrics like cotton'
        ])
        recommendations['accessories'].extend([
            'Sunglasses',
            'Sunscreen (SPF 30+)',
            'Light hat or cap'
        ])
    else:
        recommendations['clothing'].extend([
            'Light, breathable clothing',
            'Short-sleeve shirt or tank top',
            'Shorts or light pants',
            'Breathable fabrics like cotton or linen'
        ])
        recommendations['accessories'].extend([
            'Sunglasses',
            'Sunscreen (SPF 50+)',
            'Wide-brimmed sun hat',
            'Water bottle for hydration'
        ])
        recommendations['health_tips'].extend([
            'Stay hydrated - drink plenty of water',
            'Avoid prolonged sun exposure between 10 AM and 4 PM',
            'Seek shade when possible'
        ])

    # Weather condition based recommendations
    if 'rain' in weather_desc or 'drizzle' in weather_desc:
        recommendations['accessories'].extend([
            'Umbrella (Navy blue or black recommended for durability)',
            'Waterproof jacket or raincoat',
            'Water-resistant footwear',
            'Waterproof bag for electronics'
        ])
        recommendations['activities'].extend([
            'Indoor activities recommended',
            'Visit museums or galleries',
            'Catch up on indoor hobbies',
            'Remember to carry emergency poncho'
        ])
        if wind_speed > 5:
            recommendations['accessories'].append('Windproof umbrella recommended due to strong winds')
    elif 'thunderstorm' in weather_desc:
        recommendations['activities'].extend([
            'Stay indoors and away from windows',
            'Avoid open areas and tall objects',
            'Keep devices charged',
            'Have emergency supplies ready'
        ])
        recommendations['health_tips'].append('Stay informed about weather updates')
    elif 'snow' in weather_desc:
        recommendations['accessories'].extend([
            'Waterproof snow boots with good grip',
            'Waterproof gloves',
            'Thermal socks',
            'Ice grips for shoes if icy'
        ])
        recommendations['activities'].extend([
            'Be careful on slippery surfaces',
            'Allow extra time for travel',
            'Check road conditions before traveling',
            'Indoor activities recommended unless properly equipped'
        ])
    elif 'clear' in weather_desc:
        if temp > 20:
            recommendations['activities'].extend([
                'Perfect for outdoor activities',
                'Great time for hiking or sports',
                'Consider picnics or outdoor dining',
                'Beach activities if available'
            ])
        else:
            recommendations['activities'].extend([
                'Good for outdoor walking or jogging',
                'Park visits recommended',
                'Photography opportunities'
            ])
    elif 'cloud' in weather_desc:
        recommendations['accessories'].append('Light jacket might be needed')
        recommendations['activities'].extend([
            'Good for outdoor activities (minimal sun exposure)',
            'Perfect for photography (no harsh shadows)',
            'Park visits or nature walks'
        ])

    # Humidity based recommendations
    if humidity > 80:
        recommendations['clothing'].append('Light, moisture-wicking fabrics')
        recommendations['health_tips'].extend([
            'Stay hydrated - humidity affects body temperature',
            'Take breaks during outdoor activities',
            'Watch for signs of heat exhaustion'
        ])
    elif humidity < 30:
        recommendations['health_tips'].extend([
            'Use moisturizer to protect skin',
            'Stay hydrated in dry conditions',
            'Consider using lip balm'
        ])

    # Wind based recommendations
    if wind_speed > 10:
        recommendations['accessories'].extend([
            'Wind-resistant jacket',
            'Secure hat or cap',
            'Sunglasses for dust protection'
        ])
        recommendations['activities'].append('Be cautious with outdoor activities')
    elif wind_speed > 5:
        recommendations['accessories'].append('Light windbreaker recommended')

    return recommendations

def get_weather(city):
    try:
        # Get current weather
        weather_params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric' 
        }
        response = requests.get(WEATHER_BASE_URL, params=weather_params)
        weather_data = response.json()

        # Get 5-day forecast
        forecast_params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric'
        }
        forecast_response = requests.get(FORECAST_BASE_URL, params=forecast_params)
        forecast_data = forecast_response.json()

        # Add recommendations
        recommendations = get_recommendations(weather_data)

        return {
            'current': weather_data,
            'forecast': forecast_data,
            'recommendations': recommendations
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather')
def weather():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City parameter is required'})
    
    weather_data = get_weather(city)
    return jsonify(weather_data)

# Favorites endpoints
@app.route('/favorites', methods=['GET'])
def get_favorites():
    try:
        with open('favorites.json', 'r') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify([])

@app.route('/favorites', methods=['POST'])
def add_favorite():
    city = request.json.get('city')
    if not city:
        return jsonify({'error': 'City parameter is required'}), 400
    
    try:
        try:
            with open('favorites.json', 'r') as f:
                favorites = json.load(f)
        except FileNotFoundError:
            favorites = []
        
        if city not in favorites:
            favorites.append(city)
            with open('favorites.json', 'w') as f:
                json.dump(favorites, f)
        
        return jsonify({'message': 'City added to favorites'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/favorites', methods=['DELETE'])
def remove_favorite():
    city = request.json.get('city')
    if not city:
        return jsonify({'error': 'City parameter is required'}), 400
    
    try:
        with open('favorites.json', 'r') as f:
            favorites = json.load(f)
        
        if city in favorites:
            favorites.remove(city)
            with open('favorites.json', 'w') as f:
                json.dump(favorites, f)
        
        return jsonify({'message': 'City removed from favorites'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False) 
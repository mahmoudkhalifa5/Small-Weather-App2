from flask import Flask, request, jsonify, render_template_string
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Get API key from environment variable (preferred) or use demo key
API_KEY = os.getenv('API_KEY', '6cf356ceb2ec0ff941855d4a43144e0e')
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'

# HTML Template with embedded CSS and JavaScript - MUST BE DEFINED BEFORE ROUTES
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather Forecast</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            width: 100%;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .header {
            background: #0984e3;
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
        }
        
        .search-container {
            padding: 30px;
            display: flex;
            gap: 10px;
        }
        
        .search-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #ddd;
            border-radius: 50px;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .search-input:focus {
            border-color: #0984e3;
        }
        
        .search-btn {
            background: #0984e3;
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 50px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            transition: background 0.3s;
        }
        
        .search-btn:hover {
            background: #0770c4;
        }
        
        .weather-info {
            padding: 0 30px 30px;
            display: none;
        }
        
        .current-weather {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .city-name {
            font-size: 2rem;
            margin-bottom: 10px;
            color: #2d3436;
        }
        
        .weather-main {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            margin: 20px 0;
        }
        
        .temperature {
            font-size: 4rem;
            font-weight: 300;
            color: #0984e3;
        }
        
        .weather-icon {
            width: 100px;
            height: 100px;
        }
        
        .description {
            font-size: 1.5rem;
            color: #636e72;
            margin-bottom: 20px;
        }
        
        .details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .detail-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .detail-title {
            font-size: 0.9rem;
            color: #636e72;
            margin-bottom: 5px;
        }
        
        .detail-value {
            font-size: 1.5rem;
            font-weight: 600;
            color: #2d3436;
        }
        
        .error-message {
            background: #ff7675;
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin: 0 30px 30px;
            display: none;
        }
        
        .loading {
            text-align: center;
            padding: 30px;
            display: none;
        }
        
        .spinner {
            border: 5px solid #f3f3f3;
            border-top: 5px solid #0984e3;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #636e72;
            font-size: 0.9rem;
            border-top: 1px solid #eee;
        }
        
        @media (max-width: 600px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .search-container {
                flex-direction: column;
            }
            
            .temperature {
                font-size: 3rem;
            }
            
            .weather-icon {
                width: 80px;
                height: 80px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Weather Forecast</h1>
            <p>Get real-time weather information for any city worldwide</p>
        </div>
        
        <div class="search-container">
            <input type="text" class="search-input" id="cityInput" placeholder="Enter city name..." autocomplete="off">
            <button class="search-btn" id="searchBtn">Search</button>
        </div>
        
        <div class="error-message" id="errorMessage"></div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Fetching weather data...</p>
        </div>
        
        <div class="weather-info" id="weatherInfo">
            <div class="current-weather">
                <h2 class="city-name" id="cityName">-</h2>
                <div class="weather-main">
                    <div class="temperature" id="temperature">-</div>
                    <img class="weather-icon" id="weatherIcon" src="" alt="Weather Icon">
                </div>
                <p class="description" id="description">-</p>
            </div>
            
            <div class="details">
                <div class="detail-card">
                    <div class="detail-title">Feels Like</div>
                    <div class="detail-value" id="feelsLike">-</div>
                </div>
                <div class="detail-card">
                    <div class="detail-title">Humidity</div>
                    <div class="detail-value" id="humidity">-</div>
                </div>
                <div class="detail-card">
                    <div class="detail-title">Pressure</div>
                    <div class="detail-value" id="pressure">-</div>
                </div>
                <div class="detail-card">
                    <div class="detail-title">Wind Speed</div>
                    <div class="detail-value" id="windSpeed">-</div>
                </div>
                <div class="detail-card">
                    <div class="detail-title">Visibility</div>
                    <div class="detail-value" id="visibility">-</div>
                </div>
                <div class="detail-card">
                    <div class="detail-title">Sunrise / Sunset</div>
                    <div class="detail-value" id="sunriseSunset">-</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Weather data provided by OpenWeatherMap • Last updated: <span id="timestamp">-</span></p>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const cityInput = document.getElementById('cityInput');
            const searchBtn = document.getElementById('searchBtn');
            const weatherInfo = document.getElementById('weatherInfo');
            const errorMessage = document.getElementById('errorMessage');
            const loading = document.getElementById('loading');
            
            // Elements to update
            const cityName = document.getElementById('cityName');
            const temperature = document.getElementById('temperature');
            const weatherIcon = document.getElementById('weatherIcon');
            const description = document.getElementById('description');
            const feelsLike = document.getElementById('feelsLike');
            const humidity = document.getElementById('humidity');
            const pressure = document.getElementById('pressure');
            const windSpeed = document.getElementById('windSpeed');
            const visibility = document.getElementById('visibility');
            const sunriseSunset = document.getElementById('sunriseSunset');
            const timestamp = document.getElementById('timestamp');
            
            // Search weather function
            function searchWeather() {
                const city = cityInput.value.trim();
                
                if (!city) {
                    showError('Please enter a city name');
                    return;
                }
                
                // Show loading, hide weather and error
                loading.style.display = 'block';
                weatherInfo.style.display = 'none';
                errorMessage.style.display = 'none';
                
                // Fetch weather data
                fetch(`/weather?city=${encodeURIComponent(city)}`)
                    .then(response => {
                        if (!response.ok) {
                            return response.json().then(data => {
                                throw new Error(data.error || 'Failed to fetch weather data');
                            });
                        }
                        return response.json();
                    })
                    .then(data => {
                        // Update UI with weather data
                        cityName.textContent = `${data.city}${data.country ? ', ' + data.country : ''}`;
                        temperature.textContent = `${data.temperature}°C`;
                        weatherIcon.src = `https://openweathermap.org/img/wn/${data.icon}@2x.png`;
                        weatherIcon.alt = data.description;
                        description.textContent = data.description;
                        feelsLike.textContent = `${data.feels_like}°C`;
                        humidity.textContent = `${data.humidity}%`;
                        pressure.textContent = `${data.pressure} hPa`;
                        windSpeed.textContent = `${data.wind_speed} m/s`;
                        visibility.textContent = `${(data.visibility / 1000).toFixed(1)} km`;
                        sunriseSunset.textContent = `${data.sunrise} / ${data.sunset}`;
                        timestamp.textContent = data.timestamp;
                        
                        // Show weather info, hide loading
                        weatherInfo.style.display = 'block';
                        loading.style.display = 'none';
                    })
                    .catch(error => {
                        showError(error.message);
                        loading.style.display = 'none';
                    });
            }
            
            // Show error message
            function showError(message) {
                errorMessage.textContent = message;
                errorMessage.style.display = 'block';
                weatherInfo.style.display = 'none';
            }
            
            // Event listeners
            searchBtn.addEventListener('click', searchWeather);
            
            cityInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchWeather();
                }
            });
            
            // Try to get weather for a default city on load
            cityInput.value = 'London';
            searchWeather();
        });
    </script>
</body>
</html>
"""

def get_weather(city):
    """Fetch weather data from OpenWeatherMap API"""
    try:
        url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        data = response.json()
        main = data['main']
        weather = data['weather'][0]
        sys = data.get('sys', {})
        
        return {
            'city': data['name'],
            'country': sys.get('country', ''),
            'temperature': round(main['temp']),
            'feels_like': round(main['feels_like']),
            'description': weather['description'].title(),
            'humidity': main['humidity'],
            'pressure': main['pressure'],
            'wind_speed': round(data['wind']['speed'], 1),
            'wind_deg': data['wind'].get('deg', 0),
            'visibility': data.get('visibility', 0),
            'icon': weather['icon'],
            'sunrise': datetime.fromtimestamp(sys.get('sunrise', 0)).strftime('%H:%M') if sys.get('sunrise') else 'N/A',
            'sunset': datetime.fromtimestamp(sys.get('sunset', 0)).strftime('%H:%M') if sys.get('sunset') else 'N/A',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Error parsing weather data: {e}")
        return None

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        city = request.form.get('city')
    else:
        city = request.args.get('city')
    
    if not city:
        return jsonify({'error': 'City parameter is required'}), 400
    
    weather_data = get_weather(city)
    if weather_data:
        return jsonify(weather_data)
    else:
        return jsonify({'error': 'City not found or API request failed'}), 404

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)



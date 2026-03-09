// Weather App JavaScript
let currentCity = '';
let favorites = [];

// Load favorites when the page loads
document.addEventListener('DOMContentLoaded', function() {
    loadFavorites();
    document.getElementById('cityInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            getWeather();
        }
    });
});

function getWeather() {
    const city = document.getElementById('cityInput').value;
    if (!city) return;

    fetch(`/weather?city=${encodeURIComponent(city)}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            
            currentCity = city;
            displayCurrentWeather(data.current);
            displayForecast(data.forecast);
            displayRecommendations(data.recommendations);
            updateFavoriteButton();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error fetching weather data');
        });
}

function displayCurrentWeather(current) {
    document.getElementById('currentWeather').style.display = 'block';
    document.getElementById('cityName').textContent = current.name;
    document.getElementById('temperature').textContent = `${Math.round(current.main.temp)}°C`;
    document.getElementById('description').textContent = current.weather[0].description;
    document.getElementById('humidity').textContent = `Humidity: ${current.main.humidity}%`;
    document.getElementById('windSpeed').textContent = `Wind: ${current.wind.speed} m/s`;
    document.getElementById('weatherIcon').src = `https://openweathermap.org/img/w/${current.weather[0].icon}.png`;
}

function displayForecast(forecast) {
    document.getElementById('forecast').style.display = 'block';
    const forecastContainer = document.getElementById('forecastContainer');
    forecastContainer.innerHTML = '';

    // Get one forecast per day (every 8th item as data is in 3-hour intervals)
    const dailyForecasts = forecast.list.filter((item, index) => index % 8 === 0);
    
    dailyForecasts.forEach(day => {
        const date = new Date(day.dt * 1000);
        const dayCard = document.createElement('div');
        dayCard.className = 'col-md-2 col-sm-4 col-6 forecast-card';
        dayCard.innerHTML = `
            <div class="text-center">
                <h5>${date.toLocaleDateString('en-US', { weekday: 'short' })}</h5>
                <img src="https://openweathermap.org/img/w/${day.weather[0].icon}.png">
                <p>${Math.round(day.main.temp)}°C</p>
                <p>${day.weather[0].description}</p>
            </div>
        `;
        forecastContainer.appendChild(dayCard);
    });
}

function displayRecommendations(recommendations) {
    document.getElementById('recommendations').style.display = 'block';
    
    // Display clothing recommendations
    const clothingList = document.getElementById('clothingList');
    clothingList.innerHTML = recommendations.clothing
        .map(item => `<li>${item}</li>`)
        .join('');

    // Display accessories recommendations
    const accessoriesList = document.getElementById('accessoriesList');
    accessoriesList.innerHTML = recommendations.accessories
        .map(item => `<li>${item}</li>`)
        .join('');

    // Display activities recommendations
    const activitiesList = document.getElementById('activitiesList');
    activitiesList.innerHTML = recommendations.activities
        .map(item => `<li>${item}</li>`)
        .join('');

    // Display health tips
    const healthTipsList = document.getElementById('healthTipsList');
    healthTipsList.innerHTML = recommendations.health_tips
        .map(item => `<li>${item}</li>`)
        .join('');
}

// Favorites functionality
function loadFavorites() {
    fetch('/favorites')
        .then(response => response.json())
        .then(data => {
            favorites = data;
            displayFavorites();
            updateFavoriteButton();
        })
        .catch(error => console.error('Error loading favorites:', error));
}

function displayFavorites() {
    const favoritesList = document.getElementById('favoritesList');
    favoritesList.innerHTML = favorites.map(city => `
        <div class="favorite-city">
            <span onclick="getWeatherForCity('${city}')">${city}</span>
            <span class="remove-favorite" onclick="removeFavorite('${city}')">×</span>
        </div>
    `).join('');
}

function getWeatherForCity(city) {
    document.getElementById('cityInput').value = city;
    getWeather();
}

function toggleFavorite() {
    if (!currentCity) return;

    const method = favorites.includes(currentCity) ? 'DELETE' : 'POST';
    
    fetch('/favorites', {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ city: currentCity })
    })
    .then(response => response.json())
    .then(() => {
        if (method === 'POST') {
            if (!favorites.includes(currentCity)) {
                favorites.push(currentCity);
            }
        } else {
            favorites = favorites.filter(city => city !== currentCity);
        }
        displayFavorites();
        updateFavoriteButton();
    })
    .catch(error => console.error('Error updating favorites:', error));
}

function removeFavorite(city) {
    fetch('/favorites', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ city: city })
    })
    .then(response => response.json())
    .then(() => {
        favorites = favorites.filter(c => c !== city);
        displayFavorites();
        updateFavoriteButton();
    })
    .catch(error => console.error('Error removing favorite:', error));
}

function updateFavoriteButton() {
    const favoriteBtn = document.getElementById('favoriteBtn');
    if (favorites.includes(currentCity)) {
        favoriteBtn.classList.add('active');
    } else {
        favoriteBtn.classList.remove('active');
    }
} 
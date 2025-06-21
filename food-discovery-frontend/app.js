// Configuration
const API_BASE_URL = 'http://localhost:3001';
let map;
let markers = [];

// DOM Elements
document.addEventListener('DOMContentLoaded', () => {
    // Check API status
    checkApiStatus();

    // Set up event listeners
    document.getElementById('query-btn').addEventListener('click', handleQuery);
    document.getElementById('voice-btn').addEventListener('mousedown', startRecording);
    document.getElementById('voice-btn').addEventListener('mouseup', stopRecording);
    document.getElementById('voice-btn').addEventListener('mouseleave', stopRecording);
    document.getElementById('send-voice-btn').addEventListener('click', handleVoiceQuery);
    document.getElementById('get-pref-btn').addEventListener('click', getPreferences);
    document.getElementById('save-pref-btn').addEventListener('click', savePreferences);
    document.getElementById('get-feedback-restaurant-btn').addEventListener('click', getRestaurantFeedback);
    document.getElementById('get-feedback-user-btn').addEventListener('click', getUserFeedback);
    document.getElementById('save-feedback-btn').addEventListener('click', saveFeedback);
    document.getElementById('suggestions-btn').addEventListener('click', getSuggestions);
});

// Check API Status
async function checkApiStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}`);
        const data = await response.json();
        
        document.getElementById('api-status').textContent = 'Connected';
        document.getElementById('api-status').className = 'text-success';
        
        // Display API details
        const endpointsList = data.endpoints.map(endpoint => 
            `<li>${endpoint.method} ${endpoint.path} - ${endpoint.description}</li>`
        ).join('');
        
        document.getElementById('api-details').innerHTML = `
            <small>
                <strong>Version:</strong> ${data.version || 'N/A'}<br>
                <strong>Environment:</strong> ${data.environment || 'N/A'}<br>
                <strong>Available Endpoints:</strong>
                <ul class="mb-0">${endpointsList}</ul>
            </small>
        `;
    } catch (error) {
        document.getElementById('api-status').textContent = 'Disconnected';
        document.getElementById('api-status').className = 'text-danger';
        document.getElementById('api-details').innerHTML = `
            <div class="alert alert-danger">
                <small>Failed to connect to API at ${API_BASE_URL}. Make sure the server is running.</small>
            </div>
        `;
        console.error('API Status Error:', error);
    }
}

// Process Query
async function handleQuery() {
    const queryText = document.getElementById('query-text').value.trim();
    const userId = document.getElementById('query-user-id').value.trim();
    const responseElement = document.getElementById('query-response');
    
    if (!queryText) {
        responseElement.textContent = 'Please enter a query';
        return;
    }
    
    responseElement.textContent = 'Loading...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: queryText,
                userId: userId || undefined
            })
        });
        
        const data = await response.json();
        responseElement.textContent = JSON.stringify(data, null, 2);
        
        // If we have restaurant results with coordinates, show them on the map
        if (data.success && data.data && data.data.length > 0) {
            showMap(data.data);
        }
    } catch (error) {
        responseElement.textContent = `Error: ${error.message}`;
        console.error('Query Error:', error);
    }
}

// Voice Recognition
let recognition;
let isRecording = false;

function startRecording() {
    const voiceBtn = document.getElementById('voice-btn');
    const recordingStatus = document.getElementById('recording-status');
    const transcription = document.getElementById('transcription');
    
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        recordingStatus.textContent = 'Speech recognition not supported in this browser';
        return;
    }
    
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    
    recognition.onstart = () => {
        isRecording = true;
        voiceBtn.classList.add('recording');
        recordingStatus.textContent = 'Recording...';
        transcription.value = '';
    };
    
    recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }
        
        transcription.value = finalTranscript || interimTranscript;
    };
    
    recognition.onerror = (event) => {
        console.error('Speech Recognition Error:', event.error);
        recordingStatus.textContent = `Error: ${event.error}`;
        stopRecording();
    };
    
    recognition.onend = () => {
        stopRecording();
    };
    
    recognition.start();
}

function stopRecording() {
    if (recognition && isRecording) {
        recognition.stop();
        isRecording = false;
        document.getElementById('voice-btn').classList.remove('recording');
        document.getElementById('recording-status').textContent = 'Recording stopped';
    }
}

// Process Voice Query
async function handleVoiceQuery() {
    const userId = document.getElementById('voice-user-id').value.trim();
    const transcription = document.getElementById('transcription').value.trim();
    const responseElement = document.getElementById('voice-response');
    
    if (!userId) {
        responseElement.textContent = 'Please enter a user ID';
        return;
    }
    
    if (!transcription) {
        responseElement.textContent = 'No transcription available. Please record your voice query first.';
        return;
    }
    
    responseElement.textContent = 'Loading...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/voice`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                userId,
                transcription
            })
        });
        
        const data = await response.json();
        responseElement.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        responseElement.textContent = `Error: ${error.message}`;
        console.error('Voice Query Error:', error);
    }
}

// Preferences Endpoints
async function getPreferences() {
    const userId = document.getElementById('pref-user-id').value.trim();
    const responseElement = document.getElementById('pref-response');
    
    if (!userId) {
        responseElement.textContent = 'Please enter a user ID';
        return;
    }
    
    responseElement.textContent = 'Loading...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/preferences/${userId}`);
        const data = await response.json();
        responseElement.textContent = JSON.stringify(data, null, 2);
        
        // If successful, populate the preferences textarea
        if (data.success && data.data) {
            document.getElementById('preferences').value = JSON.stringify(data.data, null, 2);
        }
    } catch (error) {
        responseElement.textContent = `Error: ${error.message}`;
        console.error('Get Preferences Error:', error);
    }
}

async function savePreferences() {
    const userId = document.getElementById('pref-user-id').value.trim();
    const preferencesText = document.getElementById('preferences').value.trim();
    const responseElement = document.getElementById('pref-response');
    
    if (!userId) {
        responseElement.textContent = 'Please enter a user ID';
        return;
    }
    
    if (!preferencesText) {
        responseElement.textContent = 'Please enter preferences';
        return;
    }
    
    let preferences;
    try {
        preferences = JSON.parse(preferencesText);
    } catch (e) {
        responseElement.textContent = 'Invalid JSON format for preferences';
        return;
    }
    
    responseElement.textContent = 'Loading...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/preferences`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                userId,
                preferences
            })
        });
        
        const data = await response.json();
        responseElement.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        responseElement.textContent = `Error: ${error.message}`;
        console.error('Save Preferences Error:', error);
    }
}

// Feedback Endpoints
async function getRestaurantFeedback() {
    const restaurantId = document.getElementById('restaurant-id').value.trim();
    const responseElement = document.getElementById('feedback-response');
    
    if (!restaurantId) {
        responseElement.textContent = 'Please enter a restaurant ID';
        return;
    }
    
    responseElement.textContent = 'Loading...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/feedback/restaurant/${restaurantId}`);
        const data = await response.json();
        responseElement.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        responseElement.textContent = `Error: ${error.message}`;
        console.error('Get Restaurant Feedback Error:', error);
    }
}

async function getUserFeedback() {
    const userId = document.getElementById('feedback-user-id').value.trim();
    const responseElement = document.getElementById('feedback-response');
    
    if (!userId) {
        responseElement.textContent = 'Please enter a user ID';
        return;
    }
    
    responseElement.textContent = 'Loading...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/feedback/user/${userId}`);
        const data = await response.json();
        responseElement.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        responseElement.textContent = `Error: ${error.message}`;
        console.error('Get User Feedback Error:', error);
    }
}

async function saveFeedback() {
    const userId = document.getElementById('feedback-user-id').value.trim();
    const restaurantId = document.getElementById('restaurant-id').value.trim();
    const rating = document.getElementById('rating').value;
    const comment = document.getElementById('comment').value.trim();
    const responseElement = document.getElementById('feedback-response');
    
    if (!userId || !restaurantId) {
        responseElement.textContent = 'Please enter both user ID and restaurant ID';
        return;
    }
    
    responseElement.textContent = 'Loading...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/feedback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                userId,
                restaurantId,
                rating: parseInt(rating),
                comment: comment || undefined
            })
        });
        
        const data = await response.json();
        responseElement.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        responseElement.textContent = `Error: ${error.message}`;
        console.error('Save Feedback Error:', error);
    }
}

// Suggestions Endpoint
async function getSuggestions() {
    const userId = document.getElementById('suggestions-user-id').value.trim();
    const context = document.getElementById('context').value.trim();
    const responseElement = document.getElementById('suggestions-response');
    
    if (!userId) {
        responseElement.textContent = 'Please enter a user ID';
        return;
    }
    
    responseElement.textContent = 'Loading...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/suggestions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                userId,
                context: context || undefined
            })
        });
        
        const data = await response.json();
        responseElement.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        responseElement.textContent = `Error: ${error.message}`;
        console.error('Get Suggestions Error:', error);
    }
}

// Map Functionality
function showMap(restaurants) {
    const mapElement = document.getElementById('map');
    mapElement.classList.remove('d-none');
    
    // Initialize map if it doesn't exist
    if (!map) {
        map = new google.maps.Map(mapElement, {
            center: { lat: 37.7749, lng: -122.4194 }, // San Francisco
            zoom: 12
        });
    }
    
    // Clear existing markers
    markers.forEach(marker => marker.setMap(null));
    markers = [];
    
    // Add markers for each restaurant
    const bounds = new google.maps.LatLngBounds();
    
    restaurants.forEach((restaurant, index) => {
        if (restaurant.coordinates && restaurant.coordinates.lat && restaurant.coordinates.lng) {
            const position = {
                lat: restaurant.coordinates.lat,
                lng: restaurant.coordinates.lng
            };
            
            const marker = new google.maps.Marker({
                position,
                map,
                title: restaurant.name,
                label: (index + 1).toString()
            });
            
            const infoWindow = new google.maps.InfoWindow({
                content: `
                    <div>
                        <h5>${restaurant.name}</h5>
                        <p>${restaurant.address}</p>
                        <p>Rating: ${restaurant.rating} (${restaurant.userRatingsTotal} reviews)</p>
                        <p>Price Level: ${Array(restaurant.priceLevel || 0).fill('$').join('')}</p>
                        ${restaurant.isOpen ? '<p class="text-success">Open Now</p>' : '<p class="text-danger">Closed</p>'}
                    </div>
                `
            });
            
            marker.addListener('click', () => {
                infoWindow.open(map, marker);
            });
            
            markers.push(marker);
            bounds.extend(position);
        }
    });
    
    // Adjust map to fit all markers
    if (markers.length > 0) {
        map.fitBounds(bounds);
    }
}

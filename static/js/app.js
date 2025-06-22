// Global variables
let map;
let markers = [];

/**
 * Initialize the map
 */
function initMap() {
    // Default to San Francisco coordinates
    const defaultLocation = { lat: 37.7749, lng: -122.4194 };
    
    map = new google.maps.Map(document.getElementById("map"), {
        center: defaultLocation,
        zoom: 13,
        styles: [
            {
                featureType: "poi.business",
                stylers: [{ visibility: "on" }],
            },
            {
                featureType: "poi.park",
                stylers: [{ visibility: "on" }],
            },
        ],
    });

    console.log("Map initialized");
}

/**
 * Clear all markers from the map
 */
function clearMarkers() {
    for (let marker of markers) {
        marker.setMap(null);
    }
    markers = [];
}

/**
 * Create a restaurant card
 */
function createRestaurantCard(restaurant, index) {
    const col = document.createElement('div');
    col.className = 'col';
    
    // Use the photo URL from the API response
    let imageUrl = 'https://via.placeholder.com/300x180?text=No+Image+Available';
    if (restaurant.photos && restaurant.photos.length > 0) {
        imageUrl = restaurant.photos[0];
    }
    
    // Create price level indicators
    let priceLevel = '';
    if (typeof restaurant.price_level !== 'undefined') {
        for (let i = 0; i < 4; i++) {
            if (i < restaurant.price_level) {
                priceLevel += '<i class="bi bi-currency-dollar active"></i>';
            } else {
                priceLevel += '<i class="bi bi-currency-dollar"></i>';
            }
        }
    }
    
    // Create the card HTML
    col.innerHTML = `
        <div class="card restaurant-card h-100">
            <img src="${imageUrl}" class="card-img-top restaurant-img" alt="${restaurant.name}">
            <div class="card-body">
                <h5 class="card-title">${index + 1}. ${restaurant.name}</h5>
                <p class="card-text">${restaurant.address}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <div class="rating">
                        <span class="badge bg-success">${restaurant.rating} ⭐</span>
                        <small class="text-muted">(${restaurant.user_ratings_total} reviews)</small>
                    </div>
                    <div class="price-level">${priceLevel}</div>
                </div>
            </div>
            <div class="card-footer">
                <small class="text-muted">${restaurant.types ? restaurant.types.join(', ') : 'Restaurant'}</small>
            </div>
        </div>
    `;
    
    return col;
}

/**
 * Display restaurant results
 */
function displayResults(restaurants, resultsList) {
    if (!resultsList) {
        console.error('Results list element not found');
        return;
    }
    
    resultsList.innerHTML = '';
    
    // Clear existing markers
    clearMarkers();
    
    // Create bounds object to fit all markers
    const bounds = new google.maps.LatLngBounds();
    
    restaurants.forEach((restaurant, index) => {
        // Add restaurant card to the list
        resultsList.appendChild(createRestaurantCard(restaurant, index));
        
        // Add marker to the map if map is initialized
        if (map && restaurant.location && restaurant.location.lat && restaurant.location.lng) {
            const position = {
                lat: restaurant.location.lat,
                lng: restaurant.location.lng
            };
            
            const marker = new google.maps.Marker({
                position: position,
                map: map,
                title: restaurant.name,
                label: {
                    text: (index + 1).toString(),
                    color: 'white'
                },
                animation: google.maps.Animation.DROP
            });
            
            // Add info window
            const infoWindow = new google.maps.InfoWindow({
                content: `
                    <div class="info-window">
                        <h5>${restaurant.name}</h5>
                        <p>${restaurant.address}</p>
                        <p>Rating: ${restaurant.rating} ⭐ (${restaurant.user_ratings_total} reviews)</p>
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
    
    // Fit map to bounds if there are markers and map is initialized
    if (map && markers.length > 0) {
        map.fitBounds(bounds);
        
        // Zoom out a bit if there's only one marker
        if (markers.length === 1) {
            google.maps.event.addListenerOnce(map, 'bounds_changed', () => {
                map.setZoom(15);
            });
        }
    }
}

// Document ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Food Discovery app initializing...');
    
    // Get DOM elements
    const queryInput = document.getElementById('query-input');
    const locationInput = document.getElementById('location-input');
    const searchBtn = document.getElementById('search-btn');
    const resultsContainer = document.getElementById('results-container');
    const resultsList = document.getElementById('restaurants-container');
    const resultsSummary = document.getElementById('results-summary');
    const queryTransformation = document.getElementById('query-transformation');
    const agentIcon = document.querySelector('.agent-icon');
    
    // Search button click event
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            handleSearchQuery();
        });
    } else {
        console.error('Search button not found in the DOM');
    }
    
    // Enter key press in search input
    if (queryInput) {
        queryInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleSearchQuery();
            }
        });
        // Set focus on query input
        queryInput.focus();
    } else {
        console.error('Query input not found in the DOM');
    }
    
    // Handle search function
    function handleSearchQuery() {
        const query = queryInput ? queryInput.value.trim() : '';
        const location = locationInput ? locationInput.value.trim() : 'San Francisco';
        
        if (!query) {
            alert('Please enter a search query');
            return;
        }
        
        // Show loading state
        if (searchBtn) {
            searchBtn.disabled = true;
            searchBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Asking agent...';
        }
        
        if (resultsSummary) {
            resultsSummary.textContent = 'Searching for restaurants...';
        }
        
        if (resultsContainer) {
            resultsContainer.classList.remove('d-none');
        }
        
        if (resultsList) {
            resultsList.innerHTML = '';
        }
        
        // Show agent thinking animation
        if (agentIcon) {
            agentIcon.classList.add('agent-thinking');
        }
        
        // Scroll to results
        if (resultsContainer) {
            resultsContainer.scrollIntoView({ behavior: 'smooth' });
        }
        
        // Make API request
        fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                query: query,
                location: location 
            })
        })
        .then(response => response.json())
        .then(data => {
            // Reset button state
            if (searchBtn) {
                searchBtn.disabled = false;
                searchBtn.innerHTML = '<i class="bi bi-search"></i> Ask Agent';
            }
            
            // Remove agent thinking animation
            if (agentIcon) {
                agentIcon.classList.remove('agent-thinking');
            }
            
            if (data.error) {
                if (resultsSummary) {
                    resultsSummary.textContent = `Error: ${data.error}`;
                }
                return;
            }
            
            if (!data.results || data.results.length === 0) {
                if (resultsSummary) {
                    resultsSummary.textContent = 'No restaurants found. Please try a different query.';
                }
                return;
            }
            
            // Agent understanding display removed as requested
            
            // Update results summary
            if (resultsSummary) {
                resultsSummary.textContent = `Found ${data.count} restaurants matching your query in ${location}.`;
            }
            
            // Display results
            if (resultsList && data.results) {
                displayResults(data.results, resultsList);
            }
            
            // Initialize map if available
            if (typeof google !== 'undefined' && google.maps && data.results) {
                initMap(data.results);
            } else {
                console.error('Google Maps API not loaded');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            
            if (searchBtn) {
                searchBtn.disabled = false;
                searchBtn.innerHTML = '<i class="bi bi-search"></i> Ask Agent';
            }
            
            if (agentIcon) {
                agentIcon.classList.remove('agent-thinking');
            }
            
            if (resultsSummary) {
                resultsSummary.textContent = `Error: ${error.message}`;
            }
        });
    }
    
    // Log that initialization is complete
    console.log('Food Discovery app initialized');
});

// Initialize map when Google Maps API loads
window.initMap = initMap;

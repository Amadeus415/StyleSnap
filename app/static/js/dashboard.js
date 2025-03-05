/**
 * Dashboard JavaScript functionality for StyleSnap
 * Handles section toggling, product carousel scrolling, and photo loading
 */

/**
 * Toggles the visibility of a category's content section
 * @param {string} category - The category identifier (e.g., 'hair', 'skin', etc.)
 */
function toggleSection(category) {
    const content = document.getElementById(`${category}Content`);
    const arrow = document.getElementById(`${category}Arrow`);
    const buttonText = document.getElementById(`${category}ButtonText`);
    
    if (content.classList.contains('hidden')) {
        // Show content
        content.classList.remove('hidden');
        arrow.style.transform = 'rotate(180deg)';
        buttonText.textContent = 'Hide Tips';
    } else {
        // Hide content
        content.classList.add('hidden');
        arrow.style.transform = 'rotate(0deg)';
        buttonText.textContent = 'Show Tips';
    }
}

/**
 * Scrolls the product carousel in the specified direction
 * @param {string} category - The category identifier
 * @param {string} direction - The scroll direction ('left' or 'right')
 */
function scrollProducts(category, direction) {
    const container = document.getElementById(`${category}Products`);
    const scrollAmount = 200; // Adjust as needed
    
    if (direction === 'left') {
        container.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    } else {
        container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
}

/**
 * Loads a user photo using a presigned URL from the server
 * This function handles the entire process of:
 * 1. Fetching the presigned URL from our server
 * 2. Loading the image with that URL
 * 3. Handling any errors that might occur
 * 
 * @param {number} photoId - The ID of the photo to load
 * @param {string} containerId - The ID of the container element where the photo should be displayed
 */
function loadUserPhoto(photoId, containerId) {
    // Get references to the container and loading text elements
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container not found: ${containerId}`);
        return;
    }
    
    // Find or create the loading text element
    let loadingText = container.querySelector('.loading-text');
    if (!loadingText) {
        loadingText = document.createElement('span');
        loadingText.className = 'loading-text text-white text-xs';
        loadingText.textContent = 'Loading...';
        container.appendChild(loadingText);
    }
    
    // If no photo ID is provided, show "No Photo" message
    if (!photoId) {
        loadingText.textContent = 'No Photo';
        return;
    }
    
    // First fetch the presigned URL from our API
    fetch(`/photo/${photoId}`)
        .then(response => {
            // Check if the response is OK (status 200-299)
            if (!response.ok) {
                throw new Error(`Failed to get presigned URL: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            // Verify that the response contains a URL
            if (!data.url) {
                throw new Error('No URL in response');
            }
            
            // Now load the image with the presigned URL
            const img = new Image();
            
            img.onload = function() {
                // Image loaded successfully - clear the container and add the image
                container.innerHTML = '';
                img.className = 'h-full w-full object-cover rounded-md';
                container.appendChild(img);
            };
            
            img.onerror = function() {
                // Image failed to load - show error message
                console.error('Failed to load image with presigned URL:', data.url);
                container.innerHTML = '';
                const errorText = document.createElement('span');
                errorText.className = 'text-white text-xs';
                errorText.textContent = 'Image unavailable';
                container.appendChild(errorText);
            };
            
            // Load the image with the presigned URL
            img.src = data.url;
        })
        .catch(error => {
            // Handle any errors in the fetch or image loading process
            console.error('Error loading photo:', error);
            container.innerHTML = '';
            const errorText = document.createElement('span');
            errorText.className = 'text-white text-xs';
            errorText.textContent = 'Error loading image';
            container.appendChild(errorText);
        });
}

/**
 * Initialize all user photos on the dashboard
 * This function is called when the DOM content is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get all photo containers that need to be loaded
    const photoContainers = document.querySelectorAll('[data-photo-id]');
    
    // Load each photo
    photoContainers.forEach(container => {
        const photoId = container.getAttribute('data-photo-id');
        if (photoId) {
            loadUserPhoto(photoId, container.id);
        }
    });
});

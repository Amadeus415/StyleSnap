/**
 * Photo Thumbnails JavaScript
 * 
 * This script is responsible for loading photo thumbnails in the dashboard photo analysis popup.
 * It fetches photo URLs from the server and displays them in their containers.
 * 
 * Key features:
 * - Automatically loads all photo thumbnails when the page loads
 * - Fetches presigned URLs from the server for secure S3 access
 * - Handles loading states and errors gracefully
 * - Optimized for performance with efficient DOM operations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize photo thumbnails as soon as the DOM is ready
    loadPhotoThumbnails();
});

/**
 * Loads all photo thumbnails in the dashboard
 * 
 * This function:
 * 1. Finds all photo container elements in the DOM
 * 2. Extracts the photo ID from each container
 * 3. Calls loadPhotoThumbnail for each valid photo ID
 */
function loadPhotoThumbnails() {
    console.log('Loading photo thumbnails...');
    
    // Get all photo containers (elements with IDs starting with "photoContainer")
    const photoContainers = document.querySelectorAll('[id^="photoContainer"]');
    console.log(`Found ${photoContainers.length} photo containers`);
    
    // Load each photo
    photoContainers.forEach((container, index) => {
        // Get photo ID from data attribute
        const photoId = container.dataset.photoId;
        
        if (photoId) {
            console.log(`Loading photo ID ${photoId} into container ${container.id}`);
            loadPhotoThumbnail(container, photoId);
        } else {
            console.warn(`No photo ID found for container ${container.id}`);
            // Show "No Photo" message
            container.innerHTML = '<span class="text-gray-600 text-xs">No Photo</span>';
        }
    });
}

/**
 * Loads a photo thumbnail into a container for popup analysis
 * 
 * This function:
 * 1. Shows a loading indicator
 * 2. Fetches the photo URL from the server
 * 3. Creates and displays the image
 * 4. Handles any errors that might occur
 * 
 * @param {HTMLElement} container - The container to load the photo into
 * @param {string} photoId - The ID of the photo to load
 */
function loadPhotoThumbnail(container, photoId) {
    // Show loading state
    container.innerHTML = '<span class="loading-text text-gray-600 text-xs">Loading...</span>';
    
    // Fetch the photo URL from the server
    fetch(`/photo/${photoId}`)
        .then(response => {
            // Check if the response is OK (status 200-299)
            if (!response.ok) {
                throw new Error(`Failed to load photo: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            // Verify that the response contains a URL
            if (!data.url) {
                throw new Error('No URL in response');
            }
            
            // Create an image element with proper attributes
            const img = new Image();
            
            // Set up onload handler before setting src to ensure it catches the load event
            img.onload = function() {
                // Image loaded successfully - clear the container and add the image
                container.innerHTML = '';
                container.appendChild(img);
            };
            
            // Set up error handler
            img.onerror = function() {
                console.error('Failed to load image with URL:', data.url);
                container.innerHTML = '<span class="text-red-500 text-xs">Image unavailable</span>';
            };
            
            // Set image attributes
            img.src = data.url;
            img.className = 'h-full w-full object-cover rounded-md';
            img.alt = 'User photo';
            img.setAttribute('loading', 'lazy'); // Use lazy loading for better performance
        })
        .catch(error => {
            // Handle any errors in the fetch or image loading process
            console.error('Error loading photo thumbnail:', error);
            container.innerHTML = '<span class="text-red-500 text-xs">Failed to load</span>';
        });
} 
/**
 * Photo Popup JavaScript
 * 
 * This script handles the display of a full-screen popup when a photo card is clicked.
 * It uses AJAX to fetch the popup content from the server and handles the popup lifecycle.
 * 
 * Features:
 * - Loads popup content dynamically from the server
 * - Shows loading indicator during fetch
 * - Handles popup closing
 * - Prevents body scrolling when popup is open
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize popup functionality for all photo cards
    initializePhotoPopups();
});

/**
 * Initializes click handlers for all photo cards
 */
function initializePhotoPopups() {
    // Get all photo cards
    const photoCards = document.querySelectorAll('.photo-card');
    
    // Add click event listener to each photo card
    photoCards.forEach(card => {
        card.addEventListener('click', function() {
            // Get the photo ID from the data attribute
            const photoId = this.dataset.photoId;
            if (!photoId) {
                console.error('No photo ID found on card');
                return;
            }
            
            // Show loading indicator
            showLoadingIndicator();
            
            // Load and show the popup
            loadPhotoPopup(photoId);
        });
    });
}

/**
 * Shows a loading indicator while the popup is being loaded
 */
function showLoadingIndicator() {
    // Create a simple loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.id = 'popup-loading';
    loadingIndicator.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    loadingIndicator.innerHTML = `
        <div class="bg-white p-4 rounded-lg shadow-lg">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-gray-900 mx-auto"></div>
            <p class="text-center mt-2">Loading analysis...</p>
        </div>
    `;
    
    // Add the loading indicator to the document
    document.body.appendChild(loadingIndicator);
}

/**
 * Removes the loading indicator
 */
function removeLoadingIndicator() {
    const loadingIndicator = document.getElementById('popup-loading');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

/**
 * Loads the photo popup template from the server and displays it
 * 
 * @param {string} photoId - The ID of the photo to display
 */
function loadPhotoPopup(photoId) {
    // Fetch the popup HTML from the server
    fetch(`/photo_popup/${photoId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to load popup: ${response.status} ${response.statusText}`);
            }
            return response.text();
        })
        .then(html => {
            // Remove loading indicator
            removeLoadingIndicator();
            
            // Add the popup HTML to the document
            document.body.insertAdjacentHTML('beforeend', html);
            
            // Add event listener to the back button
            const backButton = document.getElementById('popup-back-button');
            if (backButton) {
                backButton.addEventListener('click', closePhotoPopup);
            }
            
            // Add event listener to close on escape key
            document.addEventListener('keydown', handleEscapeKey);
            
            // Prevent scrolling on the body when popup is open
            document.body.style.overflow = 'hidden';
            
            // Initialize any additional functionality for the popup
            initializePopupFunctionality();
        })
        .catch(error => {
            console.error('Error loading popup:', error);
            removeLoadingIndicator();
            
            // Show error message
            alert('Failed to load photo details. Please try again.');
        });
}

/**
 * Handles escape key press to close the popup
 * 
 * @param {KeyboardEvent} event - The keyboard event
 */
function handleEscapeKey(event) {
    if (event.key === 'Escape') {
        closePhotoPopup();
    }
}

/**
 * Initializes additional functionality for the popup
 * This can include things like swipe gestures, additional buttons, etc.
 */
function initializePopupFunctionality() {
    // Add any additional functionality here
    
    // Example: Close popup when clicking outside the content area
    document.getElementById('photo-popup').addEventListener('click', function(event) {
        // Only close if clicking directly on the popup background (not its children)
        if (event.target === this) {
            closePhotoPopup();
        }
    });
}

/**
 * Closes the photo popup
 */
function closePhotoPopup() {
    const popup = document.getElementById('photo-popup');
    if (popup) {
        // Remove the popup from the DOM
        popup.remove();
        
        // Restore scrolling on the body
        document.body.style.overflow = '';
        
        // Remove escape key event listener
        document.removeEventListener('keydown', handleEscapeKey);
    }
} 
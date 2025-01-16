/**
 * Dashboard JavaScript functionality for StyleSnap
 * Handles section toggling and product carousel scrolling
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
 * Scrolls the product carousel for a specific category
 * @param {string} category - The category identifier (e.g., 'hair', 'skin', etc.)
 * @param {string} direction - The scroll direction ('left' or 'right')
 */
function scrollProducts(category, direction) {
    const container = document.getElementById(`${category}Products`);
    const scrollAmount = 300; // Pixels to scroll
    
    if (direction === 'left') {
        container.scrollBy({
            left: -scrollAmount,
            behavior: 'smooth'
        });
    } else {
        container.scrollBy({
            left: scrollAmount,
            behavior: 'smooth'
        });
    }
}

// Initialize all sections when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Add any initialization code here if needed
    console.log('Dashboard initialized');
});

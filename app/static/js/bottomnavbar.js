/**
 * Bottom Navigation Bar for StyleSnap
 * Handles section switching and active button styling
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get all section buttons
    const sectionButtons = document.querySelectorAll('nav button[data-section]');
    
    // Get all content sections
    const sections = {
        photos: document.getElementById('photos-section'),
        routine: document.getElementById('routine-section'),
        products: document.getElementById('products-section')
    };
    
    // Function to show a section and hide others
    function showSection(sectionId) {
        // Hide all sections
        Object.values(sections).forEach(section => {
            if (section) {
                section.classList.add('hidden');
            }
        });
        
        // Show the selected section
        if (sections[sectionId]) {
            sections[sectionId].classList.remove('hidden');
        }
        
        // Update button styling
        sectionButtons.forEach(button => {
            const buttonSection = button.getAttribute('data-section');
            
            if (buttonSection === sectionId) {
                // Active button - blue text
                button.classList.remove('text-black');
                button.classList.add('text-blue-500');
            } else {
                // Inactive button - gray text
                button.classList.remove('text-blue-500');
                button.classList.add('text-black');
            }
        });
    }
    
    // Add click event listeners to all section buttons
    sectionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const sectionId = this.getAttribute('data-section');
            showSection(sectionId);
        });
    });
    
    // Initialize with Photos section visible by default
    showSection('photos');
});

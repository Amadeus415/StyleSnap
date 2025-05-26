/**
 * Tailored Plan JavaScript
 * Handles the generation and display of tailored skincare/lifestyle plans
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get the button element
    const generatePlanBtn = document.getElementById('generate-tailored-plan-btn');
    
    // If the button exists on this page
    if (generatePlanBtn) {
        // Add click event listener
        generatePlanBtn.addEventListener('click', generateTailoredPlan);
    }
});

/**
 * Generate a tailored plan by calling the API endpoint
 */
function generateTailoredPlan() {
    // Show loading state
    const generatePlanBtn = document.getElementById('generate-tailored-plan-btn');
    const originalBtnText = generatePlanBtn.textContent;
    generatePlanBtn.textContent = 'Generating...';
    generatePlanBtn.disabled = true;
    generatePlanBtn.classList.add('opacity-75');
    
    // Call the API endpoint
    fetch('/generate_tailored_plan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Display the tailored plan
        displayTailoredPlan(data);
        
        // Reset button state
        generatePlanBtn.textContent = originalBtnText;
        generatePlanBtn.disabled = false;
        generatePlanBtn.classList.remove('opacity-75');
    })
    .catch(error => {
        console.error('Error generating tailored plan:', error);
        
        // Show error message
        const resultsDiv = document.getElementById('tailored-plan-results');
        resultsDiv.classList.remove('hidden');
        resultsDiv.innerHTML = `
            <h2 class="text-xl font-semibold text-gray-800 mb-2">Error</h2>
            <p class="text-red-600">There was an error generating your tailored plan. Please try again later.</p>
        `;
        
        // Reset button state
        generatePlanBtn.textContent = originalBtnText;
        generatePlanBtn.disabled = false;
        generatePlanBtn.classList.remove('opacity-75');
    });
}

/**
 * Display the tailored plan in the UI
 * @param {Object} data - The tailored plan data from the API
 */
function displayTailoredPlan(data) {
    // Get the results container
    const resultsDiv = document.getElementById('tailored-plan-results');
    const recommendationsDiv = document.getElementById('tailored-recommendations');
    
    // Clear previous recommendations
    recommendationsDiv.innerHTML = '';
    
    // Check if we have recommendations
    if (data.recommendations && data.recommendations.length > 0) {
        // Show the results container
        resultsDiv.classList.remove('hidden');
        
        // Add each recommendation
        data.recommendations.forEach((rec, index) => {
            const recElement = document.createElement('div');
            recElement.className = 'bg-white rounded-lg p-3 shadow-sm border border-yellow-200';
            recElement.innerHTML = `
                <h3 class="text-lg font-semibold text-gray-800">${index + 1}. ${rec.product}</h3>
                <p class="text-gray-700 mb-2"><strong>Why:</strong> ${rec.reason}</p>
                <p class="text-gray-700"><strong>How to use:</strong> ${rec.usage_instructions}</p>
            `;
            recommendationsDiv.appendChild(recElement);
        });
    } else {
        // Show error message if no recommendations
        resultsDiv.classList.remove('hidden');
        recommendationsDiv.innerHTML = `
            <p class="text-red-600">No recommendations found. Please try again later.</p>
        `;
    }
    
    // Scroll to the results
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
} 
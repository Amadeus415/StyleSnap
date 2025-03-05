document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.image-comparison-container');
    const handle = document.querySelector('.comparison-handle');
    const beforeImage = document.querySelector('.before-image');
    const afterImage = document.querySelector('.after-image');
    
    if (!container || !handle || !beforeImage || !afterImage) return;
    
    let isDragging = false;
    
    // Set initial position
    function setPosition(x) {
        const containerWidth = container.offsetWidth;
        // Constrain x to container bounds
        x = Math.max(0, Math.min(x, containerWidth));
        
        // Calculate position as percentage
        const position = (x / containerWidth) * 100;
        
        // Update handle position
        handle.style.left = `${position}%`;
        
        // Update clip path for the after image
        afterImage.style.clipPath = `inset(0 ${100 - position}% 0 0)`;
    }
    
    // Initialize position at 50%
    setPosition(container.offsetWidth / 2);
    
    // Handle mouse events
    handle.addEventListener('mousedown', function(e) {
        isDragging = true;
        e.preventDefault(); // Prevent text selection
    });
    
    container.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        
        // Get mouse position relative to container
        const rect = container.getBoundingClientRect();
        const x = e.clientX - rect.left;
        
        setPosition(x);
    });
    
    document.addEventListener('mouseup', function() {
        isDragging = false;
    });
    
    // Handle touch events for mobile
    handle.addEventListener('touchstart', function(e) {
        isDragging = true;
    });
    
    container.addEventListener('touchmove', function(e) {
        if (!isDragging) return;
        
        // Get touch position relative to container
        const rect = container.getBoundingClientRect();
        const touch = e.touches[0];
        const x = touch.clientX - rect.left;
        
        setPosition(x);
        e.preventDefault(); // Prevent scrolling while dragging
    });
    
    document.addEventListener('touchend', function() {
        isDragging = false;
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        // Maintain the same percentage position when window is resized
        const position = parseFloat(handle.style.left) || 50;
        setPosition((position / 100) * container.offsetWidth);
    });
}); 
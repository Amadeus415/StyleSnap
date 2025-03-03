document.addEventListener('DOMContentLoaded', function() {
    const footer = document.getElementById('scrollFooter');
    let lastScrollTop = 0;
    let footerVisible = false;
    const scrollThreshold = 15; // Show after scrolling 30% down

    window.addEventListener('scroll', function() {
        // Calculate scroll percentage
        const scrollHeight = document.documentElement.scrollHeight;
        const windowHeight = window.innerHeight;
        const scrollTop = window.scrollY;
        const scrollPercentage = (scrollTop / (scrollHeight - windowHeight)) * 100;
        
        // Determine scroll direction
        const scrollingDown = scrollTop > lastScrollTop;
        lastScrollTop = scrollTop;
        
        // Show footer when scrolling down past threshold
        if (scrollingDown && scrollPercentage > scrollThreshold && !footerVisible) {
            footer.classList.remove('translate-y-full');
            footerVisible = true;
        } 
        // Hide footer when scrolling up
        else if (!scrollingDown && footerVisible) {
            footer.classList.add('translate-y-full');
            footerVisible = false;
        }
    });
});
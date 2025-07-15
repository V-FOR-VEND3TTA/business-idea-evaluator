document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Update score value display for range inputs
    function updateScoreValue(input) {
        const displayElement = document.getElementById('scoreValue');
        if (displayElement) {
            displayElement.textContent = input.value;
        }
    }
    
    // Set up event listeners for any existing range inputs
    const rangeInputs = document.querySelectorAll('input[type="range"]');
    rangeInputs.forEach(input => {
        input.addEventListener('input', function() {
            updateScoreValue(this);
        });
        // Initialize displayed value
        updateScoreValue(input);
    });
});
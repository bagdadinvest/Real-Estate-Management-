document.addEventListener('DOMContentLoaded', function() {
    const languageSelect = document.querySelector('.language-select');
    const wrapper = document.querySelector('.language-select-wrapper');
    
    if (languageSelect && wrapper) {
        // Set initial flag
        wrapper.setAttribute('data-lang', languageSelect.value);
        
        // Update flag when selection changes
        languageSelect.addEventListener('change', function() {
            wrapper.setAttribute('data-lang', this.value);
        });
    }
});
// static/admin/js/product_admin.js
document.addEventListener('DOMContentLoaded', function() {
    const categoryField = document.getElementById('id_category');
    const shadePanel = document.querySelector('.shade-panel');
    
    // Function to check if it's a paint category
    function isPaintCategory() {
        if (!categoryField) return false;
        
        const categoryOption = categoryField.options[categoryField.selectedIndex];
        if (!categoryOption) return false;
        
        return categoryOption.text.toLowerCase().includes('paint');
    }
    
    // Function to toggle shade panel visibility
    function toggleShadePanel() {
        if (shadePanel) {
            if (isPaintCategory()) {
                shadePanel.style.display = 'block';
            } else {
                shadePanel.style.display = 'none';
            }
        }
    }
    
    // Add event listener to category field
    if (categoryField) {
        categoryField.addEventListener('change', toggleShadePanel);
    }
    
    // Initial check
    toggleShadePanel();
});
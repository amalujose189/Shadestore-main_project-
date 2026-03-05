// static/admin/js/color_picker.js
document.addEventListener('DOMContentLoaded', function() {
    const initColorPickers = function() {
        document.querySelectorAll('.color-shade-container').forEach(function(container) {
            const hiddenInput = container.querySelector('.color-shade-widget');
            const colorsList = container.querySelector('.colors-list');
            const newColorPicker = container.querySelector('.new-color-picker');
            const newColorQuantity = container.querySelector('.new-color-quantity');
            const addColorBtn = container.querySelector('.add-color-btn');
            
            // Find the available_shades_json hidden input
            const availableShadesInput = document.getElementById('id_available_shades_json');

            // Initialize the hidden inputs with current colors if empty
            if (!hiddenInput.value) {
                hiddenInput.value = '{}';
            }
            
            // If we have initial data in the availableShadesInput, use that
            if (availableShadesInput && availableShadesInput.value) {
                try {
                    // Parse the initial JSON data
                    const initialData = JSON.parse(availableShadesInput.value);
                    
                    // Clear any existing color items
                    colorsList.innerHTML = '';
                    
                    // Create color items for each shade
                    Object.entries(initialData).forEach(([color, quantity]) => {
                        addColorToList(color, quantity);
                    });
                    
                    // Update the original hidden input as well
                    hiddenInput.value = availableShadesInput.value;
                } catch (e) {
                    console.error('Error parsing initial shade data:', e);
                }
            }

            // Function to add a color item to the list
            function addColorToList(color, quantity) {
                // Create new color item
                const newItem = document.createElement('div');
                newItem.className = 'color-item';
                newItem.dataset.color = color;
                
                newItem.innerHTML = `
                    <div class="color-swatch" style="background-color: ${color}"></div>
                    <span class="color-code">${color}</span>
                    <input type="number" class="quantity-input" value="${quantity}" min="0">
                    <button type="button" class="remove-color">✕</button>
                `;
                
                // Add event listener to remove button
                newItem.querySelector('.remove-color').addEventListener('click', function() {
                    newItem.remove();
                    updateHiddenInputs();
                });
                
                // Add event listener to quantity input
                newItem.querySelector('.quantity-input').addEventListener('change', updateHiddenInputs);
                
                colorsList.appendChild(newItem);
            }

            // Function to update all hidden inputs with colors and quantities
            function updateHiddenInputs() {
                const colors = {};
                colorsList.querySelectorAll('.color-item').forEach(function(item) {
                    const color = item.dataset.color;
                    const quantity = parseInt(item.querySelector('.quantity-input').value) || 0;
                    colors[color] = quantity;
                });
                
                // Update both hidden inputs with the same JSON data
                const jsonData = JSON.stringify(colors);
                hiddenInput.value = jsonData;
                
                if (availableShadesInput) {
                    availableShadesInput.value = jsonData;
                }
                
                // For debugging
                console.log('Updated shade data:', jsonData);
            }

            // Add a new color when the add button is clicked
            addColorBtn.addEventListener('click', function() {
                const color = newColorPicker.value;
                const quantity = parseInt(newColorQuantity.value) || 1;
                
                // Check if this color already exists
                const existingItem = colorsList.querySelector(`.color-item[data-color="${color}"]`);
                if (existingItem) {
                    existingItem.querySelector('.quantity-input').value = quantity;
                } else {
                    // Add new color to the list
                    addColorToList(color, quantity);
                }
                
                // Update hidden inputs
                updateHiddenInputs();
            });

            // Initial update to ensure everything is synced
            updateHiddenInputs();
        });
    };

    // Initialize when the page loads
    initColorPickers();
    
    // For Django admin inlines, we need to listen for the 'formset:added' event
    document.addEventListener('formset:added', function(e) {
        // Wait a moment for the DOM to update
        setTimeout(initColorPickers, 10);
    });
    
    // Also handle category changes
    const categorySelect = document.getElementById('id_category');
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            // Submit the form to reload with the correct fields for the new category
            const form = categorySelect.closest('form');
            if (form) {
                // Add a hidden field to indicate this is just for updating the form
                let hiddenField = document.getElementById('_update_category');
                if (!hiddenField) {
                    hiddenField = document.createElement('input');
                    hiddenField.type = 'hidden';
                    hiddenField.name = '_update_category';
                    hiddenField.id = '_update_category';
                    hiddenField.value = '1';
                    form.appendChild(hiddenField);
                }
                
                // Submit the form
                form.submit();
            }
        });
    }
});
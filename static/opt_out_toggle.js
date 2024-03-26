document.addEventListener('DOMContentLoaded', function() {
    const optOutCheckbox = document.querySelector('input[name="opt_out"]');
    // Directly reference each day checkbox by name
    const mondayCheckbox = document.querySelector('input[name="monday"]');
    const tuesdayCheckbox = document.querySelector('input[name="tuesday"]');
    const wednesdayCheckbox = document.querySelector('input[name="wednesday"]');
    const thursdayCheckbox = document.querySelector('input[name="thursday"]');
    const fridayCheckbox = document.querySelector('input[name="friday"]');
    const saturdayCheckbox = document.querySelector('input[name="saturday"]');
    const sundayCheckbox = document.querySelector('input[name="sunday"]');

    const dayCheckboxes = [mondayCheckbox, tuesdayCheckbox, wednesdayCheckbox, thursdayCheckbox, fridayCheckbox, saturdayCheckbox, sundayCheckbox];

    function toggleDayCheckboxes(disableAndDeselect) {
        dayCheckboxes.forEach(checkbox => {
            if(checkbox) { // Check if the checkbox exists
                checkbox.disabled = disableAndDeselect;
                checkbox.checked = !disableAndDeselect; // Uncheck if disabling
                // Optionally, add visual indication like changing the background color
                if (disableAndDeselect) {
                    checkbox.closest('div').style.opacity = '0.5';
                } else {
                    checkbox.closest('div').style.opacity = '1';
                }
            }
        });
    }

    optOutCheckbox.addEventListener('change', function() {
        toggleDayCheckboxes(this.checked);
    });

    // Initial check in case of pre-checked opt_out
    toggleDayCheckboxes(optOutCheckbox.checked);
});


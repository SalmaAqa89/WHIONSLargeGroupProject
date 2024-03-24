function getCookie(name) {
    const cookieValue = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return cookieValue ? cookieValue.pop() : '';
}

document.getElementById('deleteButton').addEventListener('click', function() {
    var selectedEntries = Array.from(document.querySelectorAll('.selectCheckbox:checked')).map(cb => cb.getAttribute('data-entry-id'));
  
    if (selectedEntries.length > 0) {
        deleteSelectedEntries(selectedEntries);
    } else {
        alert("Please select at least one entry to delete.");
    }
});

function deleteSelectedEntries(entryIds) {
    fetch('/delete_selected_entries/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ entryIds: entryIds }),
    })
    .then(response => {
        if (response.ok) {
            location.reload();
        } else {
            throw new Error('Failed to delete entries');
        }
    })
    .catch(error => {
        console.error('Error:', error.message);
        alert('Failed to delete entries. Please try again later.');
    });
}

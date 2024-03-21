function showFavJournalSuggestions(query) {
    if (query.length >= 1) {
        fetch(`/search-favouritesuggestion/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                var suggestionsContainer = document.getElementById('Fjournal-suggestions-container');
                suggestionsContainer.innerHTML = ''; 
                data.suggestions.forEach((title) => {
                    var div = document.createElement('div');
                    div.textContent = title;
                    div.onclick = function() {
                        selectSuggestion(title);
                    };
                    suggestionsContainer.appendChild(div);
                });
                suggestionsContainer.style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching search suggestions:', error);
            });
    } else {
        document.getElementById('Fjournal-suggestions-container').style.display = 'none';
    }
}

function selectSuggestion(value) {
  
    var searchBox = document.getElementById('journal-search-box');

    searchBox.value = value;
    document.getElementById('Fjournal-suggestions-container').style.display = 'none';
    searchBox.form.submit();
}

document.getElementById('details-{{ entry.id }}').addEventListener('toggle', function(event) {
    
    
    var summary = document.getElementById('summary-{{ entry.id }}');
    if (this.open) {
      summary.textContent = 'See Less';
    } else {
      summary.textContent = 'See More';
    }
  });
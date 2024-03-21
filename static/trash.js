function showSuggestions(query) {
    if (query.length >= 1) {
        fetch(`/search-suggestions1/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                var suggestionsContainer = document.getElementById('suggestionsContainer');
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
        document.getElementById('suggestionsContainer').style.display = 'none';
    }
}

function selectSuggestion(value) {
    var searchBox = document.getElementById('search-box');
    searchBox.value = value;
    document.getElementById('suggestionsContainer').style.display = 'none';
    searchBox.form.submit();
}


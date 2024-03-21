
document.addEventListener('DOMContentLoaded', (event) => {
    const suggestions = document.querySelectorAll('.search-suggestion');
    suggestions.forEach(function(suggestion) {
      suggestion.addEventListener('click', function() {
        const value = this.textContent || this.innerText; 
        window.location.href = '/search?query=' + encodeURIComponent(value);
      });
    });
    
    });
    



function showJournalSuggestions(query) {
if (query.length >= 1) {
    fetch(`/search-suggestions/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            var suggestionsContainer = document.getElementById('journal-suggestions-container');
           
            suggestionsContainer.innerHTML = '';
            
            data.suggestions.forEach(title => {
                const div = document.createElement('div');
                div.textContent = title;
                div.classList.add('search-suggestion'); 
                div.addEventListener('click', function() {
                    selectJournalSuggestion(title); 
                });
                suggestionsContainer.appendChild(div);
            });
            suggestionsContainer.style.display = 'block';
        });
} else {
    document.getElementById('journal-suggestions-container').innerHTML = '';
    document.getElementById('journal-suggestions-container').style.display = 'none';
}
}


function selectJournalSuggestion(value) {
var searchBox = document.getElementById('journal-search-box');
searchBox.value = value;
document.getElementById('journal-suggestions-container').style.display = 'none';
 searchBox.form.submit();
}
    

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('details').forEach((element) => {
        element.addEventListener('toggle', function(event) {
            const entryId = this.dataset.entryId;
            var summary = document.getElementById(`summary-${entryId}`);
            if (this.open) {
              summary.textContent = 'See Less';
            } else {
              summary.textContent = 'See More';
            }
        });
    });
});

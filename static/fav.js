

function showSuggestions(value) {
 
    if(value.length >= 0) {
      fetch('{% url "search_favouriteSuggestion" %}?q=' + encodeURIComponent(value))
      .then(response => response.json())
      .then(data => {
        let suggestionsHTML = '';
        for(let i = 0; i < data.suggestions.length; i++) {
         
          suggestionsHTML += '<div onclick="selectSuggestion(\'' + data.suggestions[i] + '\')">' + data.suggestions[i] + '</div>';
        }
        document.getElementById('suggestionsContainer').innerHTML = suggestionsHTML;
     
        document.getElementById('suggestionsContainer').style.display = data.suggestions.length > 0 ? 'block' : 'none';
      })
      .catch(error => console.error('Error:', error));
    } else {
      document.getElementById('suggestionsContainer').style.display = 'none';
    }
  }
  

function selectSuggestion(value) {
  document.getElementById('search-box').value = value;
  document.getElementById('suggestionsContainer').innerHTML = '';
}


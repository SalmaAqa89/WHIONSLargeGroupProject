
document.getElementById('journal-search-input').addEventListener('input', function(e) {
    const query = e.target.value; 
    showJournalSuggestions(query);
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

document.addEventListener('DOMContentLoaded', (event) => {
    const suggestions = document.querySelectorAll('.search-suggestion');
    suggestions.forEach(function(suggestion) {
      suggestion.addEventListener('click', function() {
        const value = this.textContent || this.innerText; 
        window.location.href = '/search?query=' + encodeURIComponent(value);
      });
    });
  });


function selectJournalSuggestion(value) {
    var searchBox = document.getElementById('journal-search-box');
    searchBox.value = value;
    document.getElementById('journal-suggestions-container').style.display = 'none';
     searchBox.form.submit();
}
//   function toggleText(entryId) {
//     var preview = document.getElementById('preview-' + entryId);
//     var fullText = document.getElementById('full-text-' + entryId);
//     preview.classList.toggle('d-none');
//     fullText.classList.toggle('d-none');
//   }

// function toggleText(entryId) {
//     var preview = document.getElementById('preview-' + entryId);
//     var fullText = document.getElementById('full-text-' + entryId);

//     // Check if the full text is currently shown
//     if (fullText.classList.contains('d-none')) {
//       // Show the full text and hide the preview
//       preview.classList.add('d-none');
//       fullText.classList.remove('d-none');
//     } else {
//       // Hide the full text and show the preview
//       fullText.classList.add('d-none');
//       preview.classList.remove('d-none');
//     }
//   }


  function openJournalEntryInNewWindow(entryId) {
    var entryText = document.getElementById('full-text-' + entryId).innerHTML;
    var newWindow = window.open("", "_blank", "toolbar=yes,scrollbars=yes,resizable=yes,top=500,left=500,width=400,height=400");
    newWindow.document.write(entryText);
    newWindow.document.write('<p><button onclick="window.close()">Hide</button></p>');
    newWindow.document.close(); 
  }
  


document.getElementById('toggleSelect').addEventListener('click', function() {
    document.querySelectorAll('.selectCheckbox').forEach(function(checkbox) {
      checkbox.style.display = checkbox.style.display === 'none' ? 'block' : 'none';
    });
  
    var exportOptions = document.getElementById('exportOptions');
    exportOptions.style.display = exportOptions.style.display === 'none' ? 'block' : 'none';
  });
  
  function exportSelected(format) {
    var selectedEntries = Array.from(document.querySelectorAll('.selectCheckbox:checked')).map(cb => cb.getAttribute('data-entry-id'));
  
    if (selectedEntries.length > 0) {
      window.location.href = `/export_entries/?entries=${selectedEntries.join(",")}&format=${format}`;
    } else {
      alert("Please select at least one entry to export.");
    }
}
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('details').forEach((element) => {
    const summaryElement = element.querySelector('summary');
    element.addEventListener('toggle', () => {
      if (element.open) {
        summaryElement.textContent = 'See Less';
      } else {
        summaryElement.textContent = 'See More';
      }
    });
  });
});

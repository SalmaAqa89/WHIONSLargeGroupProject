document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('details').forEach((element) => {
    const summaryElement = element.querySelector('summary');
    element.addEventListener('toggle', () => {
      if (element.open) {
        summaryElement.textContent = 'Hide Text';
      } else {
        summaryElement.textContent = 'Show Text';
      }
    });
  });
});

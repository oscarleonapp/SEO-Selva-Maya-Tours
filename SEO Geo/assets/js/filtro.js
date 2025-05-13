
  document.getElementById('categoryFilter').addEventListener('change', function() {
    var selectedCategory = this.value;
    var items = document.querySelectorAll('.portfolio-item');

    items.forEach(function(item) {
      if (selectedCategory === 'All categories' || item.getAttribute('data-category') === selectedCategory) {
        item.style.visibility = 'visible';
        item.style.position = 'relative';
      } else {
        item.style.visibility = 'hidden';
        item.style.position = 'absolute';
      }
    });
  });

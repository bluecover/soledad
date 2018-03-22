$('body')
  .on('click', '.friendly-link', function () {
    $('.friendly-link-detail').fadeIn('fast')
  })
  .on('click', function (e) {
    if (!$(e.target).hasClass('friendly-link')) {
      $('.friendly-link-detail').fadeOut('fast')
    }
  })

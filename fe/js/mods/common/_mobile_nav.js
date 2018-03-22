$('body')
  .on('click', '.mobile-header-title', function () {
    $(this).toggleClass('unfolded')
    $('.mobile-header-nav').slideToggle('fast')
  })
  .on('click', '.js-mobile-parent-nav', function () {
    var par = $(this).parent()
    var ul = par.find('ul')
    ul.slideToggle('fast', function () {
      par.toggleClass('unfolded')
    })
  })
  .on('click', '.js-m-global-nav', function (e) {
    var btn = $(this)
    if (btn.hasClass('close')) {
      btn.removeClass('close')
      $('.mobile-nav').slideUp('fast')
    } else {
      btn.addClass('close')
      $('.mobile-nav').slideDown('fast')
    }
  })

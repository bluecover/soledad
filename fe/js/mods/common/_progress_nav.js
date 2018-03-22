var nav_on = $('.progress-nav .on')
if (nav_on.length) {
  var width = nav_on.outerWidth()
  var margin_left = parseInt(nav_on.css('margin-left'), 10)
  var offset = nav_on.position().left + margin_left + (width / 2) - 4
  $('.progress-dot').css('width', offset).find('i').css('left', offset).end().show()
}

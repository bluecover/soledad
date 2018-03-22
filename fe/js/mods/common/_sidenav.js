var mask = require('mods/mask')()

mask.onTouch(function () {
  var w = -parseInt($('.js-sidenav').width(), 10)
  $('.js-sidenav').css('left', w - 30)
  $('.js-m-side-login').css('left', w - 30)
  mask.hide()
})

$('body').on('click', '.js-sidenav-switch', function (e) {
  e.preventDefault()
  mask.show()
  $('.js-sidenav').css('left', '0')
  $('.js-m-side-login').css('left', '0')
})

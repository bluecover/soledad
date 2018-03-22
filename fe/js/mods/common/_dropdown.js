require('mods/jquery-hover-delay.js')

$('.js-dropdown-toggle').on('click', function () {
  $(this).find('.js-dropdown').fadeToggle('fast')
})

$('.js-dropdown-toggle').hoverDelay(function () {
  $(this).find('.js-dropdown').fadeIn('fast')
}, function () {
  $(this).find('.js-dropdown').fadeOut('fast')
}, 200)

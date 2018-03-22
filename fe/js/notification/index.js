let n = 1

$('.js-btn-more').on('click', function () {
  let num = 10 * n + 10
  $('.js-notice-item:lt(' + num + ')').removeClass('hide')
  n++
  $('.js-notice-item').hasClass('hide') ? null : $('.js-btn-more').hide()
})

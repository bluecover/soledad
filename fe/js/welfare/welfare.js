let n = 1

$('.js-btn-record').on('click', function () {
  let num = 5 * n + 5
  $('.js-record:lt(' + num + ')').removeClass('hide')
  n++
  if (!($('.js-record').hasClass('hide'))) {
    $('.js-btn-record').hide()
  }
})

function tab(index) {
  $('.js-nav').eq(index).addClass('cur').siblings().removeClass('cur')
  $('.js-section').eq(index).siblings('.js-section').addClass('desktop-element')
  $('.js-section').eq(index).removeClass('desktop-element')
}

$('.js-nav').click(function () {
  let index = $(this).index()
  tab(index)
})

if (window.location.hash === '#coupon') {
  tab(1)
}

$('.js-btn-history').on('click', function () {
  $('.js-coupon-main').find('.coupon-void').toggleClass('hide')
  if ($(this).text() === '收起') {
    $(this).text('查看历史礼券')
    $('.js-coupon-tips').removeClass('hide')
  } else {
    $('.js-coupon-tips').addClass('hide')
    $(this).text('收起')
  }
})

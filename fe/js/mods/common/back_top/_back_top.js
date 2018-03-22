import throttle from 'lodash/function/throttle'

let tmpl_back_top = require('./_back_top.hbs')
let back_top_icon = '<svg class="icon" src="{svg{{img/index/backtop.svg}}}"></svg>'

$('body').append(tmpl_back_top({icon: back_top_icon}))

let $win = $(window)
let $back_top = $('.js-g-back-top')

$win.on('scroll.back resize.back', throttle(setBackTop, 100))

function setBackTop() {
  let viewport_height = $win.height()
  let scroll_distance = $win.scrollTop()

  let top_threshold = viewport_height * 0.5

  if (scroll_distance > top_threshold) {
    $back_top.fadeIn()
  } else {
    $back_top.fadeOut()
  }
}

$back_top.find('.btn-back').on('click', function (e) {
  e.preventDefault()

  setScrollTop(0)
})

function setScrollTop(top) {
  $('html, body').animate({
    scrollTop: top
  }, 600)
}

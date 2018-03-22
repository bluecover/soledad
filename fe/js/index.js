import 'fullpage.js'

const SLIDES_LENGTH = {}
const IS_SECTION_LOADED = {}
const SCREENSHOT_SCROLL_TIME = 15000

let screenshot_animation
let $back_top = $('.js-g-back-top')
let $screenshot_wrap = $('.js-website-screenshot')
let $screenshot = $screenshot_wrap.find('.screenshot')
let translate_distance = $screenshot.height() - $screenshot_wrap.height()

// 首屏返回顶部按钮特殊处理
$(window).off('resize.back')
$back_top.find('.btn-back').on('click.back', function () {
  $.fn.fullpage.moveTo('section-1')
})

$screenshot_wrap.hover(() => {
  $screenshot_wrap.stop(true, false)
}, () => {
  let remaining_time = (1 - $screenshot_wrap.scrollTop() / translate_distance) * SCREENSHOT_SCROLL_TIME

  $screenshot_wrap.animate({
    scrollTop: translate_distance
  }, {
    duration: remaining_time,
    easing: 'linear',
    complete: function () {
      $screenshot_wrap.animate({
        scrollTop: 0
      }, 500)

      $screenshot_wrap.off('mouseenter mouseleave')
    }
  })
})

function animate(sectionIndex) {
  if (IS_SECTION_LOADED[sectionIndex]) {
    return
  }

  sectionIndex = sectionIndex - 1
  let $eles = $('.section:eq(' + sectionIndex + ')').find('.wow').addClass('animated')

  $eles.map((index, item) => {
    let $item = $(item)
    let delay = $item.data('delay') || 0
    let duration = $item.data('duration') || null

    let cls = $item.data('animate')

    if (duration) {
      $item.css({animationDuration: duration})
    }

    $item.addClass(cls).css({visibility: 'visible', animationDelay: delay})
  })
}

$('#fullpage').fullpage({
  scrollingSpeed: 600,
  menu: '#section_menu',
  controlArrows: false,
  verticalCentered: false,
  loopHorizontal: false,
  fixedElements: '#section_menu, .header-wrapper',
  afterRender: () => {
    let $sections = $('#fullpage').find('.section')
    $sections.each((index, el) => {
      SLIDES_LENGTH[index + 1] = $(el).find('.slide').length
    })
  },

  afterLoad: (anchorLink, index) => {

    animate(index)

    // 首屏处理特殊动画效果
    if (index === 1) {
      $('#fullpage').addClass('set-scrolling-speed')
      $back_top.fadeOut()
    } else {
      $('#fullpage').removeClass('set-scrolling-speed')
      $back_top.fadeIn()
    }

    // 第一次加载第三屏时播放截图动画
    if (index === 3 && !IS_SECTION_LOADED[index]) {
      screenshot_animation = setTimeout(() => {

        $screenshot_wrap.animate({
          scrollTop: translate_distance
        }, {
          duration: SCREENSHOT_SCROLL_TIME,
          easing: 'linear',
          complete: function () {
            $screenshot_wrap.animate({
              scrollTop: 0
            }, 500)

            $screenshot_wrap.off('mouseenter mouseleave')
          }
        })

      }, 1200)
    }

    IS_SECTION_LOADED[index] = true
  },

  onLeave: (index, nextIndex, direction) => {
    if (index === 1) {
      $('#fullpage').addClass('section-leave-animation')
    } else {
      $('#fullpage').removeClass('section-leave-animation')
    }

    if (index === 3) {
      clearTimeout(screenshot_animation)
    }

    // 离开时清除动画相关样式，避免在 safari webkit 内核中产生元素抖动问题
    let $eles = $('.section:eq(' + (index - 1) + ')').find('.wow')

    $eles.map((index, item) => {
      let $item = $(item)

      let cls = $item.data('animate')

      $item.removeClass(cls)
        .removeClass('animated wow')
        .css({
          visibility: '',
          animationDelay: '',
          animationDuration: ''
        })
    })
  },

  onSlideLeave: function (anchorLink, index, slideIndex, direction, nextSlideIndex) {
    if (!SLIDES_LENGTH[index]) {
      return
    }

    if (nextSlideIndex === (SLIDES_LENGTH[index] - 1)) {
      $('.js-btn-next').addClass('disable')
    } else {
      $('.js-btn-next').removeClass('disable')
    }

    if (nextSlideIndex === 0) {
      $('.js-btn-prev').addClass('disable')
    } else {
      $('.js-btn-prev').removeClass('disable')
    }
  }
})

$('.js-anchor-next').on('click', function () {
  $.fn.fullpage.moveSectionDown()
})

$('.js-btn-next').on('click', function () {
  $.fn.fullpage.moveSlideRight()
})

$('.js-btn-prev').on('click', function () {
  $.fn.fullpage.moveSlideLeft()
})

$('.js-gm-select').on('click', '.option', function (e) {
  $(this).closest('.js-gm-select')
  .find('.select .btn-value')
  .removeClass('default')
  .html($(this).html())
})

// wechat share
let config = $('#wx_config').data('val')
let url = window.location.href
let desc = {
  title: '好规划理财-您身边的理财规划师',
  link: url,
  desc: '「好规划」为你提供专业易懂和可执行的理财规划及咨询服务',
  imgUrl: 'https://dn-ghimg.qbox.me/pMbD83BAX6NxfeO8'
}

wx.config(config)
wx.ready(function () {
  wx.onMenuShareAppMessage(desc)
  wx.onMenuShareTimeline(desc)
  wx.onMenuShareQQ(desc)
})

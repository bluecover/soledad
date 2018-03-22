var dlg_error = require('g-error')
var dlg_tips = require('mods/modal/modal_tips')
var dlg_success = require('mods/modal/modal_success')
var draw_chart = require('./mods/_draw_chart')
var id = $('.js-detail-wrapper').data('id')

if (window.location.href.match('follow')) {
  $.ajax({
    url: '/j/fund/like/' + id,
    type: 'get'
  }).done(function (c) {
    if (c.r) {
      $('.js-btn-unfollow').addClass('hide').siblings('.js-btn-follow').removeClass('hide')
      dlg_success.show({
        success_title: '跟踪成功',
        success_msg: '跟踪成功！您可以在基金管家首页查看每日跟踪情况'
      })
    }
  }).fail(function () {
    dlg_error.show('跟踪失败，请重试')
  })
}

$('.js-btn-unfollow').on('click', function () {
  $.ajax({
    url: '/j/fund/like/' + id,
    type: 'get'
  }).done(function (c) {
    if (c.r) {
      $('.js-btn-unfollow').addClass('hide').siblings('.js-btn-follow').removeClass('hide')
      dlg_success.show({
        success_title: '跟踪成功',
        success_msg: '跟踪成功！您可以在基金管家首页查看每日跟踪情况'
      })
    } else {
      dlg_error.show('已跟踪,请刷新页面')
    }
  }).fail(function () {
    dlg_error.show('跟踪失败，请重试')
  })
})

$('.js-nav-item').on('click', function () {
  var index = $(this).index()
  $('html, body').animate({
    scrollTop: $('.js-section').eq(index).offset().top
  })
})
$('.js-reason').on('click', function () {
  var reason = $(this).next('p').text()
  dlg_tips.show({
    tips_title: '入选理由',
    tips_main: reason
  })
})
$('.js-tip-box').on('click', function () {
  var text = '赚钱指数：组合赚取收益的能力<br />稳定指数：抵抗市场波动的能力<br />调整频率：组合配置进行调整的频率<br />长期持有：组合适合长期持有的能力<br />抗跌能力：组合抵御大幅回撤亏损的能力<br />节省费用：配置内基金的手续费率控制水平'
  dlg_tips.show({
    tips_title: '名词解释',
    tips_main: text
  })
})

$.ajax({
  url: '/j/fund/income_chart/' + id,
  type: 'get'
}).done(function (c) {
  var element = $('.js-chart-box')[0]
  draw_chart(c, element)
}).fail(function () {
  dlg_error.show('获取图表信息失败，请重试')
})

if (Number($('.js-data-num').text()) < 0) {
  $('.js-data-num').parent().addClass('text-green')
}

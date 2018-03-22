var dlg_tips = require('mods/modal/modal_tips')
var dlg_error = require('g-error')
var tmpl_product = require('./mods/_fund_product')
var draw_chart = require('./mods/_draw_chart')

tmpl_product.reload()

function convert_percent(num) {
  num = Number(Number(num * 100).toFixed(2))
  return num
}

$('.js-section-wrapper').each(function (index, ele) {
  var id = $(this).data('id')
  var element = $(this).find('.js-chart-box')[0]
  $.ajax({
    url: '/j/fund/income_chart/' + id,
    type: 'get'
  }).done(function (c) {
    $(ele).find('.js-created-date').text(c.group_created)
    $(ele).find('.js-group-income').text(convert_percent(c.group_income))
    draw_chart(c, element)
  }).fail(function () {
    dlg_error.show('获取图表信息失败，请重试')
  })
})

$('.js-btn-unfollow').on('click', function () {
  var section = $(this).parents('.js-section-wrapper')
  var id = $(section).data('id')
  var data_url = '/j/fund/like/' + id
  $.ajax({
    url: data_url,
    type: 'get'
  }).done(function (c) {
    if (c.r) {
      $(section).find('.js-btn-unfollow').addClass('hide').siblings('.js-btn-follow').removeClass('hide')
      $('.js-product-main').html('')
      tmpl_product.reload()
    } else {
      dlg_error.show('跟踪未成功，请重试')
    }
  }).fail(function () {
    dlg_error.show('请重试')
  })
})

$('.js-tip-box').on('click', function () {
  var text = '赚钱指数：组合赚取收益的能力<br />稳定指数：抵抗市场波动的能力<br />调整频率：组合配置进行调整的频率<br />长期持有：组合适合长期持有的能力<br />抗跌能力：组合抵御大幅回撤亏损的能力<br />节省费用：配置内基金的手续费率控制水平'
  dlg_tips.show({
    tips_title: '名词解释',
    tips_main: text
  })
})

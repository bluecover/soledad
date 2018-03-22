import 'slick-carousel'
import ShareWeixin from 'mods/share/_shareWeixin.jsx'
var cookie = require('cookies-js')

require('./mine/_edit_target')
require('./mods/_trading_detail')
require('./mine/_savings')
require('./mine/_animate_numbers')
var trading_detail = require('./mods/_trading_detail.js')
var appDispatcher = require('utils/dispatcher')
var Record = require('mods/record/_recordList.jsx')
let weixinDefaultConfig = {
  title: '微信扫一扫进入新春大礼包',
  desc: '打开手机微信，选择「微信」标签，点击右上角「+」，选择「扫一扫」。',
  picUrl: $('.js-banner').data('qrcode-url')
}

function loadOrders() {
  $('.js-loading').removeClass('hide')
  $('.js-reload').addClass('hide')
  $.ajax({
    url: '/j/savings/orders?limit=5',
    type: 'GET'
  }).done(function (c) {
    ReactDOM.render(<Record recordsData={c.records}/>, document.getElementById('js_record_info'))
    getUserData(c)
  }).fail(function () {
    $('.js-loading').addClass('hide')
    $('.js-reload').removeClass('hide')
  })
}

function getUserData(c) {
  if (!$('.js-loading-box').length) {
    return
  }
  $('.js-loading-box').addClass('hide')
  $('.js-total-profit').text(c.info.total_profit.toFixed(2))
  $('.js-daily-profit').text(c.info.daily_profit)
  $('.js-invest-amount').text(c.info.on_account_invest_amount)
  $('.js-plan-amount').text(c.info.plan_amount)

  var rate = c.info.fin_ratio
  var bottle_height = parseInt($('.js-bottle').css('height'), 10)
  var highly = bottle_height * rate
  if (highly >= bottle_height) {
    highly = bottle_height
  }
  $('.js-water').css('height', highly + 'px').addClass('cur')
  $('.js-line').css('bottom', highly + 'px').addClass('cur')
  if (rate > 1) {
    $('.js-plan-num').animateNumbers(100, false, 1000, 'linear')
    $('.js-bottle').addClass('over')
    $('.js-over-text').removeClass('hide')
  } else {
    $('.js-plan-num').animateNumbers((rate * 100).toFixed(0), false, 1000, 'linear')
  }
}

loadOrders()

if (!cookie.get('alert_wrapper')) {
  $('.js-alert-wrapper').removeClass('hide')
}

$('body')
  .on('click', '.js-banner', function () {
    let shareQr = ReactDOM.render(<ShareWeixin data={weixinDefaultConfig} />, document.getElementById('share_wrapper'))
    shareQr.handleClick()
  })
  .on('click', '.js-alert-close', function () {
    $(this).parent().slideUp()
    cookie.set('alert_wrapper', true, {
      'expires': 60 * 60 * 24 * 30
    })
  })
  .on('click', '.js-reload-order', function () {
    loadOrders()
  })
  .on('click', '.js-tips-close', function () { // 售罄close
    $(this).parents('.js-tips').slideUp('fast')
  })
  .on('click', '.js-sold-out-close', function () {
    let now = new Date()
    let tomorrow = new Date()
    tomorrow.setDate(now.getDate() + 1)
    tomorrow.setHours(0)
    tomorrow.setMinutes(0)
    let duration = parseInt((tomorrow.getTime() - now.getTime()) / 1000, 10)
    cookie.set('savings-sold-out', true, {
      'expires': duration
    })
  })

$('.js-carousel').slick({
  fade: true,
  autoplay: true,
  autoplaySpeed: 4000
})

appDispatcher.register(function (payload) {
  switch (payload.actionType) {
    case 'reocrd:modalDetail':
      trading_detail.show(payload.record_detail)
      break
  }
})

if (!cookie.get('profit_down_tip')) {
  $('#js_down_profit').onemodal({
    clickClose: false,
    escapeClose: false
  }).on('onemodal:close', function () {
    cookie.set('profit_down_tip', true, {
      'expires': 60 * 60 * 24 * 30
    })
  })
}

let is_sell_time = $('#sell_time').val()
is_sell_time ? $('.js-stamp').removeClass('hide') : null
// 售罄tip
if (!$('.btn-start').length && !cookie.get('savings-sold-out') && is_sell_time) {
  $('.js-tips').hide().removeClass('hide').slideDown('fast')
}

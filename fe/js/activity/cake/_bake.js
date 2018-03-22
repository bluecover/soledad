let RegPhone = require('lib/re').phone
let dlgError = require('g-error')
let setWX = require('./_wx.js')
import Animate from 'utils/animate'

let startTime
let count
let cakeCount
let closest = 0

let $oven = $('.js-oven')
let $btnTiming = $('.js-meta-game')
let $btnGoCoupon = $('.js-btn-coupon')

$btnGoCoupon.on('click', function () {
  showCoupon()
})

$('.js-phone').on('click', () => {
  if ($('.js-phone').attr('disabled')) {
    return
  }
  $('.js-phone').attr('disabled', true)
  var phone = $('.js-input-phone').val().trim()
  if (!phone || !RegPhone.test(phone)) {
    dlgError.show('请输入正确的手机号')
  } else {
    $.ajax({
      url: '/j/promotion/christmas/2015',
      type: 'POST',
      data: {
        mobile_phone: phone,
        rank: cakeCount
      }
    }).done(() => {
      $('.js-phone').attr('disabled', false)
      finishPhone()
    }).fail(res => {
      $('.js-phone').attr('disabled', false)
      dlgError.show(res && res.responseJSON && res.responseJSON.error || undefined)
    })
  }
})

const level = {
  rawest: { text: '也太快了，发生了什么？(＃°Д°) ', img: '{{{img/activity/cake/cake_rawest.png}}}' },
  rawer: { text: '不行啊，还生着呢  (＞﹏＜)', img: '{{{img/activity/cake/cake_rawer.png}}}' },
  raw: { text: '遗憾啊！只差一点点啦，加油！＞︿＜', img: '{{{img/activity/cake/cake_raw.png}}}' },
  perfect: { text: '完美！ ╮(￣▽￣)╭', img: '{{{img/activity/cake/cake_perfect.png}}}' },
  mess: { text: '怎么出来个煤球啊？(>_<、)', img: '{{{img/activity/cake/cake_mess.png}}}' },
  devil: { text: '你召唤出了黑暗料理王！╯０╰', img: '{{{img/activity/cake/cake_devil.png}}}' },
  melt: { text: '盘子都烤化了！（/TДT)/', img: '{{{img/activity/cake/cake_melt.png}}}' },
  angry: { text: '太久啦！(°□°；) ', img: '{{{img/activity/cake/cake_angry.png}}}' }
}

const award = [
  { level: '挑战失败', text: '别灰心，再试一次吧', img: '{{{img/activity/cake/award4.png}}}' },
  { level: '获得三等奖', text: '一个也不容易呢，不信啊，让朋友试试能烤几个！', img: '{{{img/activity/cake/award3.png}}}' },
  { level: '获得二等奖', text: '哎呦不错哦，蛋糕这么甜，心灵一定很美吧', img: '{{{img/activity/cake/award2.png}}}' },
  { level: '获得一等奖', text: '烘培届的施瓦辛格，受在下一拜！发朋友圈得瑟一下', img: '{{{img/activity/cake/award1.png}}}' }
]

function calc(duration) {
  let result
  let diff = duration - 3.00
  let absDiff = Math.abs(diff)
  let oldAbs = Math.abs(closest - 3.00)
  if (absDiff < oldAbs) {
    closest = duration
  }

  if (absDiff <= 0.1) {
    result = level.perfect
    cakeCount++
    try {
      setWX('我花' + closest + '秒烤出美味上天的蛋糕，邀你热乎来战')
    } catch (e) {}
  } else if (diff < -2.0) {
    result = level.rawest
  } else if (diff < -1.0) {
    result = level.rawer
  } else if (diff < 0) {
    result = level.raw
  } else if (diff > 0.4) {
    result = level.angry
  } else if (diff > 0.3) {
    result = level.melt
  } else if (diff > 0.2) {
    result = level.devil
  } else if (diff > 0.1) {
    result = level.mess
  }

  $('.js-row-time td').eq(count).text(duration + ' 秒')
  $('.js-row-img td').eq(count).find('div').html('<img src="' + result.img + '" alt="">')
  $('.js-result-tip').text(result.text)

  count++
}

function updateAward(count) {
  let awd = award[count]
  $('.text-award').text(awd.level)
  $('.text-award-tip').text(awd.text)
  $('.pig-award').attr('src', awd.img)
}

function updateRes() {
  if (count === 3) {
    $('body')
      .off('touchstart.bake')
      .off('touchend.bake')

    setTimeout(function () {
      showResult(cakeCount)
    }, 800)
    return
  }
}

function showResult() {
  Animate.out($oven)
  updateAward(cakeCount)
  $btnTiming.fadeOut('fast')
  $('.game-board').fadeOut('fast', function () {
    cakeCount > 0 ? $btnGoCoupon.removeClass('hide') : $btnGoCoupon.addClass('hide')
    $('.award-board').hide().removeClass('hide').fadeIn('fast')
    $('.js-meta-result, .js-share').hide().removeClass('hide').fadeIn('fast')
  })
}

function finishPhone() {
  $('.js-meta-phone').hide()
  $('.js-meta-coupon').removeClass('hide').show()
  $('.text-coupon').removeClass('hide')
  $('.js-text-coupon-tip').addClass('hide')
}

function start(e) {
  e.preventDefault()
  Animate.cancel($oven)
  $oven.addClass('shaking')
  $('.js-line').removeClass('hide')
  $('.js-btn-timing').css({ 'margin-top': '4px' })
  $('.js-result-tip').text('')
  startTime = new Date()
}

function stop() {
  let duration = (new Date()) - startTime
  $oven.removeClass('shaking')
  $('.js-line').addClass('hide')
  $('.js-btn-timing').css({ 'margin-top': '0' })
  duration = parseFloat(duration / 1000).toFixed(2)
  calc(duration)
  updateRes()
}

function showCoupon() {
  $('.cake' + cakeCount).removeClass('hide')
  $('.game-board, .award-board,.js-meta-result, .js-meta-coupon, .js-meta-game').fadeOut('fast', function () {
    $('.coupon-board, .js-meta-phone').hide().removeClass('hide').fadeIn('fast')
  })
}

function init() {
  startTime = null
  count = 0
  cakeCount = 0

  $('.js-row-time td').empty()
  $('.js-row-img td div').empty()
  $('.js-result-tip').text('按住3.00秒烤香甜蛋糕')
  $('.cake1, .cake2, .cake3').addClass('hide')
  $('.js-text-coupon').addClass('hide')
  $('.js-text-coupon-tip').removeClass('hide')
  Animate.run($oven)
  $('body')
    .on('touchstart.bake', '.js-btn-timing', start)
    .on('touchend.bake', '.js-btn-timing', stop)
}

function restart() {
  Animate.cancel($oven)
  init()
  $('.award-board, .coupon-board, .js-meta-result, .js-meta-phone, .js-meta-coupon, .js-share').fadeOut('fast', function () {
    $('.game-board, .js-meta-game').hide().removeClass('hide').fadeIn('fast')
  })
}

let Bake = {
  init: init,
  start: start,
  restart: restart,
  stop: stop
}

export default Bake

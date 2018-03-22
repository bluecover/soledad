import lottery_prize from './lottery/_lottery_prize'
import dlg_tips from 'mods/modal/modal_tips'

let config = $('#wx_config').data('val')
let url = window.location.href
let desc = {
  title: '和我一起攒钱吧！还可以拿红包，赢Kindle！',
  desc: '我一直在用好规划，安全赚收益，你也来试试吧！',
  link: url,
  imgUrl: 'http://7xk4uw.com2.z0.glb.qiniucdn.com/lottery.png'
}
wx.config(config)
wx.ready(function () {
  wx.onMenuShareAppMessage(desc)
  wx.onMenuShareTimeline(desc)
  wx.onMenuShareQQ(desc)
})

let remain_times = Number($('.js-lottery-times').text())
let prize_type = 0
const first_level = '恭喜您抽得大奖kindlepaperwhite一台！<br /><br />我们的客服将于48小时内联系您并寄出奖品，请注意接听电话。<br /><br />我们不会向您收取包含运费在内的任何额外的费用，注意防骗，保护好自己的财产安全。'

const prize_data = [
  { text: '未中奖', location: [1, 4, 8, 10, 12, 17, 19, 21] },
  { text: 'kindle', location: [2] },
  { text: '+2元', location: [16] },
  { text: '+1.8元', location: [3, 14] },
  { text: '+1元', location: [5, 7, 13, 20] },
  { text: '+0.8元', location: [0, 6, 9, 11, 15, 18] }
]

let lottery = {
  init: function (ele) {
    this.index = -1 // 当前转动到哪个位置，起点位置
    this.count = 0 // 总共有多少个位置
    this.timer = 0 // setTimeout的ID，用clearTimeout清除
    this.roll_times = 0 // 转动次数
    this.cycle = 80 // 转动基本次数：即至少需要转动多少次再进入抽奖环节
    this.prize = -1 // 中奖位置
    this.running = false // 是否转动过程中
    this.speed = 20 // 初始转动速度
    this.speed_down = 10 // 即将结束的减速度
    this.ele = $(ele)

    $(ele).removeClass('mask')
    let $items = $(ele).find('.lottery-item')

    if ($items.length) {
      this.count = $items.length
      $(ele).find('.js-lottery-item-' + this.index).addClass('active')
    }
  },

  roll: function () {
    this.running = true
    this.roll_times += 1

    let index = this.index
    let $lottery = this.ele
    let is_speed_down = this.roll_times > this.cycle + 11

    $lottery.addClass('mask')
    $lottery.find('.js-lottery-item-' + index).removeClass('active')
    index += 1
    if (index > this.count - 1) {
      index = 0
    }
    $lottery.find('.js-lottery-item-' + index).addClass('active')
    this.index = index

    if (is_speed_down && this.prize === this.index) {
      this.stop()
      return
    }

    if (this.roll_times < this.cycle) {
      this.speed = 20
    } else if (this.roll_times === this.cycle) {
      let prize_arr = prize_data[prize_type].location
      let prize_index = Math.floor(Math.random() * prize_arr.length)
      this.prize = prize_arr[prize_index]
    } else {
      let is_last_step = (this.prize === 0 && this.index === 21) || this.prize === this.index + 1
      this.speed += is_speed_down && is_last_step ? 110 : this.speed_down
    }

    this.timer = setTimeout(this.roll.bind(this), this.speed)
  },

  stop: function () {
    let prize = this.prize
    showPirze(this.ele, this.prize)

    setTimeout(() => {
      lottery_prize.close()
      if (prize === 2) {
        dlg_tips.show({
          tips_title: '恭喜你',
          tips_main: first_level
        })
      }
      this.init(this.ele)
      this.index = prize
      lotteryComplete()
    }, 2000)
  }
}

lottery.init('#lottery')

$('.js-btn-start').on('click', () => {
  if (remain_times === 0) {
    dlg_tips.show({
      tips_title: '提示',
      tips_main: '你的抽奖次数已用完,邀请好友获得更多抽奖机会'
    })
    return
  }
  if (lottery.running) {
    return
  }
  getRequest()
  lottery.roll()
})
function lotteryComplete() {
  $.ajax({
    url: '/j/activity/get_gift',
    type: 'GET'
  }).fail(function () {
    lotteryComplete()
  })
}

function showPirze(ele, prize) {
  let prize_img_src = $('.js-lottery-item-' + prize).find('img').attr('src')
  let prize_text

  for (let i in prize_data) {
    if (prize_data[i].location.indexOf(prize) !== -1) {
      prize_text = prize_data[i].text
    }
  }
  lottery_prize.show({
    parent_ele: ele,
    prize_img_src,
    prize_text
  })
}

function getRequest() {
  $.ajax({
    url: '/j/activity/do_lottery',
    type: 'GET'
  }).done(function (e) {
    if (e) {
      prize_type = e.gift_id
      remain_times = e.remain_num
      $('.js-lottery-times').text(remain_times)
    } else {
      dlg_tips.show({
        tips_title: '出错了',
        tips_main: '网络繁忙,请刷新页面再试'
      })
    }
  }).fail(function () {
    dlg_tips.show({
      tips_title: '出错了',
      tips_main: '网络繁忙,请刷新页面再试'
    })
  })
}

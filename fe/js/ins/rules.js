let config = $('#wx_config').data('val')
let url = window.location.href
let desc = {
  title: '保险精选年终福利来啦，力度空前仅限本月！',
  desc: '投保就返攒钱助手礼券，最高220元，收益猛增2%起！',
  link: url,
  imgUrl: 'http://7xkkgg.dl1.z0.glb.clouddn.com/accident.png'
}
wx.config(config)
wx.ready(function () {
  wx.onMenuShareAppMessage(desc)
  wx.onMenuShareTimeline(desc)
  wx.onMenuShareQQ(desc)
})

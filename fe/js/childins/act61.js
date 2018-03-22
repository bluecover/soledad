var wechat = require('mods/modal/modal_wx')

$('.js-btn-wechat').on('click', wechat.show)

$('.js-input-url').on('mouseover', function () {
  this.select()
}).on('change', function () {
  var $this = $(this)
  $this.val($this.data('url'))
})

var config = $('#wx_config').data('val')
var url = $('.js-input-url').data('url')

var desc = {
  title: '儿童保险规划：专业理财师帮你选保险 - 好规划',
  desc: '我已经做了免费儿童保险规划，靠谱省心，邀请更多妈妈来试试！',
  link: url,
  imgUrl: 'https://dn-ghimg.qbox.me/FmHA6Z8iZmijixDRL7UYH1OnuaVn'
}

wx.config(config)
wx.ready(function () {
  wx.onMenuShareAppMessage(desc)
  wx.onMenuShareTimeline(desc)
  wx.onMenuShareQQ(desc)
})

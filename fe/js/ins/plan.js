new WOW().init()

let $window = $(window)

let win_height = $window.height()

$('.js-anchor-next').on('click', () => {
  setScrollTop(win_height)
})

function setScrollTop(top) {
  $('html, body').animate({
    scrollTop: top
  }, 600)
}

// wechat share
var config = $('#wx_config').data('val')
var url = window.location.href
var desc = {
  link: url,
  desc: '只需10分钟，量身定制专业保险规划',
  imgUrl: 'https://dn-ghimg.qbox.me/LwRqg9xc86vpwqW7'
}

wx.config(config)
wx.ready(function () {
  wx.onMenuShareAppMessage(desc)
  wx.onMenuShareTimeline(desc)
  wx.onMenuShareQQ(desc)
})

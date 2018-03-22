import dlg_tip from 'mods/modal/modal_tips'

$('.js-ins-guidebook').on('click', (e) => {
  e.preventDefault()

  dlg_tip.show({
    tips_main: '即将发布，敬请期待！'
  })
})

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

let ShareList = require('mods/share/_shareList.jsx')

let qrcodeUrl = $('.js-share-mod').find('.btn-weixin').data('image-url')

let invite_link = $('.js-invite-link').text()
let shareConfig = {
  general: {
    title: '送你115元大礼包，和我一起使用攒钱助手吧！',
    summary: '我一直在用攒钱助手，本息保障收益靠谱。你也来吧！现在注册还送115元新人礼包',
    pic: 'https://mmbiz.qlogo.cn/mmbiz/dOjJX8Y7SMic7KTw6cibqFhqNALSWTDhBLQKa0yiaibMMb6kqf6eurUjsTlaRCBSWlicOj096ephUveELlHibTyc42OQ/0?wx_fmt=png',
    ralateUid: '3355515910',
    url: invite_link
  },

  weixin: {
    picUrl: qrcodeUrl
  }
}

var share_wrapper = $('.js-share-mod').find('.bd')[0]
if (share_wrapper) {
  ReactDOM.render(<ShareList shareConfig={shareConfig} />, share_wrapper)
}

let config = $('#wx_config').data('val')
let desc = {
  title: '送你115元大礼包，和我一起使用攒钱助手吧！',
  desc: '我一直在用攒钱助手，本息保障收益靠谱。你也来吧!',
  link: invite_link,
  imgUrl: 'https://mmbiz.qlogo.cn/mmbiz/dOjJX8Y7SMic7KTw6cibqFhqNALSWTDhBLQKa0yiaibMMb6kqf6eurUjsTlaRCBSWlicOj096ephUveELlHibTyc42OQ/0?wx_fmt=png'
}

wx.config(config)
wx.ready(function () {
  wx.onMenuShareAppMessage(desc)
  wx.onMenuShareTimeline(desc)
  wx.onMenuShareQQ(desc)
})

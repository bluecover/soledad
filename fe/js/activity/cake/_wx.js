let config = $('#wx_config').data('val')
let url = $('#share_url').val()
let desc = {
  title: '手指都按断了，也没烤出来一个蛋糕，你要来挑战下嘛？',
  link: url,
  imgUrl: 'https://dn-ghimg.qbox.me/wx_cake.png'
}

wx.config(config)

function setWX(title) {
  title ? desc.title = title : null
  wx.ready(function () {
    wx.onMenuShareAppMessage(desc)
    wx.onMenuShareTimeline(desc)
    wx.onMenuShareQQ(desc)
  })
}

export default setWX

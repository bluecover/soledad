var config = $('#ins_data').data('val')
var title = $('#ins_data').data('title')
var data_desc = $('#ins_data').data('desc')
var url = window.location.href
var desc = {
  title: title,
  desc: data_desc,
  link: url,
  imgUrl: 'http://7xkkgg.dl1.z0.glb.clouddn.com/accident.png'
}
wx.config(config)
wx.ready(function () {
  wx.onMenuShareAppMessage(desc)
  wx.onMenuShareTimeline(desc)
  wx.onMenuShareQQ(desc)
})

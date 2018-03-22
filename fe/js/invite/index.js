import PhoneForm from 'mods/_phone_form.jsx'

ReactDOM.render(<PhoneForm actionUrl="/invite/register"/>, document.getElementById('phone_form'))
let config = $('#wx_config').data('val')
let url = window.location.href
let desc = {
  title: '送你115元大礼包，和我一起使用攒钱助手吧！',
  desc: '我一直在用攒钱助手，本息保障收益靠谱。你也来吧!',
  link: url,
  imgUrl: 'https://mmbiz.qlogo.cn/mmbiz/dOjJX8Y7SMic7KTw6cibqFhqNALSWTDhBLQKa0yiaibMMb6kqf6eurUjsTlaRCBSWlicOj096ephUveELlHibTyc42OQ/0?wx_fmt=png'
}
wx.config(config)
wx.ready(function () {
  wx.onMenuShareAppMessage(desc)
  wx.onMenuShareTimeline(desc)
  wx.onMenuShareQQ(desc)
})

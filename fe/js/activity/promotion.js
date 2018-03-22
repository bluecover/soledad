import PhoneForm from 'mods/phone/_phone_submit.jsx'
import tmpl from './promotion/mods/tmpl_redeem_dlg.hbs'

let download_url = $('#download_url').val()
let phoneForm = document.getElementById('phone_form')
let tips_main = tmpl({ download_url: download_url })
let url = window.location.href + '?dcs=&dcm=sangongzimenu&ch=sangongzi'
let config = $('#wx_config').data('val')

let desc = {
  title: '好规划@三公子专属福利',
  desc: '送你115元新人代金券和0.4%加息券，一起来攒钱吧!',
  link: url,
  imgUrl: `https://mmbiz.qlogo.cn/mmbiz/dOjJX8Y7SMic7KTw6cibqFhqNAL
  SWTDhBLQKa0yiaibMMb6kqf6eurUjsTlaRCBSWlicOj096ephUveELlHibTyc42OQ/0?wx_fmt=png`
}

wx.config(config)
wx.ready(function () {
  wx.onMenuShareAppMessage(desc)
  wx.onMenuShareTimeline(desc)
  wx.onMenuShareQQ(desc)
})

const phoneData = {
  submit_url: '/activity/promotion/is_new_user',
  new_user: {
    tips_title: '专属兑换码为：',
    tips_main: tips_main
  },
  old_user: {
    tips_title: '温馨提示',
    tips_main: '您已是好规划注册用户，本次活动仅针对新用户。'
  }
}

ReactDOM.render(<PhoneForm phoneData={phoneData} />, phoneForm)

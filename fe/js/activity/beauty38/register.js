import RegForm from 'mods/account/_regForm.jsx'
import dlg_tips from 'mods/modal/modal_tips'

let $accountWrap = $('.js-accounts-form')
let redirect_url = $accountWrap.data('url')
let account = ReactDOM.render(<RegForm type="register"/>, $accountWrap[0])
let default_phone = $('.js-accounts-form').data('phone')
let tips_main = '领取成功,完成注册后即可使用礼包'
dlg_tips.show({
  tips_title: '领取成功',
  tips_main: tips_main
})

$('#reg-username').val(default_phone).attr('disabled', 'disabled').css('color', '#999')

account.setSubmitInfo({
  redirect_url: redirect_url
})

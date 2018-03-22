import RegForm from 'mods/account/_regForm.jsx'

let $accountWrap = $('.js-accounts-form')
let redirect_url = $accountWrap.data('url')
let account = ReactDOM.render(<RegForm type="register"/>, $accountWrap[0])
let default_phone = $('.js-accounts-form').data('phone')

$('#reg-username').val(default_phone).attr('disabled', 'disabled').css('color', '#999')

account.setSubmitInfo({
  redirect_url: redirect_url
})

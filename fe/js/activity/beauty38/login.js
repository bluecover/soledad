import LoginForm from 'mods/account/_loginForm.jsx'

let $accountWrap = $('.js-accounts-form')
let redirect_url = $accountWrap.data('url')
let account = ReactDOM.render(<LoginForm type="login"/>, $accountWrap[0])
let default_phone = $('.js-accounts-form').data('phone')

$('#login-username').val(default_phone).attr('disabled', 'disabled').css('color', '#999')
$('.btn-register').addClass('hide')

account.setSubmitInfo({
  redirect_url: redirect_url
})

import appDispatcher from 'utils/dispatcher'
import Account from 'mods/account/_account.jsx'

let $accountWrap = $('.accounts-content-form')
let accountType = $accountWrap.data('account-type')
let redirectUrl = $accountWrap.data('url')
let stats = {
  dcm: $accountWrap.data('dcm'),
  dcs: $accountWrap.data('dcs')
}

let account = ReactDOM.render(<Account type={accountType}/>, $accountWrap[0])

account.setSubmitInfo({
  redirect_url: redirectUrl,
  stats
})

let $loginAside = $('.login-aside')
let $regAside = $('.register-aside')
let $accountTitle = $('.accounts-title')

if (accountType === 'login') {
  $loginAside.show()
  $accountTitle.html('登录好规划')
} else {
  $regAside.show()
  $accountTitle.html('注册好规划')
}

$('.js-to-register').click(() => {
  $loginAside.hide()
  $regAside.show()
  $accountTitle.html('注册好规划')

  appDispatcher.dispatch({
    actionType: 'account:toRegister'
  })
})

$('.js-to-login').click(() => {
  $regAside.hide()
  $loginAside.show()
  $accountTitle.html('登录好规划')

  appDispatcher.dispatch({
    actionType: 'account:toLogin'
  })
})

appDispatcher.register((payload) => {
  switch (payload.actionType) {
    case 'account:toLogin':
      account.switchAccount('login')
      break
    case 'account:toRegister':
      account.switchAccount('register')
      break
  }
})

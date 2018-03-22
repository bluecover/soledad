import dlgError from 'g-error'
import Account from './_account.jsx'

// 如果是触摸设备，则跳转至登录注册页
let supportsTouch = 'ontouchstart' in window || window.navigator.msMaxTouchPoints

const entrance_text_map = new Map([['home', ''], ['savings', '攒钱助手'], ['wallet', '零钱包'], ['ins', '保险精选']])

let $accountWrap = $('.js-g-account')
let account
let accountWrap
let entrance = $('meta[name="x-endpoint"]').attr('content')
let account_entrance_text = entrance_text_map.get(entrance)

if ($accountWrap.length && !supportsTouch) {
  accountWrap = $accountWrap[0]
  account = ReactDOM.render(<Account page={account_entrance_text}/>, accountWrap)

  $(document).on('click', '.js-g-login', function (e) {
    e.preventDefault()

    let url = getRedirectUrl($(e.target))
    let stats = getStatsInfo($(e.target))

    account.setSubmitInfo({
      redirect_url: url,
      stats
    })

    account.switchAccount('login')
    $accountWrap.onemodal()
  })

  $(document).on('click', '.js-g-register', function (e) {
    e.preventDefault()

    let url = getRedirectUrl($(e.target))
    let stats = getStatsInfo($(e.target))

    account.setSubmitInfo({
      redirect_url: url,
      stats
    })

    account.switchAccount('register')
    $accountWrap.onemodal()
  })

}

function getStatsInfo($ele) {
  return {
    dcm: $ele.data('dcm'),
    dcs: $ele.data('dcs')
  }
}

function getRedirectUrl($ele) {
  if ($ele.data('url')) {
    return $ele.data('url')
  } else {
    return null
  }
}

// 处理退出，成功退出刷新当前页
let $logout = $('.js-g-logout')

$logout.on('click', function (e) {
  e.preventDefault()

  $.ajax({
    url: '/j/account/logout',
    type: 'POST'
  }).done(()=> {
    window.location.reload()
  }).fail(()=> {
    dlgError.show()
  })

})

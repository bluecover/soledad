var Cookies = require('cookies-js')
let $app_float = $('.js-g-app-float')
let $btn_close = $app_float.find('.js-g-btn-close')

if (!Cookies.get('ad_app_download_float')) {
  $app_float.show()
}

$btn_close.click(function (e) {
  $app_float.hide()
  Cookies.set('ad_app_download_float', 'true', {expires: 7 * 24 * 3600})
})

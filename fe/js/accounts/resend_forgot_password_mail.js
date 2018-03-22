var resend_countdown = require('utils/resend_countdown')
var dlg_error = require('g-error')

var resend_forgot = $('.js-btn-resend-forgot')
var btn_disable = $('.js-resend-forgot-countdown')
var ele_num = $('.js-countdown-num')
var resend_email = $('.js-resend-email')

resend_forgot.click(function () {
  var params = {
    alias: resend_email.text()
  }

  $.ajax({
    url: '/j/account/forgot_password',
    type: 'POST',
    data: params,
    dataType: 'json'
  }).done(function (c) {
    if (c.r) {
      resend_countdown(resend_forgot, btn_disable, ele_num, 60)
    } else {
      dlg_error.show()
    }
  }).fail(function () {
    dlg_error.show()
  })
})

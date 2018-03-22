var re = require('lib/re')

var prompt = $('.email-prompt')
var form_error = $('.form-error')
var send_btn = $('.send-btn')
var sending_btn = $('.sending-btn')
var email_form = $('.email-form')

$('.pmail-txt')
  .blur(function () {
    if ($(this).val() === '') {
      prompt.show()
      form_error.html('')
    } else if (!re.email.test($(this).val()) && !re.phone.test($(this).val())) {
      prompt.html('请填写正确的邮箱或手机号')
      form_error.html('')
      prompt.show()
    } else {
      prompt.hide()
    }
  })
  .keydown(function (event) {
    if (event.keyCode === 13) {
      send_btn.click()
    }
  })

send_btn.click(function () {
  $('.pmail-txt').blur()
  if (prompt.css('display') === 'none') {
    sending_btn.css('display', 'inline-block')
    send_btn.hide()
    email_form.submit()
  }
})

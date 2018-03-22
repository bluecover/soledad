var phone_tmpl = require('mods/phone/tmpl_phone_verify.hbs')()
var dlg_error = require('g-error')
var countdown = require('utils/countdown')
var re_phone = require('lib/re').phone

module.exports = function (parent) {
  var $parent = $(parent)
  $parent.append(phone_tmpl)
  var phone_input = $parent.find('.js-phone')
  var send_con = $parent.find('.js-send-con')
  var btn_send = $parent.find('.js-btn-send')

  btn_send.on('click', function () {
    if (!phonePrompt()) {
      return
    }
    $.ajax({
      type: 'POST',
      url: '/j/account/bind_mobile',
      data: {
        mobile: phone_input.val()
      }
    }).done(function (c) {
      if (c.r) {
        send_con.removeClass('hide').show()
        btn_send.hide()
        countdown(60, function (second) {
          $('.js-resend').text(second)
        }, function () {
          send_con.hide()
          btn_send.show()
        })
      } else if (c.error) {
        dlg_error.show(c.error)
      } else {
        dlg_error.show()
      }
    }).fail(function () {
      dlg_error.show()
      send_con.hide()
      btn_send.show()
    })
  })

  function phonePrompt(func) {
    if (phone_input.val() === '') {
      return false
    }
    if (!re_phone.test(phone_input.val())) {
      return false
    }
    return true
  }
}

let tmpl = require('./_payment_detail.hbs')
let dlg_sms = require('mods/modal/sms')
let dlg_loading = require('g-loading')
let dlg_error = require('g-error')
let request_running = false

module.exports = {
  show: function (data) {
    let options = {...data}
    let $tmpl = $(tmpl(options))
    $('body').append($tmpl)

    $(tmpl).find('.js-btn-confirm').one('click', function () {
      dlg_loading.show()
      submitOrder(data)
    })

    $tmpl.onemodal({
      removeAfterClose: true
    })
    return $tmpl
  }
}

function submitOrder(data) {
  $.ajax({
    type: 'post',
    url: '/j/savings/' + data.partner + '/subscribe',
    data: data
  }).done(function (res) {
    if (res.r) {
      dlg_sms.show('请输入收到的手机验证码').on('sms:submit', function (e, val) {
        if (request_running) {
          return
        }
        checkSmsCode(val, res.payment_url)
        dlg_loading.show()
      })
    } else {
      dlg_error.show(res.error)
    }
  }).fail(function () {
    dlg_error.show()
  })
}

function checkSmsCode(val, url) {
  var smscode_data = {
    sms_code: val
  }
  request_running = true

  $.ajax({
    type: 'post',
    url: url,
    data: smscode_data
  }).done(function (c) {
    if (c.r) {
      window.location.href = c.redirect_url
    } else {
      dlg_error.show(c.error)
    }
  }).fail(function (r) {
    dlg_error.show(r && r.responseJSON && r.responseJSON.error)
  }).always(function () {
    request_running = false
  })
}

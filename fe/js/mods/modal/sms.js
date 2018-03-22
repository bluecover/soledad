var tmpl = require('./sms_tmpl.hbs')

module.exports = {
  show: function (title) {
    var $tmpl = $(tmpl({
      title: title || '请输入验证码'
    }))
    $('body').append($tmpl)

    $tmpl.onemodal({
      clickClose: false,
      escapeClose: false,
      removeAfterClose: true
    })

    $tmpl.find('.js-btn-code').on('click', function () {
      var $error = $tmpl.find('.js-error')
      var val = $tmpl.find('.js-code').val()
      val = val.trim()
      $error.text('')
      if (!val) {
        $error.text('请输入验证码')
        return
      }

      let number_reg = /^\d+$/
      if (!number_reg.test(val)) {
        $error.text('验证码只能是数字')
        return
      }

      $tmpl.trigger('sms:submit', [val])
    })

    return $tmpl
  }
}

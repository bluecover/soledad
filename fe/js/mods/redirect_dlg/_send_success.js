let tmpl = require('./_send_success.hbs')

module.exports = {
  show: function (options) {
    let default_opt = {
      user_email: '',
      ins_title: ''
    }
    options = $.extend({}, default_opt, options)
    let $tmpl = $(tmpl(options))
    $('body').append($tmpl)

    $tmpl.find('.js-resend').click(() => {
      let user_email = $tmpl.find('.js-email-str').text()
      $.ajax({
        url: $('#ins_data').data('url'),
        type: 'POST',
        dataType: 'json',
        data: {
          user_email: user_email,
          ins_title: options.ins_title
        }
      }).done(() => {
        this.show({ user_email: user_email })
      })
    })

    $tmpl.onemodal({
      escapeClose: false,
      removeAfterClose: true
    })
    return $tmpl
  }
}

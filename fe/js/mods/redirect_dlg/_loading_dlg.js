let loading_dot = require('mods/modal/modal_loading_dot')
let tmpl = require('./_loading_dlg.hbs')
let send_success = require('./_send_success')
let r = require('lib/re').email

let ins_title = $('#ins_data').length ? $('#ins_data').data('title') : null

module.exports = {
  show: function (options) {
    let default_opt = {
      guihua_logo_src: '{{{img/logo-nake.png}}}',
      partner_logo: 'hzw-logo',
      partner_logo_src: '{{{img/logo/hzw_logo.png}}}',
      redirect_url: '#',
      ins_title: ins_title
    }

    options = $.extend({}, default_opt, options)
    let $tmpl = $(tmpl(options))
    loading_dot($tmpl.find('.js-dot-main'))
    $('body').append($tmpl)

    $tmpl.find('.js-btn-send').on('click', function () {
      let user_email = $tmpl.find('.js-user-email').val()
      if (!user_email) {
        return
      }
      if (!r.test(user_email)) {
        $tmpl.find('.js-email-error').removeClass('hide')
        return
      }

      $.ajax({
        url: $('#ins_data').data('url'),
        type: 'POST',
        dataType: 'json',
        data: {
          user_email: user_email,
          ins_title: options.ins_title
        }
      }).done(function () {
        send_success.show({
          user_email: user_email,
          ins_title: ins_title
        })
      })
    })

    $tmpl.onemodal({
      escapeClose: false,
      removeAfterClose: true
    })
    return $tmpl
  }
}

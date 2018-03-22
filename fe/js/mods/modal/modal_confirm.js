let tmpl = require('./tmpl_dlg_confirm.hbs')

let $body = $('body')

module.exports = {
  show: function (options) {
    let default_opt = {
      title: '确认对话框',
      confirm_text: '确定'
    }

    options = {
      ...default_opt,
      ...options
    }

    let $tmpl = $(tmpl(options))
    $body.append($tmpl)
    let bd_main = $tmpl.find('.onemodal-bd')
    bd_main.html(options.content)

    $tmpl.find('.js-btn-confirm').on('click', (e) => {
      options.handleConfirm && options.handleConfirm(e)
      $.onemodal.close()
    })

    $tmpl.onemodal({
      removeAfterClose: true
    })

    return $tmpl
  },

  close: function () {
    $.onemodal.close()
  }
}

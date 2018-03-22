var tmpl = require('./tmpl_dlg_success.hbs')

module.exports = {
  show: function (options) {
    var default_opt = {
      success_title: '提交成功',
      success_msg: '您的提交成功，祝贺您',
      redirect_url: ''
    }
    options = $.extend({}, default_opt, options)
    var $tmpl = $(tmpl(options))
    $('body').append($tmpl)

    $tmpl.onemodal({
      removeAfterClose: true
    })

    return $tmpl
  },

  close: function () {
    $.onemodal.close()
  }
}

var tmpl = require('./error_tmpl.hbs')

module.exports = {
  show: function (error_msg, error_title) {
    error_msg = error_msg || '您的提交出现了错误，请重试'
    error_title = error_title || '出错啦'
    var $tmpl = $(tmpl({
      error_msg: error_msg,
      error_title: error_title
    }))
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

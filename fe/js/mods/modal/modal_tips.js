var tmpl = require('./tmpl_dlg_tips.hbs')

module.exports = {
  show: function (options) {
    var default_opt = {
      tips_title: '提示',
      tips_main: ''
    }

    options = $.extend({}, default_opt, options)
    var $tmpl = $(tmpl(options))
    $('body').append($tmpl)
    var bd_main = $tmpl.find('.onemodal-bd')
    bd_main.append(options.tips_main)
    $tmpl.onemodal({
      removeAfterClose: true
    })

    return $tmpl
  },

  close: function () {
    $.onemodal.close()
  }
}

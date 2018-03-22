var tmpl = require('./loading_tmpl.hbs')

module.exports = {
  show: function (options) {
    var default_opt = {
      loading_title: '正在提交',
      loading_info: '正在提交，请稍候...',
      loading_src: '{{{img/misc/loading.gif}}}'
    }
    options = $.extend({}, default_opt, options)
    var $tmpl = $(tmpl(options))

    $('body').append($tmpl)
    $tmpl.onemodal({
      clickClose: false,
      escapeClose: false,
      removeAfterClose: true
    })

    return $tmpl
  },

  close: function () {
    $.onemodal.close()
  }
}

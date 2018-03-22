var tmpl = require('./tmpl_modal_wechat.hbs')

module.exports = {
  show: function () {
    let img_src = '{{{img/misc/arrow.png}}}'
    let $tmpl = $(tmpl({img_src: img_src}))
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

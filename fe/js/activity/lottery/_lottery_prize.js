import tmpl from './_lottery_prize.hbs'

export default {
  show: function (options) {
    let default_opt = {
      parent_ele: 'body',
      prize_img_src: '',
      prize_text: ''
    }
    options = Object.assign(default_opt, options)
    let $tmpl = $(tmpl(options))
    $(options.parent_ele).append($tmpl)
    $tmpl.find('img,p').addClass('active')
    this.ele = $tmpl
    return $tmpl
  },
  close: function () {
    this.ele.remove()
  }
}

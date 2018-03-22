var loading_tmpl = require('./tmpl_loading_dot.hbs')
var tmpl = loading_tmpl()

module.exports = function (parent) {
  var $parent = $(parent)
  $parent.html('').append(tmpl)
  var i = 0
  var dot = $parent.find('.js-dot')

  setInterval(function () {
    $(dot).eq(i).addClass('cur').siblings().removeClass('cur')
    i === $(dot).length ? i = 0 : i++
  }, 500)
}

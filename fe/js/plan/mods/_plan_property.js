var tmpl = require('./_plan_property.hbs')

module.exports = {
  show: function (str, ele) {
    var options = {
      property_str: str,
      property_ele: ele
    }
    var $tmpl = $(tmpl(options))
    $('.js-savings').before($tmpl)
    return $tmpl
  },
  remove: function (ele) {
    $('.' + ele).remove()
  }
}

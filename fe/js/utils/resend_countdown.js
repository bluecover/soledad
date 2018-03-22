var countdown = require('utils/countdown')

module.exports = function (btn, btn_disable, ele_num, num) {
  btn.hide()
  if (btn_disable.hasClass('js-inline-block')) {
    btn_disable.css('display', 'inline-block')
  }
  btn_disable.show()
  ele_num.html(num)

  countdown(num, function (seconds_left) {
    ele_num.html(seconds_left)
  }, function () {
    btn.show()
    btn_disable.hide()
  })
}

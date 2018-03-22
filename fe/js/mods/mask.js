var $ = require('jquery')

function Mask(opts) {
  var def = {
    background: 'rgba(0,0,0,0.3)',
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%'
  }
  this.div = $('<div></div>')
  this.opts = $.extend(def, opts)
  this.init()
}

Mask.prototype.init = function (opts) {
  $('body').append(this.div)
  this.div.css(this.opts).hide()
}

Mask.prototype.show = function () {
  this.div.fadeIn('fast')
}

Mask.prototype.hide = function () {
  this.div.fadeOut('fast')
}

Mask.prototype.onTouch = function (handler) {
  this.div.on('click touchstart', function () {
    handler.call(this)
  })
}

module.exports = function (opts) {
  return new Mask(opts)
}

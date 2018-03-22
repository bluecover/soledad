(function (factory) {
  if (typeof define === 'function' && define.amd) {
    define(['jquery'], factory)
  } else if (typeof exports === 'object') {
    factory(require('jquery'))
  } else {
    factory(jQuery)
  }
}(function ($) {
  if ($.hoverDelay) {
    return
  }

  $.HoverDelay = function (el, over, out, ms) {
    ms = ms || 500
    var delay

    $(el).bind('mouseenter.hoverDelay', function (e) {
      delay = setTimeout(function () {
        over.call(el, e)
      }, ms)
    }).bind('mouseleave.hoverDelay', function (e) {
      clearTimeout(delay)
      out.call(el, e)
    })
  }

  $.fn.hoverDelay = function (over, out, ms) {
    return this.each(function () {
      new $.HoverDelay(this, over, out, ms)
    })
  }
}))

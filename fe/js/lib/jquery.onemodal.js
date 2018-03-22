(function(factory) {

  if (typeof define === 'function' && define.amd) {
    define(['jquery'], factory)
  } else if(typeof exports === 'object') {
    factory(require('jquery'))
  } else {
    factory(jQuery)
  }

} (function ($) {
  if($.fn.onemodal) {
    return
  }

  var current = null
  var $body = $('body')
  var $overlay = $('<div>').css({
    top: 0, right: 0, bottom: 0, left: 0,
    width: "100%", height: "100%",
    position: "fixed",
    display: "none"
  })
  $body.append($overlay)


  var EVENTS = {
    BEFORE_OPEN: 'onemodal:before-open',
    OPEN: 'onemodal:open',
    BEFORE_CLOSE: 'onemodal:before-close',
    CLOSE: 'onemodal:close'
  }

  var defaults = {
    bg: "#000",
    opacity: 0.4,
    zIndex: 99,
    escapeClose: true,
    clickClose: true,
    removeAfterClose: false
  }

  var scrollbarWidth = (function() {
    var $scrollDiv = $('<div>').css({
      position: 'absolute',
      top: -99999,
      width: 10,
      height: 10,
      overflow: 'scroll'
    })
    $body.append($scrollDiv)
    var scrollbarWidth = $scrollDiv[0].offsetWidth - $scrollDiv[0].clientWidth
    $scrollDiv.remove()
    return scrollbarWidth
  })()

  function showMask(options) {
    $overlay.css({
      zIndex: options.zIndex,
      background: options.bg,
      opacity: options.opacity
    }).fadeIn(100)
  }

  function hideMask() {
    $overlay.fadeOut(100)
  }

  function isBodyOverflow() {
    return $body.outerHeight() - $(window).height() > 0
  }

  $.onemodal = function(ele, options) {
    this.options = $.extend({}, defaults, options)

    this.$wrapper = $('<div>').addClass('modal-wrapper').css({
      position: 'fixed',
      top: 0,
      bottom: 0,
      left: 0,
      right: 0,
      overflow: 'auto',
      '-webkit-overflow-scrolling': 'touch'
    })

    this.$wrapper.on('click', function() {})

    if(ele.is('a')) {
      var target = ele.attr('href')
      this.$ele = $(target)
      if (this.$ele.length !== 1) return null
    } else {
      this.$ele = ele
    }

    $body.append(this.$wrapper.append(this.$ele))
    this.open()
  }

  $.onemodal.prototype.open = function() {
    if(current) {
      if(current === this) {
        return
      }
      current.close(true)
    } else {
      showMask(this.options)
    }

    this.$ele.trigger(EVENTS.BEFORE_OPEN, [this._ctx()])

    this.$wrapper.css({
      zIndex: this.options.zIndex
    }).show()

    this.center()
    this.$ele.removeClass('onemodal-bounceOut')
    this.$ele.addClass('onemodal-bounceIn')
    this.$ele.show()

    this.bind()
    current = this
    this.$ele.trigger(EVENTS.OPEN, [this._ctx()])
  }

  $.onemodal.prototype.close = function(is_change) {
    var ele = this.$ele
    var that = this
    ele.trigger(EVENTS.BEFORE_CLOSE, [this._ctx()])
    if(!is_change) {
      hideMask()
    }

    ele.removeClass('onemodal-bounceIn')
    ele.addClass('onemodal-bounceOut')

    if(isBodyOverflow()) {
      $body.css('overflow-y', 'auto')
      this.resetScrollbar()
    }

    this.$ele.fadeOut(200, function() { //degration for ie
      that.$wrapper.fadeOut(200) //直接hide会让$ele没有动画
      ele.trigger(EVENTS.CLOSE, [that._ctx()])
      if(that.options.removeAfterClose) {
        that.$wrapper.remove()
      }
    })

    this.unbind()
    current = null
  }

  $.onemodal.prototype.bind = function() {
    var that = this

    if (this.options.escapeClose) {
      $(document).on('keydown.onemodal', function (event) {
        if (event.which == 27) {
          $.onemodal.close()
        }
      })
    }

    if (this.options.clickClose) {
      $body.on('click.onemodal', function (e) {
        if (e.target === that.$wrapper[0]) {
          $.onemodal.close()
        }
      })
    }

    $(window).on('resize.onemodal', function () {
      that.center()
    })
  }

  $.onemodal.prototype.unbind = function() {
    $(document).off('keydown.onemodal')
    $body.off('click.onemodal')
    $(window).off('resize.onemodal')
  }

  $.onemodal.prototype.center = function() {
    if(this.isOverflow()) {
      if(isBodyOverflow()) {
        $body.css({
          'overflow-y': 'hidden'
        })
        this.setScrollbar(scrollbarWidth)
      }

      this.$ele.css({
        margin: '20px auto',
        position: 'static'
      })
    } else {
      this.$ele.css({
        position: 'absolute',
        top: '50%',
        marginTop: -(this.$ele.outerHeight() / 2),
        left: 0,
        right: 0,
        marginLeft: 'auto',
        marginRight: 'auto'
      })
    }
  }

  $.onemodal.prototype._ctx = function() {
    return { ele: this.$ele, overlay: $overlay, options: this.options }
  }

  $.onemodal.prototype.setScrollbar = function(scrollbarWidth) {
    var bodyPad = parseInt(($body.css('padding-right') || 0), 10)
    this.originalBodyPad = document.body.style.paddingRight || ''
    $body.css('padding-right', bodyPad + scrollbarWidth)
  }

  $.onemodal.prototype.resetScrollbar = function() {
    $body.css('padding-right', this.originalBodyPad)
  }

  $.onemodal.prototype.isOverflow = function() {
    return this.$ele.outerHeight() - $(window).height() > 0
  }

  $.onemodal.close = function(event) {
    if (!current) return
    if (event) event.preventDefault()
    current.close()
  }

  $.fn.onemodal = function(options) {
    if(this.length === 1) {
      new $.onemodal(this, options)
    }
    return this
  }

  $(document).on('click.onemodal', 'a[rel="onemodal:close"]', $.onemodal.close)
  $(document).on('click.onemodal', 'a[rel="onemodal:open"]', function(event) {
    event.preventDefault()
    $(this).onemodal()
  })
}))

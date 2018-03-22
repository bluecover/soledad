require('lib/validate')
var tmpl_error_start = '<div class="item-info text-red"><i class="iconfont icon-wrong"></i>'
var tmpl_option_start = '<div class="item-info text-orange"><i class="iconfont icon-caution"></i>'
var tmpl_end = '</div>'

function cancelZoom() {
  var d = document
  var viewport
  var content
  var maxScale = ',maximum-scale='
  var maxScaleRegex = /,*maximum\-scale\=\d*\.*\d*/

  if (!this.addEventListener || !d.querySelector) {
    return
  }

  viewport = d.querySelector('meta[name="viewport"]')
  content = viewport.content

  function changeViewport(event) {
    viewport.content = content + (event.type === 'blur' ? (content.match(maxScaleRegex, '') ? '' : maxScale + 10) : maxScale + 1)
  }

  this.addEventListener('focus', changeViewport, true)
  this.addEventListener('blur', changeViewport, false)
}

$.fn.cancelZoom = function () {
  return this.each(cancelZoom)
}

$('input:text,select,textarea').cancelZoom()

function errorHandler(is_error, ele, msg) {
  var item = $(ele).parents('.item')
  ele = $(ele)
  $(ele.data('msg_ele')).remove()

  if (is_error) {
    var res = $(tmpl_error_start + msg + tmpl_end)
    res.insertAfter(item)
    ele.data('msg_ele', res)
  }
}

function optionHandler(ele, msg) {
  var item = $(ele).parents('.item')
  ele = $(ele)
  $(ele.data('msg_ele')).remove()

  var res = $(tmpl_option_start + msg + tmpl_end)
  res.insertAfter(item)
  ele.data('msg_ele', res)
}

function scrollToError(form) {
  var error = $(form).find('.has-error')
  if (error.length) {
    var top = $(error[0]).offset().top
    $('body, html').animate({ scrollTop: top - 50 }, 400, 'swing')
  }
}

var guihuaFormRules = {
  adultAgeLimit: {
    test: function (val) {
      val = parseInt(val, 10)
      if (val > 99 || val < 18) {
        return true
      }
      return false
    },
    msg: '请正确填写成年人年龄'
  },
  minorsAgeLimit: {
    test: function (val) {
      val = parseInt(val, 10)
      if (val > 17) {
        return true
      }
      return false
    },
    msg: '请正确填写未成年子女年龄'
  },
  guihuaLimit: {
    test: function (val) {
      val = parseInt(val, 10)
      if (val > 100000000) {
        return true
      }
      return false
    },
    msg: '请正确填写，不大于1亿'
  },
  guihuaLimitRequire: {
    test: function (val) {
      val = parseInt(val, 10)
      if (val > 100000000 || val < 1) {
        return true
      }
      return false
    },
    msg: '这是必填项，请正确填写，不大于1亿'
  },
  guihuaRealPropertyLimit: {
    test: function (val) {
      val = parseInt(val, 10)
      if (val > 10000) {
        return true
      }
      return false
    },
    msg: '请正确填写实物资产，不大于1亿，请注意单位是万元'
  }
}

$.extend({
  validate: {
    errorHandler: errorHandler,
    optionHandler: optionHandler,
    scrollToError: scrollToError,
    guihuaFormRules: guihuaFormRules
  }
})

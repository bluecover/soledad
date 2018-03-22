require('utils/form_helper')

function addProperty(nav, data) {
  var parent = nav.parents('.info-section')
  var tmpl = nav.hasClass('real') ? $('#tmpl_real_property').html() : $('#tmpl_property').html()
  var item = $(tmpl).hide()
  parent.append(item)
  nav.addClass('on')

  var input = item.find('.js-input')
  nav.data('ele', item)
  item.find('.title').text(nav.text())
  input.attr('name', nav.data('name'))

  if (nav.hasClass('js-house')) {
    input.addClass('js-input-house')
  }

  var keyup = nav.data('keyup') || ''
  if (keyup) {
    var old = input.attr('data-validate-keyup')
    input.attr('data-validate-keyup', old + ',' + keyup)
  }

  if (data) {
    input.val(data)
    item.show()
  } else {
    item.slideDown('fast')
  }
}

$('body').on('click', '.js-header-property a', function () {
  var nav = $(this)
  if (nav.data('ele')) {
    var ele = nav.data('ele')
    nav.removeClass('on')
    nav.data('ele', '')
    $(ele).slideUp('fast', function () {
      $(ele).remove()
    })
    return
  }

  addProperty(nav)
})

function initProperty() {
  var nav = $('.js-header-property a')
  $.each(nav, function (index, item) {
    var data = $(item).data('val') || ''
    if (data) {
      addProperty($(item), data)
    }
  })
}

var info_rules = {
  loanLimit: {
    test: function (val) {
      var house_val = parseInt($('.js-input-house').val(), 10) || 0
      if (val > house_val) {
        return true
      }
      return false
    },
    msg: '未还房贷不能大于房产总值'
  }
}
var helper = $.validate
var config = {
  errorHandler: helper.errorHandler,
  optionHandler: helper.optionHandler,
  failCallback: helper.scrollToError
}
var rules = $.extend(helper.guihuaFormRules, info_rules)

$('.js-form-info3').validateForm(rules, config)
$('.js-submit-form').on('click', function (e) {
  e.preventDefault()
  $('.js-form-info3').submit()
})

initProperty()

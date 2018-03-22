require('utils/form_helper')

function addTarget(length, data) {
  if (length >= 5) {
    return
  }

  var tmpl = $('#tmpl_target').html()
  var placeholder = $('.js-add-target').parents('.item')
  var target = $(tmpl).hide().insertBefore(placeholder)

  if (!length) {
    target.find('.js-del-target').remove()
    target.show()
  }
  if (data) {
    target.find('.js-target-type').val(data.target)
    target.find('.js-target-money').val(data.money)
    target.find('.js-target-year').val(data.year)
    target.show()
  } else {
    target.slideDown('fast')
  }
}

function setTargetData() {
  var target = []
  var target_item = $('.js-target-item')
  target_item.each(function (index, item) {
    var $item = $(item)
    var tar_item = {}
    tar_item.target = $item.find('.js-target-type').val()
    tar_item.money = $item.find('.js-target-money').val()
    tar_item.year = $item.find('.js-target-year').val()
    target.push(tar_item)
  })
  $('#target').val(JSON.stringify(target))
}

function initTargetData() {
  var val = $('#target').data('val')
  if (!val) {
    addTarget(0)
    return
  }

  $.each(val, function (index, item) {
    addTarget(index, item)
    if (index >= 4) {
      $('.js-add-target').parents('.item').hide()
    }
  })
}

$('body')
  .on('click', '.js-add-target', function () {
    var length = $('.info-section .js-target-item').length
    var placeholder = $('.js-add-target').parents('.item')

    length >= 4 ? placeholder.slideUp('fast') : ''
    addTarget(length)
  })
  .on('click', '.js-del-target', function () {
    var parent = $(this).parents('.item')

    $('.js-add-target').parents('.item').slideDown('fast')
    $.each(parent.find('.validate'), function (index, item) {
      $($(item).data('msg_ele')).slideUp('fast')
    })
    parent.slideUp('fast', function () {
      parent.remove()
    })
  })
  .on('click', '.js-submit-form', function () {
    setTargetData()
    $('.js-form-info4').submit()
  })

var info5Rules = {
  targetYearLimt: {
    test: function (val) {
      val = parseInt(val, 10)
      if (val > 50 || val < 1) {
        return true
      }
      return false
    },
    msg: '请正确填写目标完成年限，不超过50年'
  }
}
var helper = $.validate
var rules = $.extend(helper.guihuaFormRules, info5Rules)
var config = {
  errorHandler: helper.errorHandler,
  optionHandler: helper.optionHandler,
  failCallback: helper.scrollToError
}
$('.js-form-info4').validateForm(rules, config)

initTargetData()

require('utils/form_helper')
var input_property = require('./mods/_plan_property.js')
var dlg_error = require('g-error')

$('.js-checkbox-property').on('change', function () {
  var str = $(this).data('property-str')
  var ele = $(this).data('property-ele')
  if ($(this).is(':checked')) {
    input_property.show(str, ele)
  } else {
    input_property.remove(ele)
  }
})

$('.js-expend-property').on('change', function () {
  if ($(this).is(':checked')) {
    $(this).val('1')
  } else {
    $(this).val('-1')
  }
})

$('.js-close').on('click', function () {
  $(this).parent().slideUp()
})

$('.js-btn-submit').on('click', function () {
  $('.js-info-form').submit()
})

function submitData() {
  var params = {
    info_gender: $("[name='info_gender']:checked").val(),
    info_age: $("[name='info_age']:checked").val(),
    info_province: $('.js-province').find('option:selected').val(),
    info_income: $('.js-input-income').val(),
    info_savings: $('.js-input-savings').val()
  }
  $('.js-expend-property').each(function () {
    $(params).attr($(this).attr('id'), $(this).val())
  })

  if ($('.js-monthly-box').length > 0) {
    params.info_monthly = $('.js-monthly-box').find('input').val()
  }
  if ($('.js-rent-box').length > 0) {
    params.info_rent = $('.js-rent-box').find('input').val()
  }
  $.ajax({
    url: '/j/plan/add',
    type: 'POST',
    data: params,
    dataType: 'json'
  }).done(function (c) {
    c.r ? window.location.href = '/plan/brief' : dlg_error.show()
  }).fail(function () {
    dlg_error.show()
  })
}

var info_rules = {
  ageLimit: {
    test: function (val) {
      val = parseInt(val, 10)
      if (val > 50 || val < 18) {
        return true
      }
      return false
    },
    msg: '年龄需在18到50岁之间'
  },
  budgetCheck: {
    test: function (val) {
      var rent_val
      var monthly_val
      var total_expend
      if ($('.js-monthly-box').length > 0) {
        monthly_val = Number($('.js-monthly-box').find('input').val())
        total_expend = monthly_val
      }
      if ($('.js-rent-box').length > 0) {
        rent_val = Number($('.js-rent-box').find('input').val())
        total_expend = rent_val
      }
      if ($('.js-rent-box').length > 0 && $('.js-monthly-box').length > 0) {
        total_expend = rent_val + monthly_val
      }
      if (val < total_expend) {
        return true
      }
      return false
    },
    msg: '收入低于固定支出，请录入您个人实际月收入或实际承担支出'
  }
}

var helper = $.validate
var rules = $.extend(helper.guihuaFormRules, info_rules)
var config = {
  errorHandler: helper.errorHandler,
  optionHandler: helper.optionHandler,
  failCallback: helper.scrollToError,
  successCallback: submitData
}

$('.js-info-form').validateForm(rules, config)

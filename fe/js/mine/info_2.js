require('utils/form_helper')

var info2Rules = {
  incomeLimit: {
    test: function () {
      var incomes = $('.js-income-con .validate')
      var flag = true
      incomes.each(function (index, item) {
        var item_val = parseInt($(item).val(), 10)
        if (item_val && item_val > 0) {
          flag = false
        }
      })
      return flag
    },
    msg: '请至少填写一项收入'
  },
  expendLimit: {
    test: function () {
      var expend = $('.js-expend-con .validate')
      var flag = true
      expend.each(function (index, item) {
        var item_val = parseInt($(item).val(), 10)
        if (item_val && item_val > 0) {
          flag = false
        }
      })
      return flag
    },
    msg: '请至少填写一项支出'
  }
}

var helper = $.validate
var rules = $.extend(helper.guihuaFormRules, info2Rules)
var config = {
  errorHandler: helper.errorHandler,
  optionHandler: helper.optionHandler,
  failCallback: helper.scrollToError
}

$('.js-form-info2').validateForm(rules, config)
$('.js-submit-form').on('click', function (e) {
  $('.js-form-info2').submit()
})

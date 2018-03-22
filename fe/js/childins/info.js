require('utils/form_helper')
var moment = require('moment')

function getBirthDate() {
  var year = $('.js-year').val()
  var month = $('.js-month').val()
  var day = $('.js-day').val()

  if (year && month && day) {
    var birthdate = year + '-' + month + '-' + day
    return birthdate
  }
  return false
}

var child_rules = {
  birthdate: {
    test: function () {
      var birthdate = getBirthDate()
      var birth = moment(birthdate, 'YYYY-MM-DD')
      if (!birth) {
        return true
      }
      var youngest = moment().subtract(31, 'd')
      var oldest = moment().subtract(18, 'y').add(1, 'd')
      if (birth.diff(youngest, 'd') > 0 || oldest.diff(birth, 'd') > 0) {
        return true
      }
      return false
    },
    msg: '出生日期超出规划范围，儿童年龄需大于30 天、小于 18 周岁'
  },
  project: {
    test: function () {
      var projects = $('.js-project-wrapper')
      var inputs = projects.find("input[name='project']")
      if (projects.is(':visible') && (!inputs.is(':checked'))) {
        return true
      }
      return false
    },
    msg: '请选择一个保障方案（只做参考，无需依此购买）'
  },
  valid: {
    test: function () {
      var birthdate = getBirthDate()
      var birth = moment(birthdate, 'YYYY-MM-DD')
      if (!birth.isValid()) {
        return true
      }
      return false
    },
    msg: '无效的日期'
  }
}

function proValidate() {
  $('.js-project-a,.js-project-b,.js-project-c').hide()
  $('.js-child-edu-item').show()
  var birthdate = getBirthDate()
  var birth = moment(birthdate, 'YYYY-MM-DD')
  if (!birth) {
    return
  }
  var youngest = moment().subtract(31, 'd')
  var younger_six = moment().subtract(7, 'y').add(-1, 'd')
  var younger_nine = moment().subtract(10, 'y').add(-1, 'd')
  var younger_thirteen = moment().subtract(14, 'y').add(-1, 'd')
  var project = $("input[name='project']")

  if (youngest.diff(birth, 'd') < 0) {
    $('.js-project-wrapper,.js-child-edu-item').hide()
    $('.js-child-unedu').trigger('click')
    project.attr('checked', false)
    return false
  }
  if (birth.diff(youngest, 'd') > 0 || younger_six.diff(birth, 'd') < 0) {
    $('.js-project-a').show()
    $('.js-project-b,.js-project-c').find(project).attr('checked', false)
    return false
  }
  if (birth.diff(younger_six, 'd') > 0 || younger_nine.diff(birth, 'd') < 0) {
    $('.js-project-b').show()
    $('.js-project-a,.js-project-c').find(project).attr('checked', false)
    return false
  }
  if (birth.diff(younger_nine, 'd') > 0 || younger_thirteen.diff(birth, 'd') < 0) {
    $('.js-project-c').show()
    $('.js-project-a,.js-project-b').find(project).attr('checked', false)
    return false
  }
  if (younger_thirteen.diff(birth, 'd') >= 0) {
    $('.js-project-wrapper,.js-child-edu-item').hide()
    $('.js-child-unedu').trigger('click')
    project.attr('checked', false)
    return false
  }
}

var helper = $.validate
var rules = $.extend(helper.guihuaFormRules, child_rules)
var config = {
  errorHandler: helper.errorHandler,
  optionHandler: helper.optionHandler,
  failCallback: helper.scrollToError
}

$('.js-child-form').validateForm(rules, config)

if ($('.js-child-edu-input').is(':checked')) {
  $('.js-project-wrapper').show()
}
proValidate()

$('body')
  .on('change', '.js-year, .js-month, .js-day', function () {
    var birthdate = getBirthDate()
    $('.js-birth-date').val(birthdate)
    proValidate()
    if ($('.js-child-edu-input').is(':checked')) {
      $('.js-child-edu').trigger('click')
    }
  })
  .on('click', '.js-child-edu', function () {
    var birthdate = getBirthDate()
    var birth = moment(birthdate, 'YYYY-MM-DD')
    if (!birth) {
      return
    }
    $('.js-child-edu-item,.js-project-wrapper').show()
    proValidate()
  })
  .on('click', '.js-child-unedu', function () {
    $("input[name='project']").attr('checked', false)
    $('.js-project-wrapper').hide()
  })
  .on('click', '.js-submit-form', function () {
    var birthdate = getBirthDate()
    $('.js-birth-date').val(birthdate)
    $('.js-child-form').submit()
  })

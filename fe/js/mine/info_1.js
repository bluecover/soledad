require('utils/form_helper')
var cityData = require('lib/city')

function initSocietyInsure(ele, value) {
  var item = $(ele)
  value = value || item.attr('data-society-insure') || 0
  var tmpl = $('#tmpl_society_insure').html()
  item.html(tmpl)
  item.val(value)
}

function initBizInsure() {
  var insures = $('[data-insure]')
  $.each(insures, function (index, item) {
    var insure = $(item).data('insure') || []
    var add_placeholder = $(item).parents('.item').find('.js-add-insure')
    $.each(insure, function (i, insure_item) {
      addBizInsure(add_placeholder, insure_item)
    })
  })
}

function initChildData() {
  var children = $('input[name=children]').data('val') || []
  $.each(children, function (index, item) {
    addChildItem(index, item)
    if (index >= 2) {
      $('.js-add-child').parents('.item').addClass('hide')
    }
  })
}

function initPageData() {
  $('[data-society-insure]').each(function (index, item) {
    initSocietyInsure(item)
  })

  initBizInsure()
  initChildData()
}

function addBizInsure(ele, data) {
  var tmpl = $('#tmpl_biz_insure').html()
  var item = ele.parents('.item')
  var biz = $(tmpl).hide().insertBefore(item)
  if (data) {
    biz.find('.js-biz-type').val(data.insure_type)
    biz.find('.js-biz-insure-year-fee').val(data.insure_year_fee)
    biz.find('.js-biz-insure-quota').val(data.insure_quota)
    biz.show()
  } else {
    biz.slideDown('fast')
  }
}

function addChildItem(number, data) {
  var parent = $('.js-add-child').parents('.item')
  var tmpl = $('#tmpl_child').html()
  var child = $(tmpl).hide().insertBefore(parent)
  var society_insure = child.find('.js-child-society-insure')

  child.find('.js-child-number').text(number + 1)
  initSocietyInsure(society_insure)

  if (data) {
    var biz = data.biz_insure || []
    var btn_biz = child.find('.js-add-insure')
    child.find('.js-child-age').val(data.age)
    society_insure.val(data.child_society_insure || 0)
    $.each(biz, function (index, biz_item) {
      addBizInsure(btn_biz, biz_item)
    })
    child.show()
  } else {
    child.slideDown('fast')
  }
}

function wrapBizInsure(ele) {
  var data = []
  var biz = $(ele).find('.js-biz-item')
  if (!biz.length) {
    return []
  }

  $.each(biz, function (index, item) {
    var insure_type = $(item).find('.js-biz-type').val()
    var fee = $(item).find('.js-biz-insure-year-fee').val()
    var quota = $(item).find('.js-biz-insure-quota').val()
    var biz_item = {
      insure_type: insure_type,
      insure_year_fee: fee,
      insure_quota: quota
    }
    data.push(biz_item)
  })

  return data
}

function setMineBiz() {
  var input = $('input[name=mine_biz_insure]')
  var biz = input.parents('.js-biz-insure-con')
  var data = JSON.stringify(wrapBizInsure(biz))
  input.val(data)
}

function setSpouseBiz() {
  var input = $('input[name=spouse_biz_insure]')
  var biz = input.parents('.js-biz-insure-con')
  var data = JSON.stringify(wrapBizInsure(biz))
  input.val(data)
}

function wrapChildren() {
  var data = []
  var children = $('.js-child-con')
  if (!children.length) {
    return
  }

  $.each(children, function (index, item) {
    var child = {}
    var age = $(item).find('.js-child-age').val()
    var society_insure = $(item).find('.js-child-society-insure').val()
    var biz_insure = wrapBizInsure($(item).find('.js-biz-insure-con'))

    child = {
      age: age,
      child_society_insure: society_insure,
      biz_insure: biz_insure
    }
    data.push(child)
  })

  $('input[name=children]').val(JSON.stringify(data))
}

function wrapData() {
  setMineBiz()
  setSpouseBiz()
  wrapChildren()
}

$('body')
  .on('click', '.js-add-insure', function () {
    var biz_parent = $(this).parents('.js-biz-insure-con')
    var number = biz_parent.find('.js-biz-item').length
    if (number >= 5) {
      return
    }
    if (number === 4) {
      $(this).parents('.item').slideUp('fast')
    }
    addBizInsure($(this))
  })

  .on('click', '.js-del-insure', function () {
    var item = $(this).parents('.item')
    $('.js-add-insure').parents('.item').slideDown('fast')

    item.slideUp('fast', function () {
      $.each(item.find('.validate'), function (index, insure_item) {
        $($(insure_item).data('msg_ele')).remove()
      })
      item.remove()
    })
  })

  .on('click', '.js-add-spouse', function () {
    $('.js-spouse').val(1)
    $('.js-spouse-info').hide().removeClass('hide').slideDown('fast')
    $('.js-add-spouse').parents('.item').slideUp('fast')
  })

  .on('click', '.js-del-spouse', function () {
    $('.js-spouse').val('')
    $('.js-spouse-info').slideUp('fast', function () {
      $('input[name=spouse_age]').val('')
      $('.js-spouse-info .js-biz-item').remove()
      $('.js-spouse-info .item-info').remove()
    })
    $('.js-add-spouse').parent().hide().removeClass('hide').slideDown('fast')
  })

  .on('click', '.js-add-child', function () {
    var number = $('.info-section .js-child-con').length
    if (number >= 3) {
      return
    }
    if (number === 2) {
      $(this).parents('.item').slideUp('fast')
    }
    addChildItem(number)
  })

  .on('click', '.js-del-child', function () {
    var parent = $(this).parents('.js-child-con')
    if ($('.info-section .js-child-con').length <= 3) {
      $('.js-add-child').parents('.item').slideDown('fast')
    }
    parent.slideUp('fast', function () {
      parent.remove()
    })
  })

  .on('change', '#js_province', function () {
    var val = $(this).val()
    var city = cityData[val].children
    var tmpl = []
    $.each(city, function (index, item) {
      var city_item = '<option value="' + item['id'] + '">' + item['name'] + '</option>'
      tmpl.push(city_item)
    })
    $('#js_city').empty().html(tmpl.join(''))
  })

var helper = $.validate
var rules = helper.guihuaFormRules
var config = {
  errorHandler: helper.errorHandler,
  optionHandler: helper.optionHandler,
  failCallback: helper.scrollToError
}

$('.js-form-info1').validateForm(rules, config)

$('.js-submit-form').on('click', function () {
  wrapData()
  $('.js-form-info1').submit()
})

initPageData()

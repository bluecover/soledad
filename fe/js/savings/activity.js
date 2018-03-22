require('utils/form_helper')
var province_data = require('lib/city')
var dlg_error = require('g-error')
var dlg_succ = require('mods/modal/modal_success')
var address_form = $('.js-address-form')

var district_codes = $('input[name=district_codes]').data('val') || []
district_codes = JSON.parse(JSON.stringify(district_codes))
var province_code = district_codes[0]
var city_code = district_codes[1]
var county_code = district_codes[2]
var address_id = $('input[name=address_id]').data('val')

function initProvince(selected) {
  var tmpl = []
  $.each(province_data, function (key, value) {
    var province_item = '<option value="' + key + '">' + value['name'] + '</option>'
    tmpl.push(province_item)
  })
  var items = tmpl.join('')
  $(items).insertAfter('.js-province-defalut')
  $('.js-province').val(selected)
}

function initCity(province_code, selected) {
  if (!province_code) {
    return
  }
  var data_url = '/j/division/' + province_code + '/prefectures'
  $.ajax({
    url: data_url,
    type: 'get'
  }).done(function (c) {
    var tmpl = []
    $.each(c.data, function (key, value) {
      var city_item = '<option value="' + value['code'] + '">' + value['name'] + '</option>'
      tmpl.push(city_item)
    })
    var items = tmpl.join('')
    $(items).insertAfter('.js-city-defalut')
    $('.js-city').val(selected)
  }).fail(function () {
    dlg_error.show('获取城市信息失败，请重试')
  })
}

function initDistrict(city_code, selected) {
  if (!city_code) {
    return
  }
  var data_url = '/j/division/' + city_code + '/counties'
  $.ajax({
    url: data_url,
    type: 'get'
  }).done(function (c) {
    var tmpl = []
    $.each(c.data, function (key, value) {
      var district_item = '<option value="' + value['code'] + '">' + value['name'] + '</option>'
      tmpl.push(district_item)
    })
    var items = tmpl.join('')
    $(items).insertAfter('.js-district-defalut')
    $('.js-district').val(selected)
  }).fail(function () {
    dlg_error.show('获取地区信息失败，请重试')
  })
}

function obtainData() {
  $('.js-province-defalut,.js-city-defalut,.js-district-defalut').siblings('option').remove()
  $('.js-name').val($('.js-name-txt').text())
  $('.js-phone').val($('.js-phone-txt').text())
  $('.js-street').val($('.js-street-txt').text())
  // 获取地区信息
  initProvince(province_code)
  initCity(province_code, city_code)
  initDistrict(city_code, county_code)
}

initProvince(0)

$('.js-address').on('click', function () {
  $('.js-address-cancel').removeClass('hide')
  $(this).addClass('hide')
  address_form.slideDown()
  obtainData()
})
$('.js-address-cancel').on('click', function () {
  $('.js-address').removeClass('hide')
  $(this).addClass('hide')
  address_form.slideUp()
})
$('.js-btn-confirm').on('click', function () {
  $('.js-address-form').submit()
})
$('.js-province').on('change', function () {
  $('.js-city-defalut,.js-district-defalut').siblings('option').remove()
  initCity($('.js-province').val(), 0)
})
$('.js-city').on('change', function () {
  $('.js-district-defalut').siblings('option').remove()
  initDistrict($('.js-city').val(), 0)
})

function addressData() {
  var params = {
    name: $('.js-name').val(),
    phone: $('.js-phone').val(),
    province: $('.js-province').val(),
    city: $('.js-city').val(),
    district: $('.js-district').val(),
    street: $('.js-street').val(),
    address_id: address_id
  }
  $.ajax({
    url: '/j/address/submit',
    type: 'POST',
    data: params,
    dataType: 'json'
  }).done(function (c) {
    if (c.r) {
      address_id = c.address_id
      address_form.slideUp()
      $('.js-address-wrapper,.js-address').removeClass('hide')
      $('.js-unaddress-wrapper,.js-address-cancel').addClass('hide')
      $('.js-name-txt').text($('.js-name').val())
      $('.js-phone-txt').text($('.js-phone').val())
      var address_text = $('.js-province,.js-city,.js-district').find('option:selected').text()
      $('.js-address-txt').text(address_text)
      $('.js-street-txt').text($('.js-street').val())
      $('html, body').animate({
        scrollTop: $('.js-address-wrapper').offset().top
      })
      province_code = $('.js-province').find('option:selected').val()
      city_code = $('.js-city').find('option:selected').val()
      county_code = $('.js-district').find('option:selected').val()
    } else {
      dlg_error.show(c.error)
    }
  }).fail(function () {
    dlg_error.show()
  })
}

var address_rules = {
  addselect: {
    test: function () {
      if ($('.js-district').val() === 0) {
        return true
      }
      return false
    },
    msg: '请选择完整的地址信息'
  }
}

var helper = $.validate
var rules = $.extend(helper.guihuaFormRules, address_rules)
var config = {
  errorHandler: helper.errorHandler,
  optionHandler: helper.optionHandler,
  failCallback: helper.scrollToError,
  successCallback: addressData
}

address_form.validateForm(rules, config)

var progress = $('.js-total-money').data('val')
var progress_rate = (parseFloat(progress / 80000) * 100).toFixed('2')
$('.js-progress-inner').animate({width: progress_rate + '%'})

$('body').on('click', '.js-get-gift', function () {
  var form = $('.js-get-gift-form')
  form.submit()
})

$('.js-flashed-message').each(function () {
  dlg_succ.show({
    success_msg: $(this).val()
  })
})

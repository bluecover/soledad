require('utils/form_helper')

var tmpl_form = require('./_tmplCardForm.hbs')
var city_raw = require('savings/mods/_city')

function CardForm(container, options) {
  var $ele = $(tmpl_form({
    bankData: options.bankData,
    cardData: options.cardData || null
  }))
  $(container).html($ele)

  this.$ele = $ele
  this.$bank = $('.js-bank', $ele)
  this.$province = $('.js-province', $ele)
  this.$city = $('.js-city', $ele)
  this.$card_num = $('.js-cardnum', $ele)
  this.$auto_branch = $('.js-auto-branch', $ele)
  this.$manual_branch = $('.js-manual-branch', $ele)
  this.$btn_to_auto = $('.js-switch-to-auto', $ele)
  this.$btn_to_manual = $('.js-switch-to-manual', $ele)
  this.$con_auto = $('.js-auto-con', $ele)
  this.$con_man = $('.js-manual-con', $ele)
  this.$mobile = $('.js-phone', $ele)
  this.$bank_type = $('.js-sub-type', $ele).val('auto')
  this.$bank_tele_name = $('.js-bank-tele-name', $ele)
  this.$bank_tel = $('.js-bank-tel', $ele)
  this.cardData = options.cardData || null

  if (this.cardData) {
    this.setBankInfo()
    this.setManualSelect()
  } else {
    this.initProvince()
  }

  this.bindEvent()
  this.bindValidate()

  return this
}

CardForm.prototype.initProvince = function () {
  var tmpl = []
  $.each(city_raw, function (key, value) {
    var province_item = '<option value="' + key + '">' + value['name'] + '</option>'
    tmpl.push(province_item)
  })
  this.$province.html(tmpl.join(''))
  this.setCity()
}

CardForm.prototype.bindEvent = function () {
  this.$bank.on('change', this.setBank.bind(this))
  this.$city.on('change', this.setBank.bind(this))
  this.$province.on('change', this.setCity.bind(this))
  this.$btn_to_auto.on('click', this.setAutoSelect.bind(this))
  this.$btn_to_manual.on('click', this.setManualSelect.bind(this))
}

CardForm.prototype.bindValidate = function () {
  var that = this
  var pay_rules = {
    cardnum: {
      test: function (val) {
        var reg_int = /^\d*$/
        return !reg_int.test(val)
      },
      msg: '请正确填写银行卡号'
    },
    bank_type: {
      test: function (val, ele) {
        var type = that.$bank_type.val()
        if (type === $(ele).data('type')) {
          if (!val) {
            return true
          }
        }
        return false
      },
      msg: '请选择或填写支行信息'
    }
  }

  var helper = $.validate
  var rules = $.extend(pay_rules, helper.guihuaFormRules)
  var config = {
    errorHandler: helper.errorHandler,
    optionHandler: helper.optionHandler,
    failCallback: helper.scrollToError,
    successCallback: that.checkSucc.bind(that)
  }

  this.$ele.validateForm(rules, config)
}

CardForm.prototype.getData = function () {
  var bank_branch_name = this.$bank_type.val() === 'auto' ? this.$auto_branch.val() : this.$manual_branch.val()
  var selected_bank = $('option:selected', this.$bank)
  var bank_name = selected_bank.text()

  var data = {
    mobile_phone: this.$mobile.val(),
    card_number: this.$card_num.val(),
    bank_branch_name: bank_branch_name,
    bank_name: bank_name,
    bank_id: this.$bank.val(),
    city_id: this.$city.val(),
    province_id: this.$province.val()
  }

  return data
}

CardForm.prototype.checkSucc = function () {
  // placeholder
}

CardForm.prototype.destory = function () {
  this.$ele.remove()
}

CardForm.prototype.setCity = function () {
  var province = this.$province.val()
  var city = city_raw[province].children
  var tmpl = []
  $.each(city, function (index, item) {
    var city_item = '<option value="' + item['id'] + '">' + item['name'] + '</option>'
    tmpl.push(city_item)
  })

  this.$city.html(tmpl.join(''))
  this.setBank()
}

CardForm.prototype.setBank = function () {
  this.setBankInfo()
  // this.setBankList()
}

CardForm.prototype.setBankInfo = function () {
  var selected_bank = $('option:selected', this.$bank) || this.$bank.val()
  var bank_name = selected_bank.text()
  var bank_tele = selected_bank.data('tele')

  if (selected_bank.val()) {
    this.$bank_tele_name.text(bank_name)
    this.$bank_tel.text(bank_tele)
    this.$bank_tel.parents('p').removeClass('hide')
  } else {
    this.$bank_tel.parents('p').addClass('hide')
    this.$bank_tele_name.text('')
    this.$bank_tel.text('')
  }
}

CardForm.prototype.setBankList = function () {
  var that = this
  var bank_id = this.$bank.val()
  var city_id = this.$city.val()
  var $auto_branch = this.$auto_branch

  if (bank_id && city_id) {
    $.ajax({
      type: 'GET',
      url: '/j/savings/bank',
      data: {
        bank_id: bank_id,
        city_id: city_id
      }
    }).done(function (data) {
      if (data.r && data.banks && data.banks.length) {
        that.setAutoSelect()
        var tmpl = []
        $.each(data.banks, function (index, item) {
          var bank = '<option value="' + item + '">' + item + '</option>'
          tmpl.push(bank)
        })
        $auto_branch.html(tmpl.join(''))
        $auto_branch.val($('option:first', $auto_branch).val())
      } else {
        $auto_branch.html('<option value="">无可选支行，请手动输入</option>')
      }
    }).fail(function () {
      $auto_branch.html('<option value="">无可选支行，请手动输入</option>')
    })
  }
}

CardForm.prototype.setAutoSelect = function (e) {
  this.$con_auto.removeClass('hide')
  this.$con_man.addClass('hide')
  this.$bank_type.val('auto')

  if (e) {
    this.setBank()
  }
}

CardForm.prototype.setManualSelect = function () {
  this.$con_auto.addClass('hide')
  this.$con_man.removeClass('hide')
  this.$bank_type.val('manual')
}

module.exports = CardForm

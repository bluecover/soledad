var once = require('once')
var Form = require('./_cardForm')
var tmpl = require('./_tmplCardModal.hbs')
var dlgError = require('g-error')
var dlgLoading = require('g-loading')
var CardAction = require('./_cardAction.jsx')
var appDispatcher = require('utils/dispatcher')

var $tmpl
var _cardForm

function setForm(options) {
  _cardForm = new Form($tmpl.find('.js-form'), {
    bankData: options.bankData
  })
}

var initOnce = once(function (options) {
  $tmpl = $(tmpl())
  $('body').append($tmpl)

  setForm(options)

  $tmpl.find('.js-btn-submit').on('click', function () {
    var formData = getFormData()
    if (formData) {
      dlgLoading.show()

      $.ajax({
        type: 'POST',
        url: '/j/bankcard/?partner=' + options.partner,
        data: formData
      }).done(function (data) {
        if (data.r) {
          $.onemodal.close()
          setForm(options)
          CardAction.updateCards(data.bankcards)
          // TODO 也不是very清真
          appDispatcher.dispatch({
            actionType: 'bankcard:bindCard',
            card_id: data.bankcard_id
          })
        } else {
          dlgError.show(data.error).on('onemodal:close', function () {
            $tmpl.onemodal({
              clickClose: false,
              escapeClose: false
            })
          })
        }
      }).fail(function (r) {
        var error
        if (r && r.responseJSON && r.responseJSON.error) {
          error = r.responseJSON.error
        }
        dlgError.show(error).on('onemodal:close', function () {
          $tmpl.onemodal({
            clickClose: false,
            escapeClose: false
          })
        })
      })
    }
  })
})

function getFormData() {
  if (_cardForm.$ele.data('validate').validate()) {
    return _cardForm.getData()
  }
  return false
}

module.exports = {
  show: function (options) {
    initOnce(options)
    $tmpl.onemodal({
      clickClose: false,
      escapeClose: false
    })
    return $tmpl
  },

  showEdit: function (options) {
    var $editTmpl = $(tmpl())
    $('body').append($editTmpl)

    var _cardForm = new Form($editTmpl.find('.js-form'), {
      bankData: options.bankData,
      cardData: options.cardData
    })

    $editTmpl.find('.js-btn-submit').text('修改').on('click', function () {
      var formData

      if (_cardForm.$ele.data('validate').validate()) {
        formData = _cardForm.getData()
      }

      if (formData) {
        dlgLoading.show()

        $.ajax({
          type: 'PUT',
          url: '/j/bankcard/' + options.cardData.card_id + '?partner=' + options.partner,
          data: formData
        }).done(function (data) {
          if (data.r) {
            $.onemodal.close()
            CardAction.updateCards(data.bankcards)
            CardAction.setCurrent(options.cardData.card_id)
          } else {
            dlgError.show(data.error)
          }
        }).fail(function () {
          dlgError.show()
        })
      }
    })

    $editTmpl.onemodal({
      clickClose: false,
      escapeClose: false
    })
    return $editTmpl
  }
}

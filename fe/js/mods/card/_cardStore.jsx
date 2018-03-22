var EventEmitter = require('events').EventEmitter
var appDispatcher = require('utils/dispatcher')
var objectAssign = require('object-assign')

var _cards = []
var _banks = []
var _current
let _card_current

function _setCurrent(cardId) {
  for (var i = 0; i < _cards.length; i++) {
    if (_cards[i].status !== 'unbound' && _cards[i].status !== 'invalid' && _cards[i].card_id === cardId) {
      _current = cardId
      _card_current = _cards[i]
      return
    }
  }
}

function _updateCards(cards) {
  _cards = cards
  _initCurrent()
}

function _initCurrent() {
  _current = null
  for (var i = 0; i < _cards.length; i++) {
    if (_cards[i].status !== 'unbound' && _cards[i].status !== 'invalid') {
      _current = _cards[i].card_id
      _card_current = _cards[i]
      return
    }
  }
}

var CardStore = objectAssign({}, EventEmitter.prototype, {
  initData: function (data) {
    _cards = data.cards
    _banks = data.bankData
    _initCurrent()
  },

  getAllCards: function () {
    return _cards
  },

  getBank: function () {
    return _banks
  },

  getCurrentCard: function () {
    return _card_current
  },

  getCurrentId: function () {
    return _current
  }
})

appDispatcher.register(function (payload) {
  switch (payload.actionType) {
    case 'bankcard:setCurrent':
      _setCurrent(payload.cardId)
      CardStore.emit('change')
      break
    case 'bankcard:updateCards':
      _updateCards(payload.cards)
      CardStore.emit('change')
      break
  }
})

module.exports = CardStore

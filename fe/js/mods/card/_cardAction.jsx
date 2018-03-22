var appDispatcher = require('utils/dispatcher')

var CardAction = {
  setCurrent: function (cardId) {
    appDispatcher.dispatch({
      actionType: 'bankcard:setCurrent',
      cardId: cardId
    })
  },

  updateCards: function (cards) {
    appDispatcher.dispatch({
      actionType: 'bankcard:updateCards',
      cards: cards
    })
  }
}

module.exports = CardAction

var Card = require('./_card.jsx')
var CardStore = require('./_cardStore.jsx')
var dlgCardForm = require('./_cardModal')

function getWrapperState(product_category) {
  return {
    cards: CardStore.getAllCards(),
    bankData: CardStore.getBank()
  }
}

function filterUsedBank(banks, cards) {
  if (cards.length) {
    var used = cards.map(function (item) {
      return item.bank_id
    })

    banks = banks.filter(function (item) {
      if (used.indexOf(item.bank_id) < 0) {
        return true
      }
    })
  }

  return banks
}

var CardWrapper = React.createClass({
  getInitialState: function () {
    CardStore.initData({
      cards: this.props.cards,
      bankData: this.props.bankData
    })
    return getWrapperState(this.props.productCategory)
  },

  componentDidMount: function () {
    CardStore.on('change', function () {
      this.setState(getWrapperState())
    }.bind(this))
  },

  handleAddCard: function () {
    var bankData = filterUsedBank(this.state.bankData, this.state.cards)
    dlgCardForm.show({
      bankData: bankData,
      partner: this.props.partner
    })
  },

  handleEdit: function (card) {
    dlgCardForm.showEdit({
      bankData: this.state.bankData,
      partner: this.props.partner,
      cardData: card
    })
  },

  getCurrentCard: function () {
    return CardStore.getCurrentCard()
  },

  renderAddBankCard: function () {
    let cards_data = this.state.cards
    let product_category = this.props.productCategory
    if (product_category === 'wallet') {
      for (let card of cards_data) {
        if (card && card.status === 'valid') {
          return
        }
      }
    }

    return (
      <a href="#" onClick={this.handleAddCard} className="btn-add-card">+ 添加银行卡</a>
    )
  },

  render: function () {
    let add_card = this.renderAddBankCard()
    return (
      <div className="bankcard-wrapper">
        <h2 className="block-title">银行卡信息</h2>
        <ul>
          {this.state.cards.map(function (card) {
            return (<Card card={card} key={card.card_id} handleEdit={this.handleEdit.bind(this, card)} productCategory={this.props.productCategory}/>)
          }, this)}
        </ul>
        {add_card}
      </div>
    )
  }
})

module.exports = CardWrapper

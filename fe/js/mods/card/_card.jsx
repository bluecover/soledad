var cx = require('classnames')
var CardStore = require('./_cardStore.jsx')
var CardAction = require('./_cardAction.jsx')
var appDispatcher = require('utils/dispatcher')

var Card = React.createClass({
  handleClick: function (e) {
    if (this.props.card.status === 'unbound') {
      appDispatcher.dispatch({
        actionType: 'bankcard:bindCard',
        card_id: this.props.card.card_id
      })
      return false
    } else if (this.props.card.status === 'invalid') {
      return false
    } else {
      CardAction.setCurrent(this.props.card.card_id)
    }
  },

  handleEdit: function (e) {
    this.props.handleEdit()
    e.preventDefault()
    e.stopPropagation()
  },

  renderModifyPhone: function () {
    if (this.props.productCategory === 'wallet') {
      return
    }
    return (
      <div className="options">
          <a href="#" onClick={this.handleEdit}>修改</a>
      </div>
    )
  },

  render: function () {
    var card_data = this.props.card
    let modify_phone = this.renderModifyPhone()
    var meta

    switch (card_data.status) {
      case 'invalid':
        meta = <p className="meta-data">不能用于该产品</p>
        break
      case 'unbound':
        break
      case 'valid':
      default:
        meta = <p className="meta-data">限额：{card_data.bank_limit}</p>
    }

    var rowCls = cx({
      'item': true,
      'valid': card_data.status !== 'invalid' && card_data.status !== 'unbound',
      'checked': card_data.card_id === CardStore.getCurrentId()
    })

    return (
      <li className={rowCls} onClick={this.handleClick}>
        <span className="img-con"><img src={this.props.card.icon_url.mdpi}/></span>
        <div className="bank-info">
          <p>{card_data.bank_name} (尾号 {card_data.tail_card_number})</p>
          {meta}
        </div>
        {modify_phone}
      </li>
    )
  }
})

module.exports = Card

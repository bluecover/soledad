var classNames = require('classnames')
var appDispatcher = require('utils/dispatcher')

var classes

var RecordItem = React.createClass({
  handleRecordDetail: function () {
    appDispatcher.dispatch({
      actionType: 'reocrd:modalDetail',
      record_detail: this.props.item
    })
  },

  orderStatus: function () {
    var status = this.props.item.order_status
    classes = classNames({
      'btn': true,
      'btn-badge': true,
      'btn-warning': (status === '已失败'),
      'btn-primary': (status === '确认中'),
      'btn-info': (status === '已转出')
    })
  },

  render: function () {
    this.orderStatus()
    var item_data = this.props.item
    return (
      <tr onClick={this.handleRecordDetail}>
        <td>
          <span className={classes}>{item_data.order_status}</span>
          <span className="number">
            {item_data.savings_money}元
          </span>
        </td>
        <td className="text-center  desktop-element">{item_data.invest_date}</td>
        <td className="text-center">{item_data.due_date}</td>
        <td className="text-right">{item_data.annual_rate}%</td>
      </tr>
    )
  }
})

module.exports = RecordItem

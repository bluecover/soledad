var RecordItem = require('./_recordItem.jsx')

var Record = React.createClass({
  render: function () {
    function getAllRecord() {
      return (
        <div className="ft">
          <a href="../record" className="btn btn-gray">查看全部记录</a>
        </div>
      )
    }
    var all_record_btn = (this.props.allRecord) ? null : getAllRecord()

    if (this.props.recordsData.length === 0) {
      return (
        <div className="text-12">暂无交易</div>
      )
    } else {
      return (
        <div>
          <table>
            <thead>
              <tr>
                <td>攒钱金额</td>
                <td className="text-center desktop-element">交易日期</td>
                <td className="text-center">到期日</td>
                <td className="text-right">年化收益率</td>
              </tr>
            </thead>
            <tbody>
              {this.props.recordsData.map(function (item, index) {
                return (
                  <RecordItem key={index} item={item}/>
                )
              }, this)}
            </tbody>
          </table>
          {all_record_btn}
        </div>
      )
    }
  }
})

module.exports = Record

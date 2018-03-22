import cx from 'classnames'

var ShareWeixin = React.createClass({
  getInitialState: function () {
    return {
      showQr: false
    }
  },

  handleClick: function (attribute) {
    this.setState({
      showQr: !this.state.showQr
    })
  },

  render: function () {
    let classes = cx(this.props.className, {
      'share-btn btn-weixin': true
    })
    return (
      <span>
        <a href="#" className={classes} onClick={this.handleClick}>{this.props.text}</a>
        {this.state.showQr ? <Qrcode data={this.props.data} close={this.handleClick.bind(this)}/> : null}
      </span>
    )
  }
})

var Qrcode = React.createClass({
  render: function () {
    var qrStyle = {
      main: {
        position: 'fixed',
        top: 0,
        left: 0,
        bottom: 0,
        right: 0,
        width: 300,
        height: 400,
        backgroundColor: '#fff',
        padding: '40px',
        margin: 'auto',
        textAlign: 'left',
        boxShadow: '0 0 5px #999',
        zIndex: 100
      },
      img: {
        display: 'inline-block',
        width: 220,
        height: 220
      },
      closeBtn: {
        position: 'absolute',
        top: 10,
        right: 10,
        fontSize: 24
      },
      ft: {
        lineHeight: 1.5,
        marginTop: 10,
        fontSize: '14px'
      }
    }

    return (
      <div id="qrcode-mod" style={qrStyle.main} className="qrcode-mod">
        <div className="hd">
          <h3 className="title">{this.props.data.title}</h3>
          <a style={qrStyle.closeBtn}
             onClick={this.props.close}
             className="close-btn" href="#">&times;</a>
        </div>
        <div className="bd">
          <img style={qrStyle.img} className="qrcode-img" src={this.props.data.picUrl} />
        </div>
        <div className="ft text-lighter" style={qrStyle.ft}>{this.props.data.desc}</div>
      </div>
    )
  }
})

module.exports = ShareWeixin

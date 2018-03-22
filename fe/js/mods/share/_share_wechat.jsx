let mask = require('mods/mask')({background: 'rgba(0,0,0,0.7)'})
import cx from 'classnames'

class ShareWechat extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      maskStatus: false
    }
    this.handleMaskClick = this.handleMaskClick.bind(this)
    this.handleBtnClick = this.handleBtnClick.bind(this)
  }

  handleMaskClick() {
    this.setState({
      maskStatus: false
    })
  }

  handleBtnClick() {
    this.setState({
      maskStatus: true
    })
  }

  getMask() {
    let shareStyle = {
      img: {
        width: '60%',
        transform: 'rotate(-35deg)',
        '-webkit-transform': 'rotate(-35deg)',
        '-moz-transform': 'rotate(-35deg)',
        '-o-transform': 'rotate(-35deg)',
        '-ms-transform': 'rotate(-35deg)',
        marginBottom: '15%',
        marginTop: '15%'
      },
      text: {
        fontSize: '20px',
        color: '#fff',
        textAlign: 'center'
      }
    }
    if (this.state.maskStatus) {
      return (
        <div style={mask.opts} className="text-right" onClick={this.handleMaskClick}>
          <img style={shareStyle.img} src="{{{img/misc/arrow2.svg}}}" alt=""/>
          <p style={shareStyle.text}>点击右上角，分享到朋友圈</p>
        </div>
      )
    }
  }

  render() {
    let shareMask = this.getMask()
    let classes = cx(this.props.className, {
      'btn btn-primary': true
    })
    return (
      <div>
        {shareMask}
        <a href="#" onClick={this.handleBtnClick} className={classes}>分享给好友</a>
      </div>
    )
  }
}

export default ShareWechat

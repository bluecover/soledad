const PropTypes = React.PropTypes

class AccountHeader extends React.Component {
  render() {
    let title = this.props.title ? (<h3 className="title">{this.props.title}</h3>) : null
    let weixin_src = this.props.weixin_src || '{{{img/misc/qrcode.png}}}'

    return (
      <div className="m-account-header">
        <div className="hd">
          <img src="{{{img/logo.png}}}" alt="好规划"/>
          {title}
        </div>
        <div className="ft">
          <img src={weixin_src} alt="微信公众号"/>
          <p className="desc">关注微信公众号</p>
        </div>
      </div>
    )
  }
}

AccountHeader.propTypes = {
  title: PropTypes.string,
  weixin_src: PropTypes.string
}

export default AccountHeader

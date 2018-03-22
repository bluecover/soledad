import cx from 'classnames'

import RegForm from './_regForm.jsx'
import LoginForm from './_loginForm.jsx'
import AccountHeader from './_accountHeader.jsx'

const PropTypes = React.PropTypes

const LOGIN = 'login'
const REGISTER = 'register'

class Account extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      type: props.type || LOGIN
    }

    this.switchAccount = this.switchAccount.bind(this)

  }

  setSubmitInfo(info) {
    this.refs.loginForm.setSubmitInfo(info)
    this.refs.regForm.setSubmitInfo(info)
  }

  switchAccount(type) {
    this.setState({
      type: type
    })
  }

  render() {
    let loginClass = this.state.type === REGISTER ? 'hide' : null
    let regClass = this.state.type === LOGIN ? 'hide' : null

    let classNames = cx({
      'm-account': true,
      'm-account-reg': this.state.type === REGISTER,
      'm-account-login': this.state.type === LOGIN
    })

    return (
      <div className={classNames}>
        <div className="wrapper">
          <div className="hd desktop-element">
            <AccountHeader title={this.props.page} />
          </div>
          <div className="bd">
            <LoginForm ref='loginForm' login_btn_text={this.props.login_btn_text} className={loginClass} switchAccount={this.switchAccount} />
            <RegForm ref='regForm' register_btn_text={this.props.register_btn_text} className={regClass} switchAccount={this.switchAccount} />
          </div>
        </div>
      </div>
    )
  }
}

Account.propTypes = {
  page: PropTypes.string,
  type: PropTypes.string
}

export default Account

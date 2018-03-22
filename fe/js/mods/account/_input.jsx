import cx from 'classnames'

const PropTypes = React.PropTypes

function isPlaceholderSupport() {
  return 'placeholder' in document.createElement('input')
}

class Input extends React.Component {
  constructor(props) {
    super()

    this.state = {
      value: '',
      error: '',
      showPlaceholder: true
    }

    // 初始化 field 验证状态
    this._initIsValid(props.validation)
  }

  _initIsValid(validation) {
    if (validation && validation.indexOf('required') !== -1) {
      this._isValid = false
    }

    this._isValid = true
  }

  getValue() {
    return (this.refs.input && this.refs.input.value) || this.state.value
  }

  setValue(value) {
    this.setState({
      value: value
    })
  }

  getError() {
    return this.state.error
  }

  setError(error) {
    this.setState({
      error: error
    })
  }

  validate() {
    // 从 form parent 组件中获取通用 rulels 规则
    this._rules = this.context && this.context.form.rules

    let val = this.getValue()
    let validations = this.props.validation || ''

    // 仅当 rules 存在时才会执行检查, 所以允许单独使用 input
    if (this._rules && validations.length) {
      validations = validations.split('|')

      for (let validation of validations) {
        if (!this._rules[validation].rule(val)) {
          let res = this._rules[validation].error
          this._isValid = false
          this.setError(res)

          // 依次检查每种规则，有错误就返回且停止后续检查
          return res
        }
      }

      this.setError('')
      this._isValid = true

      return
    }

  }

  isValid() {
    return this._isValid
  }

  handleBlur(e) {
    this.getValue() ? null : this.setState({
      showPlaceholder: true
    })

    this.validate()
  }

  handleFocus(e) {
    this.getValue() ? null : this.setState({
      showPlaceholder: false
    })
  }

  handleChange(e) {
    this.setValue(e.target.value)
  }

  componentWillMount() {
    this.context && this.context.form.attachToForm(this)
  }

  componentWillUnmount() {
    this.context && this.context.form.detachFromForm(this)
  }

  _renderHelp() {
    let error = this.getError()

    // 如果有错误，优先显示错误，否则显示提示文案
    let msg = error || this.props.tip
    let classNames = cx({
      'help-block': true,
      'visible': !!msg
    })
    return (
      <p className={classNames}>
        {error ? <i className="iconfont icon-wrong"></i> : null}
        {msg}
      </p>
    )
  }

  // 设置 iconfont
  _renderIcon() {
    let icon
    if (this.props.iconClass) {
      let iconClasses = cx({
        'iconfont': !!this.props.iconClass
      }, this.props.iconClass)

      icon = <i className={iconClasses}></i>
    }

    return icon
  }

  render() {
    let classNames = cx({
      'form-group': true,
      'has-error': !!this.getError()
    }, this.props.className)

    // 去除不必要的属性
    let {className, iconClass, tip, type, children, placeholder, ...other} = this.props

    placeholder = this.state.showPlaceholder ? this.props.placeholder : null

    return (
      <div className={classNames}>
        <div>
          <label
            ref="label"
            htmlFor={this.props.id}>{isPlaceholderSupport() ? null : placeholder}</label>

          {this._renderIcon()}
          <input
            ref="input"
            placeholder={placeholder}
            type={this.props.type}
            value={this.getValue()}
            onChange={this.handleChange.bind(this)}
            onFocus={this.handleFocus.bind(this)}
            onBlur={this.handleBlur.bind(this)}
            {...other} />

          {this.props.children}
        </div>
        {this._renderHelp()}
      </div>
    )
  }
}

// Input 只管理自己的 value 状态，error 由父组件传递
Input.propTypes = {
  id: PropTypes.string.isRequired,
  type: PropTypes.string,
  tip: PropTypes.string,
  className: PropTypes.string,
  iconClass: PropTypes.string,
  placeholder: PropTypes.string
}

Input.contextTypes = {
  form: PropTypes.object
}

Input.defaultProps = {
  type: 'text'
}

export default Input

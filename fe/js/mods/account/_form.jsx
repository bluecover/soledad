import rules from './_validation_rules'

const PropTypes = React.PropTypes

class Form extends React.Component {
  constructor(props) {
    super(props)

    this.state = {}

    // 所有 form fields eg.{username: 'haoguihua@gmail.com'}
    this._fields_map = new Map()

    // 表单提交后跳转 url
    this._redirect_url = '/'

    // 自定义检验规则 @1
    this._rules = Object.assign({}, rules, props.rules)
  }

  // 为 child component 创建 context，使子组件通过 component.context.form 能访问所返回的对象
  getChildContext() {
    return {
      form: {
        attachToForm: this.attachToForm.bind(this),
        detachFromForm: this.detachFromForm.bind(this),
        rules: this._rules
      }
    }
  }

  // 检查单个 field 或整个表单
  validate(name) {
    if (name) {
      this._fields_map.get(name).validate()
    } else {
      for (let [, component] of this._fields_map) {
        component.validate()
      }
    }
  }

  // 获取单个 field 或整个表单是否通过检查状态
  isValid(name) {
    if (name) {
      let component = this._fields_map.get(name)
      return component.isValid()
    } else {
      let valid = true
      for (let [, component] of this._fields_map) {
        if (!component.isValid()) {
          valid = false
          break
        }
      }
      return valid
    }
  }

  // 设置表单错误内容，分为 field error 和 common error
  setError(errors) {
    if (errors.commonError) {
      this.setState({
        commonError: errors.commonError
      })
    }

    for (let name of Object.keys(errors)) {
      if (name !== 'commonError') {
        this._fields_map.get(name).setError(errors[name])
      }
    }
  }

  _renderCommonError() {
    let commonError
    if (this.getCommonError()) {
      commonError = (
        <p className="help-block has-error all-error">
          <i className="iconfont icon-wrong"></i>
          {this.getCommonError()}
        </p>
      )
    }

    return commonError
  }

  getCommonError() {
    return this.state.commonError
  }

  // 取得某个 field 的值
  getFieldValue(name) {
    return this._fields_map.get(name).getValue()
  }

  // 获取全部 fields 的值
  getAllFields() {
    let fields = {}
    for (let [field, component] of this._fields_map) {
      fields[field] = component.getValue()
    }
    return fields
  }

  // 将某个组件绑定到 form 上
  attachToForm(component) {
    this._fields_map.set(component.props.name, component)
  }

  // 将某个组件从 form 解绑
  detachFromForm(component) {
    this._fields_map.set(component.props.name, component)
  }

  // 设置表单提交前需要的相关信息
  setSubmitInfo(info) {
    this._redirect_url = info.redirect_url
    this._stats_info = info.stats

    if (info.handleSubmitSuccess) {
      this.handleSubmitSuccess = info.handleSubmitSuccess
    }
  }

  // 获取表单提交后跳转 url
  getRedirectUrl() {
    return this._redirect_url
  }

  // 获取统计相关信息
  getStatsInfo() {
    return this._stats_info
  }

  handleSubmit(e) {
    // 每次提交前清空通用错误
    if (this.getCommonError()) {
      this.setError({
        commonError: ''
      })
    }

    e.preventDefault()

    this.validate()

    if (this.isValid()) {
      this.sendSubmit()
    } else {
      return
    }
  }

  handleSubmitSuccess() {
    if (this.getRedirectUrl()) {
      window.location = this.getRedirectUrl()
    } else {
      window.location.reload()
    }
  }

  sendSubmit() {
    let url = this._api_url
    let stats = this.getStatsInfo()
    if (stats && stats.dcm) {
      url += '?' + $.param(stats)
    }

    let params = this.getAllFields()

    $.ajax({
      url: url,
      type: 'POST',
      dataType: 'json',
      data: params
    }).done(() => {
      this.handleSubmitSuccess()
    }).fail((c) => {
      if (c && c.responseJSON) {
        let errors = c.responseJSON.errors

        // return obj: {field_name: error_msg, ...}
        errors = handleServiceError(errors)

        this.setError(errors)

      } else {
        this.setError({
          commonError: '您的提交出现了错误，请重试!'
        })
      }
    })
  }

  componentWillUnmount() {
    this._fields_map = null
    this._stats_info = null
  }
}

Form.childContextTypes = {
  form: PropTypes.object
}

function handleServiceError(errors) {
  let new_errors = {}

  for (let error of errors) {
    if (error.field) {
      new_errors[error.field] = error.message
    } else {
      new_errors.commonError = error.message
    }
  }

  return new_errors
}

export default Form

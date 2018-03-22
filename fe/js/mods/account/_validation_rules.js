import Rules from 'lib/re.js'

// 通用检验规则，可通过给 form 组件传递 rules 属性自定义规则，见下面 @1
const rules = {
  username: {
    rule: function (val) {
      if (!Rules.email.test(val) && !Rules.phone.test(val)) {
        return false
      }
      return true
    },
    error: '请输入正确的手机号或邮箱'
  },
  captcha: {
    rule: function (val) {
      let captcha_reg = /\d{4}/
      if (!captcha_reg.test(val)) {
        return false
      }
      return true
    },
    error: '请输入正确的验证码'
  },
  password: {
    rule: function (val) {
      if (val.length < 6) {
        return false
      }
      return true
    },
    error: '请输入至少 6 位密码'
  },
  phone: {
    rule: function (val) {
      if (!Rules.phone.test(val)) {
        return false
      }
      return true
    },
    error: '请输入正确的手机号'
  },
  email: {
    rule: function (val) {
      if (!Rules.email.test(val)) {
        return false
      }
      return true
    },
    error: '请输入正确的邮箱'
  },
  required: {
    rule: function (val) {
      if (!val) {
        return false
      }
      return true
    },
    error: '这是必填项，请填写'
  }
}

export default rules

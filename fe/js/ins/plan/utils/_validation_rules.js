const validation_rules = {
  child: {
    rule: (val) => {
      if (val < 18) {
        return false
      }
      return true
    },
    error: '请输入 18-55 之间的整数'
  },

  older: {
    rule: (val) => {
      if (val > 55) {
        return false
      }
      return true
    },
    error: '请输入 18-55 之间的整数'
  },

  positive_integer: {
    rule: (val) => {
      if (!/^\d+$/.test(val)) {
        return false
      }
      return true
    },
    error: '只支持正整数，请正确填写'
  },

  number_0_100: {
    rule: (val) => {
      if (/^\d+$/.test(val) && val >= 0 && val <= 100) {
        return true
      } else {
        return false
      }
    },
    error: '请输入 0-100 之间的整数'
  },

  number_1_100: {
    rule: (val) => {
      if (/^\d+$/.test(val) && val >= 1 && val <= 100) {
        return true
      } else {
        return false
      }
    },
    error: '请输入 1-100 之间的整数'
  },

  number_0_1000: {
    rule: (val) => {
      if (/^\d+$/.test(val) && val >= 0 && val <= 1000) {
        return true
      } else {
        return false
      }
    },
    error: '请输入 0-1000 之间的整数'
  },

  number_1_1000: {
    rule: (val) => {
      if (/^\d+$/.test(val) && val >= 1 && val <= 1000) {
        return true
      } else {
        return false
      }
    },
    error: '请输入 1-1000 之间的整数'
  },

  number_0_1000000: {
    rule: (val) => {
      if (/^\d+$/.test(val) && val >= 0 && val <= 1000000) {
        return true
      } else {
        return false
      }
    },
    error: '请输入 0-1000000 之间的整数'
  },

  required: {
    rule: function (val) {
      if (val === null || val === undefined || val === '') {
        return false
      }
      return true
    },
    error: '这是必填项，请填写'
  }
}

export default validation_rules

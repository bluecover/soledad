import validation_rules from './_validation_rules.js'

function validate(value, rules) {
  let validation_res

  rules = rules.split('|')

  for (let rule of rules) {
    let validate = validation_rules[rule].rule
    let error = validation_rules[rule].error

    let res = validate(value)
    if (!res) {
      validation_res = error
      break
    } else {
      validation_res = null
    }

  }

  return validation_res
}

export default validate

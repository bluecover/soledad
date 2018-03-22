import * as type from '../_constant'
import validate from 'ins/plan/utils/_validate'
import validateRevenue from 'ins/plan/adult/reducer/_validate_revenue'

function planData(state = {}, action) {
  let payload = action.payload

  switch (action.type) {
    case type.ADD_PLAN_DATA:
      let value = payload.value
      let name = payload.name

      let input = {
        ...state[name],
        value
      }

      let input_owner
      if (value === '未婚') {
        input_owner = {
          value: '自己',
          error: null
        }

        return {
          ...state,
          owner: input_owner,
          [name]: input
        }
      }

      return {
        ...state,
        [name]: input
      }

    case type.VALIDATE:
      let validation = payload.validation
      let error
      name = payload.name

      if (name === 'annual_revenue') {
        return validateRevenue(state)
      }

      value = state[name] && state[name].value || ''
      error = validate(value, validation)

      input = {
        ...state[name],
        error
      }

      return {
        ...state,
        [name]: input
      }

    case type.COMPLETE_FORM:
      if (state.marriage.value === '未婚') {
        delete state.annual_revenue_family
      }

      return {
        ...state,
        ...payload
      }

    default:
      return state
  }
}

export default planData

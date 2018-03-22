import { createStore, applyMiddleware } from 'redux'
import thunk from 'redux-thunk'

import reducer from './reducer/_reducer'

let server_state = $('#ins_plan_consulting').data('plan') || {}

const initial_state = hydrateState(server_state)

const middlewares = [thunk]
if (process.env.NODE_ENV === 'development') {
  const createLogger = require('redux-logger')
  const logger = createLogger()
  middlewares.push(logger)
}

let createStoreWithMiddleware = applyMiddleware(...middlewares)(createStore)

let store = createStoreWithMiddleware(reducer, initial_state)

function hydrateState(state) {
  let initial_state = {
    gender: {
      value: '女性',
      error: null
    }
  }

  const PROPS = [
    'id',
    'gender',
    'marriage',
    'owner',
    'age',
    'annual_revenue_family',
    'annual_revenue_personal',
    'resident',
    'has_social_security',
    'has_complementary_medicine',
    'family_duty',
    'older_duty',
    'spouse_duty',
    'child_duty',
    'loan_duty',
    'asset',
    'annual_premium'
  ]

  for (let name in state) {
    if (PROPS.indexOf(name) !== -1 && state[name] !== '') {
      if (name === 'id') {
        initial_state[name] = state[name]
      } else {
        initial_state[name] = {
          value: state[name],
          error: null
        }
      }
    }
  }

  return {
    planData: initial_state,
    view: {
      progress: 0,
      show_start: ['start_que'],
      show_dialogs: [],
      show_form: '',
      is_login: state.is_login
    }
  }
}

export default store

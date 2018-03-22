import { combineReducers } from 'redux'

import planData from './_plan_data.js'
import view from './_view.js'

const plan = combineReducers({
  planData,
  view
})

export default plan

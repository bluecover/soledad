import _select from 'ins/plan/utils/_select'

import {
  addPlanData,
  validate,
  addDialog,
  completeForm,
  showForm
} from 'ins/plan/_actions'

function select(all_states) {

  let states = _select({ all_states })

  return states
}

function selectAction(dispatch) {
  return {
    addAnswer: (anwser) => dispatch(addPlanData(anwser)),
    showForm: (show_form) => dispatch(showForm(show_form)),
    completeForm: (stage) => dispatch(completeForm(stage)),
    addDialog: (show) => dispatch(addDialog(show)),
    validate: (payload) => dispatch(validate(payload))
  }
}

export {
  select,
  selectAction
}

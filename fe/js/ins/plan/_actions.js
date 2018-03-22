import * as type from './_constant'
import dialogs_show_rule from './_dialog_list.js'

function addPlanData(payload) {
  return {
    type: type.ADD_PLAN_DATA,
    payload: payload
  }
}

function showForm(show_form) {
  return {
    type: type.SHOW_FORM,
    payload: {
      show_form
    }
  }
}

function completeForm(payload) {
  return (dispatch, getState) => {
    dispatch({
      type: type.COMPLETE_FORM,
      payload
    })

    _updateDialogs(dialogs_show_rule, payload.stage, dispatch)
  }
}

function addDialog(show) {
  return {
    type: type.ADD_DIALOG,
    payload: {
      show
    }
  }
}

function _updateDialogs(dialogs_show_rule, stage, dispatch) {
  let time_total = 0
  let dialogs_will_show = dialogs_show_rule[stage]

  for (let dialog of dialogs_will_show) {
    time_total += dialog.timeout
    setTimeout(() => {
      dispatch(addDialog(dialog.name))
    }, time_total)
  }
}

function validate(payload) {
  return {
    type: type.VALIDATE,
    payload
  }
}

export {
  addPlanData,
  showForm,
  completeForm,
  addDialog,
  validate
}

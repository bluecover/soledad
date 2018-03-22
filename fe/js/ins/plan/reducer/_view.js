import * as type from '../_constant'

function view(state = {}, action) {
  switch (action.type) {
    case type.COMPLETE_FORM:
      return {
        ...state,
        progress: action.payload.stage
      }

    case type.SHOW_FORM:
      return {
        ...state,
        show_form: action.payload.show_form
      }

    case type.ADD_DIALOG:
      if (action.payload.show === 'start_ans') {
        return {
          ...state,
          show_start: state.show_start.concat(action.payload.show)
        }
      } else {
        return {
          ...state,
          show_dialogs: state.show_dialogs.concat(action.payload.show)
        }
      }
      break

    default:
      return state
  }
}

export default view

function _select({ names, all_states }) {
  let states = {}
  for (let state_name in all_states) {
    if (!all_states.hasOwnProperty(state_name)) {
      continue
    }

    let state = all_states[state_name]
    for (let name in state) {

      if (state.hasOwnProperty(name) &&
          (names === undefined || names.indexOf(name) !== -1)) {
        states = {
          ...states,
          [name]: state[name]
        }
      }

    }

  }

  return states
}

export default _select

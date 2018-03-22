import { connect } from 'react-redux'

import {
  select,
  selectAction
} from './_container'

import StartForm from '../views/forms/_start_form.jsx'

class StartFormContainer extends React.Component {
  constructor() {
    super()
  }

  render() {
    return <StartForm {...this.props} />
  }
}

export default connect(select, selectAction)(StartFormContainer)

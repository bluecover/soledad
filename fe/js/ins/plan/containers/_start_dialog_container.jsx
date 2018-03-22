import { connect } from 'react-redux'

import {
  select,
  selectAction
} from './_container'

import StartDialog from '../views/_start_dialog.jsx'

class StartDialogContainer extends React.Component {
  constructor() {
    super()
  }

  render() {
    return <StartDialog {...this.props} />
  }
}

export default connect(select, selectAction)(StartDialogContainer)

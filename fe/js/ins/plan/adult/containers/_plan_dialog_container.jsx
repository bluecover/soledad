import { connect } from 'react-redux'

import {
  select,
  selectAction
} from 'ins/plan/containers/_container'

import PlanDialog from '../views/_plan_dialog.jsx'

class PlanDialogContainer extends React.Component {
  constructor() {
    super()
  }

  render() {
    return <PlanDialog {...this.props} />
  }
}

export default connect(select, selectAction)(PlanDialogContainer)

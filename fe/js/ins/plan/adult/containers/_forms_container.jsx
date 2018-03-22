import { connect } from 'react-redux'

import {
  select,
  selectAction
} from 'ins/plan/containers/_container'

import Forms from '../views/_survey_forms.jsx'

class FormsContainer extends React.Component {
  constructor() {
    super()
  }

  render() {
    return <Forms {...this.props} />
  }
}

export default connect(select, selectAction)(FormsContainer)

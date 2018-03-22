import { connect } from 'react-redux'

import AdultFormsContainer from 'ins/plan/adult/containers/_forms_container.jsx'

function select(state) {
  return {
    owner: state.planData.owner
  }
}

const SurveyFormsContainer = (props) => {
  let {
    owner = {}
  } = props

  let forms
  if (owner.value === '自己' || owner.value === '配偶') {
    forms = <AdultFormsContainer />
  }

  return (
    <div>
      {forms}
    </div>
  )
}

export default connect(select)(SurveyFormsContainer)

import { connect } from 'react-redux'

import AdultPlanDialogContainer from 'ins/plan/adult/containers/_plan_dialog_container.jsx'
import StartDialogContainer from './containers/_start_dialog_container.jsx'
import { PLANNER_NAME } from 'ins/plan/_constant.js'

function select(state) {
  return {
    owner: state.planData.owner
  }
}

class App extends React.Component {
  render() {
    let {
      owner = {}
    } = this.props

    owner = owner.value

    let plan_consulting
    if (owner === '自己' || owner === '配偶') {
      plan_consulting = (
        <AdultPlanDialogContainer {...this.props}/>
      )
    }

    return (
      <div className="m-plan-consulting">
        <div className="hd">

          <div className="m-planner">
            <div className="hd">
              <img className="avatar" src="{{{img/ins/plan/cfp_avatar.png}}}" alt="理财师头像"/>
            </div>
            <div className="bd">
              <h3 className="name">{PLANNER_NAME}</h3>
              <p className="desc">好规划专属理财规划师</p>
            </div>
          </div>

        </div>
        <div className="bd">
          <StartDialogContainer {...this.props}/>
          {plan_consulting}
        </div>
      </div>
    )
  }
}

export default connect(select)(App)

import MODS from './qa/_qa.jsx'

class PlanDialog extends React.Component {
  constructor(props) {
    super(props)
  }

  _renderDialogs(show_dialogs, family_duty, progress) {
    let dialogs = []
    let index

    let has_family_duty = family_duty && family_duty.indexOf('clear') === -1

    if (progress === 5 && has_family_duty) {
      index = show_dialogs.indexOf('annual_premium_que')
      index !== -1 ? show_dialogs.splice(index, 1) : null
    }

    if (show_dialogs.length) {
      for (let name of show_dialogs) {
        dialogs.push(MODS[name](this.props))
      }
    }

    return dialogs
  }

  render() {
    let {
      family_duty = {},
      progress,
      show_dialogs
    } = this.props

    family_duty = family_duty.value

    return (
      <div className="m-plan-dialogs">
        {this._renderDialogs(show_dialogs, family_duty, progress)}
      </div>
    )
  }
}

export default PlanDialog

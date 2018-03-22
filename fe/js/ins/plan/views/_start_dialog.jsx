import StartQue from 'ins/plan/views/_start_que.jsx'
import StartAns from 'ins/plan/views/_start_ans.jsx'

const start_que = (props) => {
  let isCompleted = props.progress > 0

  return (
    <StartQue
      key={0}
      id={props.id}
      isCompleted={isCompleted}
      showForm={props.showForm}
    />
  )
}

const start_ans = (props) => {
  return (
    <StartAns
      key={1}
      gender={props.gender}
      marriage={props.marriage}
      owner={props.owner}
    />
  )
}

const MODS = {
  start_que,
  start_ans
}

class StartDialog extends React.Component {
  constructor(props) {
    super(props)
  }

  _renderDialogs(show_start) {
    let dialogs = []
    if (show_start.length) {
      for (let name of show_start) {
        dialogs.push(MODS[name](this.props))
      }
    }

    return dialogs
  }

  render() {
    let {
      show_start
    } = this.props

    return (
      <div className="m-start-dialogs">
        {this._renderDialogs(show_start)}
      </div>
    )
  }
}

export default StartDialog

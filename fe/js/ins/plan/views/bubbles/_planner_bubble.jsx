import getScrollBottom from 'utils/get_scroll_bottom'

class LoadingBubble extends React.Component {
  constructor(props) {
    super(props)
  }

  componentDidMount() {
    setTimeout(() => {
      this.props.handleEnding()
    }, this.props.timeout || 1000)

  }

  render() {
    return (
      <div className="m-loading-bubble">
        <ul>
          <li></li>
          <li></li>
          <li></li>
        </ul>
      </div>
    )
  }
}

class PlannerBubble extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      show_loading: true
    }

    this._msg_tip = $('.js-ins-msg-tip')
  }

  componentDidMount() {
    if (getScrollBottom() > 100) {
      this._msg_tip.show()
    }
  }

  hideLoading() {
    this.setState({
      show_loading: false
    })
  }

  render() {
    let props = this.props

    let loadingBubble = (
      <LoadingBubble
        timeout={props.loading_timeout}
        handleEnding={this.hideLoading.bind(this)} />
    )

    let content = this.state.show_loading ? loadingBubble : <div>{props.children}</div>

    return (
      <div className="m-planner-bubble" key={props.key}>
        <div className="hd">
          <div className="avatar">
            <img src={props.img_src || '{{{img/ins/plan/cfp_avatar.png}}}'} alt="理财师头像" />
          </div>
        </div>
        <div className="bd">
          <div className="wrap">
            {content}
          </div>
        </div>
      </div>
    )
  }
}

export default PlannerBubble

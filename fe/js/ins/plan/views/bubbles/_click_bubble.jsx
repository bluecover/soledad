class ClickBubble extends React.Component {
  constructor(props) {
    super()

    this.handleClick = props.handleClick || this.handleClick.bind(this)
  }

  componentDidMount() {
    let {
      showForm,
      show_form
    } = this.props

    showForm && showForm(show_form)
  }

  handleClick() {
    let {
      showForm,
      href,
      forms_container = '#ins_survey_forms'
    } = this.props

    if (showForm) {
      $(forms_container).onemodal()
    }

    if (href) {
      window.location.replace(href)
    }
  }

  render() {
    return (
      <div className="m-click-bubble" key={this.props.key}>
        <div className="bd" onClick={this.handleClick}>
          <div className="wrap">
            <p>
              {this.props.children || '点击填写信息'}
              <i className="iconfont icon-arrowright"></i>
            </p>
          </div>
        </div>
      </div>
    )
  }
}

export default ClickBubble

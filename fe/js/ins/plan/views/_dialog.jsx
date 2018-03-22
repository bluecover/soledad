class Dialog extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      show_paragraphs_num: 0
    }
  }

  componentDidMount() {
    this.show_paragraphs(this._paragraphs_show_rule)
  }

  _addParagraph() {
    this.setState({
      show_paragraphs_num: this.state.show_paragraphs_num + 1
    })
  }

  show_paragraphs(paragraphs_show_rule) {
    let time_total = 0
    for (let timeout of paragraphs_show_rule) {
      time_total += timeout
      setTimeout(() => {
        this._addParagraph()
      }, time_total)
    }
  }
}

export default Dialog

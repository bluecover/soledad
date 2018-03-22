class InputGroup extends React.Component {
  constructor(props) {
    super(props)
  }

  render() {
    let { title, error, ...others } = this.props

    return (
      <div className="m-input-group">
        <div
          {...others}
          className="input-group">
          <div className="hd">
            <h3 className="title">
              <span className="text">{title}</span>
            </h3>
          </div>
          <div className="bd">
            {this.props.children}
          </div>
        </div>
        <div className="input-group-error">
          <p>{error}</p>
        </div>
      </div>
    )
  }

}

class Input extends React.Component {
  constructor(props) {
    super(props)

    this.handleBlur = this.handleBlur.bind(this)
    this.handleChange = this.handleChange.bind(this)
    this.handleKeyDown = this.handleKeyDown.bind(this)
  }

  handleKeyDown(e) {
    let {
      blurValidation,
      validate,
      name
    } = this.props

    if (e.which === 13) {
      blurValidation && validate({
        name,
        validation: blurValidation
      })
    }
  }

  handleChange() {
    let {
      onChange,
      changeValidation,
      name,
      validate
    } = this.props

    onChange && onChange({
      name,
      value: this.refs.age.value
    })

    changeValidation && validate({
      name,
      validation: changeValidation
    })
  }

  handleBlur() {
    let {
      onBlur,
      name,
      blurValidation,
      validate
    } = this.props

    onBlur && onBlur({
      name,
      value: this.refs.age.value
    })

    blurValidation && validate({
      name,
      validation: blurValidation
    })
  }

  render() {
    let {
      value,
      title,
      name,
      unit,
      error,
      ...props
    } = this.props

    return (
      <div className="m-input">
        <div className="bd">
          <span className="title">
            {title}
          </span>
          <input
            ref="age"
            type="text"
            {...props}
            name={name}
            onBlur={this.handleBlur}
            onChange={this.handleChange}
            onKeyDown={this.handleKeyDown}
            value={value}/>
          <span className="unit">
            {unit}
          </span>
        </div>
        <div className="ft">
          {error}
        </div>
      </div>
    )
  }
}

export {
  InputGroup,
  Input
}

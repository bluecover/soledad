import cx from 'classnames'

class Select extends React.Component {
  constructor(props) {
    super(props)

    // 存储 options 数据
    this._options = []
    React.Children.forEach(props.children, (child) => {
      if (child.type === 'option') {
        this._options.push({
          value: child.props.value,
          content: child.props.children
        })
      }
    })

    this.onChangeSelect = this.onChangeSelect.bind(this)
  }

  handleMultipleSelectChange(selected_value) {
    let {
      value
    } = this.props

    if (selected_value === 'clear') {
      return ['clear']
    }

    let new_value
    if (value) {
      let value_set = new Set(value)

      if (value_set.has(selected_value)) {
        value_set.delete(selected_value)
      } else {
        value_set.add(selected_value)
        value_set.delete('clear')
      }

      new_value = Array.from(value_set)
      new_value = new_value.length ? new_value : null
    } else {
      new_value = [selected_value]
    }

    return new_value
  }

  onChangeSelect(e) {
    let {
      onChange,
      changeValidation,
      name,
      value,
      multiple,
      validate
    } = this.props

    let selected_value = e.currentTarget.getAttribute('data-value')

    if (multiple) {
      value = this.handleMultipleSelectChange(selected_value)
    } else {
      value = selected_value
    }

    onChange({
      name,
      value
    })

    changeValidation && validate({
      name,
      validation: changeValidation
    })
  }

  setOptionClass(option_value) {
    let {
      value,
      disabled,
      multiple
    } = this.props

    let option_className = disabled ? 'option disabled' : 'option'

    if (multiple && value && value.indexOf(option_value) !== -1) {
      option_className = 'option active'
    }

    if (value === option_value) {
      option_className = 'option active'
    }

    return option_className
  }

  renderOptions() {
    let {
      disabled
    } = this.props

    let options
    let option_className

    options = this._options.map((option, key) => {
      option_className = this.setOptionClass(option.value)

      return (
        <li className={option_className}
            data-value={option.value}
            onClick={disabled ? null : this.onChangeSelect}
            key={key}>
            {option.content}
            <i className="iconfont icon-smcheck"></i>
        </li>
      )
    })

    return options
  }

  render() {
    let {
      title,
      className
    } = this.props

    className = cx('m-select', className)

    return (
      <div className={className}>
        <div className="hd">
          <h3 className="title">
            <span className="text">{title}</span>
          </h3>
        </div>
        <div className="bd">
          <ul className="options">
            {this.renderOptions()}
          </ul>
        </div>
        <div className="ft">
        </div>
      </div>
    )
  }
}

Select.propTypes = {
  title: React.PropTypes.string.isRequired,
  name: React.PropTypes.string.isRequired
}

export default Select

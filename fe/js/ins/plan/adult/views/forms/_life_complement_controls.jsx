import Select from 'ins/plan/views/forms/_select.jsx'

let older_duty = (props) => {
  return getSelect({
    key: 0,
    title: '照料老人还需',
    name: 'older_duty',
    props
  })
}

let spouse_duty = (props) => {
  return getSelect({
    key: 1,
    title: '照顾配偶还需',
    name: 'spouse_duty',
    props
  })
}

let child_duty = (props) => {
  return getSelect({
    key: 2,
    title: '抚养子女还需',
    name: 'child_duty',
    props
  })
}

let loan_duty = (props) => {
  return getSelect({
    key: 3,
    title: '偿还贷款还需',
    name: 'loan_duty',
    props
  })
}

function getSelect({
  title,
  name,
  key,
  props
}) {

  return (
    <Select
      key={key}
      name={name}
      title={title}
      value={props[name] && props[name].value}
      changeValidation="required"
      validate={props.validate}
      onChange={props.addAnswer}>
      <option value="a">15 万元以内</option>
      <option value="b">20 – 50 万元</option>
      <option value="c">50 – 100 万元</option>
      <option value="d">100 万元以上</option>
    </Select>
  )
}

export {
  older_duty,
  spouse_duty,
  child_duty,
  loan_duty
}

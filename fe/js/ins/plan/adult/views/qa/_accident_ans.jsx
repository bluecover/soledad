import UserBubble from 'ins/plan/views/bubbles/_user_bubble.jsx'

import getSubject from 'ins/plan/utils/_get_subject.js'

const AccidentAns = (props) => {
  let {
    gender,
    marriage,
    owner,
    annual_revenue_personal,
    annual_revenue_family,
    resident
  } = props

  let subject = getSubject({
    owner: owner.value,
    gender: gender.value,
    is_que: false
  })

  let subject2 = marriage.value === '未婚' ? '我' : '我们'

  let family_revenue
  if (marriage.value === '已婚') {
    family_revenue = '；家庭年收入 ' + annual_revenue_family.value + ' 万元'
  }

  return (
    <UserBubble>
      <p>{subject}年收入 {annual_revenue_personal.value} 万元{family_revenue}。</p>
      <p>{subject2}生活在{resident.value}。</p>
    </UserBubble>
  )
}

export default AccidentAns

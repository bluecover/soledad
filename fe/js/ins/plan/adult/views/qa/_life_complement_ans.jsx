import UserBubble from 'ins/plan/views/bubbles/_user_bubble.jsx'

import { FAMILY_DUTY, DUTY_FIELDS } from 'ins/plan/_constant'
import getSubject from 'ins/plan/utils/_get_subject.js'

const DUTY_VALUE = {
  a: '15 万元以内',
  b: '20 - 50 万元',
  c: '50 - 100 万元',
  d: '100 万元以上'
}

const LifeComplementAns = (props) => {
  let {
    gender,
    owner,
    marriage,
    asset,
    family_duty
  } = props

  gender = gender.value
  owner = owner.value
  marriage = marriage.value
  asset = asset.value
  family_duty = family_duty.value

  let subject = getSubject({
    owner,
    gender,
    is_que: false
  })

  family_duty = family_duty.map((duty_name) => {
    let duty_type
    let duty_value

    if (duty_name !== 'clear') {
      let duty = props[DUTY_FIELDS[duty_name]]
      duty_type = duty && duty.value
      duty_value = DUTY_VALUE[duty_type]
    }

    return FAMILY_DUTY[duty_name] + '还需 ' + duty_value
  })

  let family = marriage === '已婚' ? '家庭' : '我'

  return (
    <UserBubble>
      <p>{subject}{family_duty.join('，')}。</p>
      <p>{family}现有金融资产 {asset} 万元。</p>
    </UserBubble>
  )
}

export default LifeComplementAns

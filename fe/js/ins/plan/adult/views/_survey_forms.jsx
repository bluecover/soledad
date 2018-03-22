import FoundationForm from './forms/_foundation_form.jsx'
import AccidentForm from './forms/_accident_form.jsx'
import CIForm from './forms/_ci_form.jsx'
import LifeForm from './forms/_life_form.jsx'
import LifeComplementForm from './forms/_life_complement_form.jsx'
import AnnualPremiumForm from './forms/_annual_premium_form.jsx'

const foundation_form = (props) => {
  return (
    <FoundationForm {...props} />
  )
}

const accident_form = (props) => {
  return (
    <AccidentForm {...props} />
  )
}

const ci_form = (props) => {
  return (
    <CIForm {...props} />
  )
}

const life_form = (props) => {
  return (
    <LifeForm {...props} />
  )
}

const life_complement_form = (props) => {
  return (
    <LifeComplementForm {...props} />
  )
}

const annual_premium_form = (props) => {
  return (
    <AnnualPremiumForm {...props} />
  )
}

const SURVEY_FORMS = {
  foundation_form,
  accident_form,
  ci_form,
  life_form,
  life_complement_form,
  annual_premium_form
}

const SurveyForms = (props) => {
  let {
    show_form
  } = props

  return (
    <div>
      {SURVEY_FORMS[show_form] && SURVEY_FORMS[show_form](props)}
    </div>
  )
}

export default SurveyForms

import FoundationQue from './_foundation_que.jsx'
import FoundationAns from './_foundation_ans.jsx'
import FoundationRes from './_foundation_res.jsx'
import AccidentQue from './_accident_que.jsx'
import AccidentAns from './_accident_ans.jsx'
import AccidentRes from './_accident_res.jsx'
import CIQue from './_ci_que.jsx'
import CIAns from './_ci_ans.jsx'
import CIRes from './_ci_res.jsx'
import LifeQue from './_life_que.jsx'
import LifeAns from './_life_ans.jsx'
import LifeRes from './_life_res.jsx'
import LifeComplementAns from './_life_complement_ans.jsx'
import LifeComplementRes from './_life_complement_res.jsx'
import AnnualPremiumQue from './_annual_premium_que.jsx'
import AnnualPremiumAns from './_annual_premium_ans.jsx'
import AnnualPremiumRes from './_annual_premium_res.jsx'
import End from 'ins/plan/views/_end.jsx'

const foundation_que = (props) => {
  let isCompleted = props.progress > 1

  return (
    <FoundationQue
      key={0}
      isCompleted={isCompleted}
      owner={props.owner}
      gender={props.gender}
      showForm={props.showForm}/>
  )
}

const foundation_ans = (props) => {
  return (
    <FoundationAns
      key={1}
      age={props.age}
      owner={props.owner}
      gender={props.gender}/>
  )
}

const foundation_res = (props) => {
  return (
    <FoundationRes
      key={2}
      age={props.age}
      owner={props.owner}
      gender={props.gender}/>
  )
}

const accident_que = (props) => {
  let isCompleted = props.progress > 2
  return (
    <AccidentQue
      key={3}
      showForm={props.showForm}
      isCompleted={isCompleted}/>
  )
}

const accident_ans = (props) => {
  return (
    <AccidentAns
      key={4}
      gender={props.gender}
      owner={props.owner}
      marriage={props.marriage}
      annual_revenue_family={props.annual_revenue_family}
      annual_revenue_personal={props.annual_revenue_personal}
      resident={props.resident}/>
  )
}

const accident_res = (props) => {
  return (
    <AccidentRes
      key={5}
      owner={props.owner}
      gender={props.gender}
      resident={props.resident}
      marriage={props.marriage}
      annual_revenue_personal={props.annual_revenue_personal}
      annual_revenue_family={props.annual_revenue_family}
      errors={props.errors}
      accident_coverage={props.accident_coverage}/>
  )
}

const ci_que = (props) => {
  let isCompleted = props.progress > 3
  return (
    <CIQue
      key={6}
      isCompleted={isCompleted}
      owner={props.owner}
      gender={props.gender}
      showForm={props.showForm}/>
  )
}

const ci_ans = (props) => {
  return (
    <CIAns
      key={7}
      has_social_security={props.has_social_security}
      has_complementary_medicine={props.has_complementary_medicine}
      owner={props.owner}
      gender={props.gender}/>
  )
}

const ci_res = (props) => {
  return (
    <CIRes
      key={8}
      has_social_security={props.has_social_security}
      has_complementary_medicine={props.has_complementary_medicine}
      owner={props.owner}
      gender={props.gender}
      age={props.age}
      annual_revenue_personal={props.annual_revenue_personal}
      ci_period={props.ci_period}
      ci_coverage={props.ci_coverage}
      ci_coverage_with_social_security={props.ci_coverage_with_social_security}/>
  )
}

const life_que = (props) => {
  let isCompleted = props.progress > 4
  return (
    <LifeQue
      key={9}
      isCompleted={isCompleted}
      owner={props.owner}
      gender={props.gender}
      showForm={props.showForm}/>
  )
}

const life_ans = (props) => {
  return (
    <LifeAns
      key={10}
      owner={props.owner}
      gender={props.gender}
      family_duty={props.family_duty}/>
  )
}

const life_res = (props) => {
  let isCompleted = props.progress > 5
  return (
    <LifeRes
      key={11}
      owner={props.owner}
      gender={props.gender}
      marriage={props.marriage}
      family_duty={props.family_duty}
      annual_revenue_family={props.annual_revenue_family}
      annual_revenue_personal={props.annual_revenue_personal}
      isCompleted={isCompleted}
      showForm={props.showForm}/>
  )
}

const life_complement_ans = (props) => {
  return (
    <LifeComplementAns
      key={12}
      owner={props.owner}
      gender={props.gender}
      marriage={props.marriage}
      asset={props.asset}
      family_duty={props.family_duty}
      older_duty={props.older_duty}
      spouse_duty={props.spouse_duty}
      child_duty={props.child_duty}
      loan_duty={props.loan_duty}/>
  )
}

const life_complement_res = (props) => {
  let isCompleted = props.progress > 5
  return (
    <LifeComplementRes
      key={13}
      owner={props.owner}
      gender={props.gender}
      age={props.age}
      marriage={props.marriage}
      asset={props.asset}
      annual_revenue_family={props.annual_revenue_family}
      family_duty={props.family_duty}
      older_duty={props.older_duty}
      spouse_duty={props.spouse_duty}
      child_duty={props.child_duty}
      loan_duty={props.loan_duty}
      isCompleted={isCompleted}
      showForm={props.showForm}
      life_coverage={props.life_coverage}
      life_period={props.life_period}
      max_duty_time={props.max_duty_time}
    />
  )
}
const annual_premium_que = (props) => {
  let isCompleted = props.progress > 6
  return (
    <AnnualPremiumQue
      key={14}
      marriage={props.marriage}
      isCompleted={isCompleted}
      showForm={props.showForm}/>
  )
}

const annual_premium_ans = (props) => {
  return (
    <AnnualPremiumAns
      key={15}
      ins_premium_up={props.ins_premium_up}
      ins_premium_least={props.ins_premium_least}
      annual_premium={props.annual_premium}/>
  )
}

const annual_premium_res = (props) => {
  return (
    <AnnualPremiumRes
      key={16}
      marriage={props.marriage}
      annual_premium={props.annual_premium}
      annual_revenue_personal={props.annual_revenue_personal}
      annual_revenue_family={props.annual_revenue_family}
      ins_premium_up={props.ins_premium_up}
      ins_premium_least={props.ins_premium_least}/>
  )
}

const end = (props) => {
  return (
    <End
      key={17}
      is_login={props.is_login}
    />
  )
}

const MODS = {
  foundation_que,
  foundation_ans,
  foundation_res,
  accident_que,
  accident_ans,
  accident_res,
  ci_que,
  ci_ans,
  ci_res,
  life_que,
  life_ans,
  life_res,
  life_complement_ans,
  life_complement_res,
  annual_premium_que,
  annual_premium_ans,
  annual_premium_res,
  end
}

export default MODS

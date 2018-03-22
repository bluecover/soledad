function validateRevenue(state) {
  let adult_info = state
  let arp = adult_info.annual_revenue_personal || {}
  let arf = adult_info.annual_revenue_family || {}

  let should_valid = _shouldValidRevenue(arp.error, arf.error)

  let arp_value = Number(arp.value || 0)
  let arf_value = Number(arf.value || 0)
  let error

  if (should_valid && arp_value > arf_value) {
    error = '个人收入应小于家庭收入'
  } else {
    error = null
  }

  return {
    ...state,
    annual_revenue: {
      error
    }
  }
}

function _shouldValidRevenue(arp_error, arf_error) {
  let should_valid = (arp_error === null && arf_error === null)

  return should_valid
}

export default validateRevenue

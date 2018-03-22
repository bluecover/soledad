export default function (num) {
  let res = num.toString().match(/^\d+(?:\.\d{0,2})?/)
  let floor_two_decimal = res && res[0]
  return Number(floor_two_decimal)
}

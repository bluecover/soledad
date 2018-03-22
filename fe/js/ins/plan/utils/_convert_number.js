export default function (num) {
  return num >= 10000 ? Number((num / 10000).toFixed(2)) + ' 万' : num + ' '
}

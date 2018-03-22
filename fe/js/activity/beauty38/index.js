import PhoneForm from 'mods/_phone_form.jsx'
import GH_APP from 'mods/global/gh_app.js'

let phoneForm = document.getElementById('phone_form')
let actionUrl = phoneForm.getAttribute('data-action')

ReactDOM.render(<PhoneForm actionUrl={actionUrl} />, phoneForm)

GH_APP.shareInfo = {
  title: '女王节快乐',
  content: '女王节送礼券,快来参加吧！',
  url: window.location.href,
  imgUrl: 'https://dn-ghimg.qbox.me/6WFBvKmncto4dqIi',
  buttonEnable: true
}

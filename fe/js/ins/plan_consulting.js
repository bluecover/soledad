import { Provider } from 'react-redux'

import store from './plan/_store'
import App from './plan/_app.jsx'
import StartFormContainer from './plan/containers/_start_form_container.jsx'
import SurveyFormsContainer from './plan/containers/_forms_container.jsx'

import getScrollBottom from 'utils/get_scroll_bottom'

ReactDOM.render(
  <Provider store={store}>
    <App />
  </Provider>,
  document.getElementById('ins_plan_consulting')
)

ReactDOM.render(
  <Provider store={store}>
    <StartFormContainer />
  </Provider>,
  document.getElementById('ins_start_forms')
)

ReactDOM.render(
  <Provider store={store}>
    <SurveyFormsContainer />
  </Provider>,
  document.getElementById('ins_survey_forms')
)

let $msg_tip = $('.js-ins-msg-tip')
$(window).on('scroll.ins_plan_tip', () => {
  if (getScrollBottom() < 30) {
    $msg_tip.hide()
  }
})

// wechat share
var config = $('#wx_config').data('val')
var url = window.location.href
var desc = {
  link: url,
  desc: '只需10分钟，量身定制专业保险规划',
  imgUrl: 'https://dn-ghimg.qbox.me/LwRqg9xc86vpwqW7'
}

wx.config(config)
wx.ready(function () {
  wx.onMenuShareAppMessage(desc)
  wx.onMenuShareTimeline(desc)
  wx.onMenuShareQQ(desc)
})

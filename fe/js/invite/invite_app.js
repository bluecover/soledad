let $btn_invite = $('.js-btn-invite')
let agent_ios_app = $btn_invite.data('agent-ios-app')
let agent_android_app = $btn_invite.data('agent-android-app')
let invite_url = $btn_invite.data('invite-url')
let invite_href = 'guihua://invite/app/share'

let share_data = {
  'title': '送你115元大礼包，和我一起攒钱吧！',
  'content': '我一直在用好规划攒钱助手，安全赚收益，你也来试试吧！',
  'inviteURL': invite_url,
  'imgURL': 'https://dn-ghimg.qbox.me/6WFBvKmncto4dqIi'
}

agent_ios_app ? share_data.inviteURL += '&dcm=app&dcs=ios' : null
agent_android_app ? share_data.inviteURL += '&dcm=app&dcs=android' : null

invite_href += '?' + decodeURIComponent(encodeURIComponent($.param(share_data)))

$btn_invite.attr('href', invite_href)

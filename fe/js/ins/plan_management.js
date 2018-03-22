const dlg_error = require('g-error')
const tmpl_planner = require('./mods/_planner.hbs')
const dlg_confirm = require('mods/modal/modal_confirm')

const MAX_PLANNING_NUM = 2

let $mod_add_planner = $('.js-m-add-planner')
let $ins_plan_list = $('.js-ins-plan-list')
let planning_num = $('.js-m-planner').length

const dlg_confirm_options = {
  title: '确定删除配偶？',
  content: '所有相关数据都将清除！'
}

// 添加规划书
$('.js-add-planner').on('click', () => {
  let params = {
    owner: '配偶'
  }

  $.ajax({
    url: '/j/ins/plan/add_planning',
    type: 'POST',
    data: params,
    dataType: 'json'
  }).done((planner) => {
    planner.avatar = setAvatar(planner.gender)
    planner = {
      ...params,
      ...planner
    }
    if (planner.owner === '自己') {
      planner.owner = '我'
    }

    $ins_plan_list.append(tmpl_planner(planner))
    planning_num += 1
    toggleAddPlannerBtn(planning_num < MAX_PLANNING_NUM)
  }).fail((res) => {
    dlg_error.show(res && res.responseJSON && res.responseJSON.error)
  })
})

// 删除规划书
$('.js-ins-plan-list').on('click', '.btn-del', (e) => {
  let $planner = $(e.target).closest('.js-m-planner')
  dlg_confirm_options.handleConfirm = getDelPlanner($planner)
  dlg_confirm.show(dlg_confirm_options)
})

function getDelPlanner($ele) {
  return () => {
    let params = {
      id: $ele.data('id')
    }

    $.ajax({
      url: '/j/ins/plan/delete_planning',
      type: 'POST',
      data: params
    }).done(() => {
      $ele.remove()
      planning_num -= 1
      toggleAddPlannerBtn(true)
    }).fail((res) => {
      dlg_error.show(res && res.responseJSON && res.responseJSON.error)
    })
  }
}

function setAvatar(gender) {
  if (gender === '女性') {
    return '<img src="{{{img/ins/plan/female_color.png}}}" alt="头像">'
  }

  return '<img src="{{{img/ins/plan/male_color.png}}}" alt="头像">'
}

function toggleAddPlannerBtn(show) {
  if (show) {
    $mod_add_planner.removeClass('hide')
  } else {
    $mod_add_planner.addClass('hide')
  }
}

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

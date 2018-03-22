var has = require('lodash/object/has')
var tmpl = require('./_fund_product.hbs')
var dlg_error = require('g-error')

module.exports = {
  reload: function () {
    $.ajax({
      url: '/j/fund/income_user_chart2',
      type: 'get'
    }).done(function (c) {
      if (c.info.length === 0) {
        return
      }

      $('.js-unfollow-wrapper,.js-chart-pic').addClass('hide')
      $('.js-follow-wrapper,.js-follow-chart').removeClass('hide')

      $.each(c.info, function (index, val) {
        var lately_income = '即将更新'
        var yesterday_income = '0.00'
        var like_date_str = val.like_date + '至今'
        if (val.group_income) {
          lately_income = (val.group_income * 100).toFixed(2) + '%'
          yesterday_income = (val.group_yesterday_income * 100).toFixed(2) + '%'
        }
        var default_opt = {
          product_subject: val.group_subject,
          group_yesterday_income: yesterday_income,
          group_lately_income: lately_income,
          like_date: like_date_str,
          group_article: val.group_article
        }
        var $tmpl = $(tmpl(default_opt))
        $('.js-product-main').append($tmpl)
        if (val.group_article && !(val.group_article_read === true)) {
          $tmpl.find('.js-tip-box').removeClass('hide')
        }
        if (val.group_income && val.group_income < 0) {
          $('.js-product-box').eq(index).find('.js-data-num').addClass('font-green')
        }
        if (c.info.length === 2) {
          $('.js-product-box').addClass('half')
        }
      })
      if ($.isEmptyObject(c.incomes)) {
        $('.js-follow-chart').addClass('hide')
        $('.js-chart-pic').removeClass('hide')
        $('.js-chart-box').addClass('short')
        return
      }

      var chart_data = getChartData(c)
      makeChart('follow_chart', chart_data[0], chart_data[1])
    }).fail(function () {
      dlg_error.show('获取信息失败，请重试')
    })
  }
}

function getChartData(c) {
  var datas = []
  var balloon = []
  var name_arr = ['theme', 'plan']

  $.each(c.incomes, function (key, value) {
    if (has(value, 1) && !has(value, 2)) {
      datas.push({
        date: key,
        theme: Number(Number(value[1] * 100).toFixed(2))
      })
    }
    if (has(value, 2) && !has(value, 1)) {
      datas.push({
        date: key,
        plan: Number(Number(value[2] * 100).toFixed(2))
      })
    }
    if (has(value, 2) && has(value, 1)) {
      datas.push({
        date: key,
        theme: Number(Number(value[1] * 100).toFixed(2)),
        plan: Number(Number(value[2] * 100).toFixed(2))
      })
    }
  })

  $.each(c.info, function (index, val) {
    balloon.push({
      'balloonText': val.group_subject + ': [[value]]%',
      'bullet': 'round',
      'title': val.group_subject,
      'valueField': name_arr[val.group_id - 1],
      'fillAlphas': 0
    })
  })
  return [datas, balloon]
}

function makeChart(ele, chart_data, balloon) {
  AmCharts.makeChart(ele, {
    'type': 'serial',
    'legend': {
      'useGraphSettings': true,
      'valueText': ''
    },
    'dataProvider': chart_data,
    'valueAxes': [{
      'integersOnly': true,
      'axisAlpha': 0,
      'dashLength': 5,
      'gridCount': 10,
      'position': 'left',
      'title': '收益率（％）'
    }],
    'graphs': balloon,
    'chartCursor': {
      'cursorAlpha': 0,
      'zoomable': false
    },
    'categoryField': 'date',
    'categoryAxis': {
      'gridPosition': 'start',
      'axisAlpha': 0,
      'fillAlpha': 0.05,
      'fillColor': '#000000',
      'gridAlpha': 0,
      'position': 'bottom'
    }
  })
}

var cloneDeep = require('lodash/lang/cloneDeep')

$('.js-plan-menu').click(function () {
  $('.js-plan-nav').slideToggle('fast')
})

function chap_2() {
  $('.balance-outcome-chart').each(function (index, pie) {
    var $pie = $(pie)
    var data = []

    $pie.find('.pie-bg').each(function (index, item) {
      var single = {}
      single.y = $(item).data('num') || 0
      single.color = $(item).data('color')
      data.push(single)

      $(item).css({
        background: single.color
      })
    })
    if ($('.pie-holder').length > 0) {
      new Highcharts.Chart({
        chart: {
          renderTo: $pie.find('.pie-holder')[0],
          plotBackgroundColor: null,
          plotBorderWidth: null,
          plotShadow: false
        },
        credits: {
          enabled: false
        },
        title: {
          text: ''
        },
        tooltip: {
          enabled: false
        },
        plotOptions: {
          pie: {
            allowPointSelect: false,
            cursor: 'pointer',
            dataLabels: {
              enabled: false
            },
            size: '100%',
            innerSize: '70%',
            showInLegend: false
          }
        },
        series: [{
          type: 'pie',
          name: 'percentage',
          data: data
        }]
      })
    }
  })

  var back = $('.bar-back-tip')
  back.each(function (index, item) {
    var $item = $(item)
    var front_height = $item.parent().find('.bar-line-content').height()
    var parent_height = $item.parent().height()
    var height = (parent_height - front_height) / 2
    $item.css('top', height)
  })

  var negtive_bars = $('.bar-line-content.negtive')
  negtive_bars.each(function (index, item) {
    var $item = $(item)
    var height = $item.height()
    $item.parents('.data-table').css('margin-bottom', height + 30)
  })
}

function chap_5() {
  var risk_data = ['很弱', '较弱', '中等', '较强', '很强']
  var risk_type_data = ['保守型', '稳健型', '平衡型', '进取型', '激进型']
  var percent_data = ['0%', '-5%', '-10%', '-15%', '-20%']
  var colors = ['#70C862', '#2CCEFC', '#727BC6', '#FFB56E', '#FF6752']
  var light_colors = ['#9fd292', '#82d4f3', '#989fcd', '#f9ca9c', '#f29488']
  var percent_type_data = cloneDeep(percent_data)
  var risk_charts_data = [risk_data, risk_type_data, percent_data, percent_type_data]
  risk_charts_data = risk_charts_data.map(function (n) {
    n = n.map(function (item) {
      var it = {}
      it.name = item
      it.color = '#CBCBCD'
      it.y = 20
      return it
    })
    return n
  })

  var risk_data1_on = $('.plan-risk-chart').data('rank') || 0
  risk_charts_data[0][risk_data1_on].color = colors[risk_data1_on]
  risk_charts_data[2][risk_data1_on].color = light_colors[risk_data1_on]

  var risk_data2_on = $('.plan-risk-type-chart').data('rank') || 0
  risk_charts_data[1][risk_data2_on].color = colors[risk_data2_on]
  risk_charts_data[3][risk_data2_on].color = light_colors[risk_data2_on]

  if ($('.plan-risk-chart').length > 0) {
    new Highcharts.Chart({
      chart: {
        renderTo: $('.plan-risk-chart')[0],
        type: 'pie',
        height: 700,
        marginTop: -200,
        plotBackgroundColor: null,
        plotBorderWidth: 0,
        plotShadow: false
      },
      credits: {
        enabled: false
      },
      title: {
        text: ''
      },
      plotOptions: {
        pie: {
          shadow: false,
          center: ['50%', '50%'],
          innerSize: '20%',
          startAngle: -90,
          endAngle: 90
        }
      },
      tooltip: {
        enabled: false
      },
      series: [{
        data: risk_charts_data[0],
        size: '75%',
        dataLabels: {
          format: '{point.name}',
          style: {
            fontWeight: 'bold',
            fontSize: '16px'
          },
          color: 'white',
          distance: -90
        }
      }, {
        data: risk_charts_data[2],
        size: '80%',
        innerSize: '65%',
        dataLabels: {
          format: '{point.name}',
          style: {
            fontWeight: 'bold',
            fontSize: '16px'
          },
          color: 'white',
          distance: -25
        }
      }]
    })
  }
  if ($('.plan-risk-type-chart').length > 0) {
    new Highcharts.Chart({
      chart: {
        renderTo: $('.plan-risk-type-chart')[0],
        type: 'pie',
        height: 700,
        marginTop: -200,
        plotBackgroundColor: null,
        plotBorderWidth: 0,
        plotShadow: false
      },
      credits: {
        enabled: false
      },
      title: {
        text: ''
      },
      plotOptions: {
        pie: {
          shadow: false,
          center: ['50%', '50%'],
          innerSize: '20%',
          startAngle: -90,
          endAngle: 90
        }
      },
      tooltip: {
        enabled: false
      },
      series: [{
        data: risk_charts_data[1],
        size: '75%',
        dataLabels: {
          format: '{point.name}',
          style: {
            fontWeight: 'bold',
            fontSize: '16px'
          },
          color: 'white',
          distance: -90
        }
      }, {
        data: risk_charts_data[3],
        size: '80%',
        innerSize: '65%',
        dataLabels: {
          format: '{point.name}',
          style: {
            fontWeight: 'bold',
            fontSize: '16px'
          },
          color: 'white',
          distance: -25
        }
      }]
    })
  }

}

function chap_6() {

  var data = []
  $('.deploy-value-chart').find('.pie-bg').each(function (index, item) {
    var single = {}
    single.y = $(item).data('num') || 0
    single.color = $(item).data('color')
    single.name = $(item).data('name')
    data.push(single)

    $(item).css({
      background: single.color
    })
  })
  if ($('.deploy-value-pieholder').length > 0) {
    new Highcharts.Chart({
      chart: {
        renderTo: $('.deploy-value-pieholder')[0],
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false
      },
      credits: {
        enabled: false
      },
      title: {
        text: ''
      },
      tooltip: {
        enabled: false
      },
      plotOptions: {
        pie: {
          allowPointSelect: false,
          cursor: 'pointer',
          dataLabels: {
            formatter: function () {
              return this.point.name + '<br>' + Highcharts.numberFormat(this.percentage, 0) + ' %'
            },
            style: {
              fontSize: '14px'
            },
            color: 'white',
            distance: -40
          },
          size: '100%',
          showInLegend: false
        }
      },
      series: [{
        type: 'pie',
        data: data
      }]
    })
  }

  var f_risk_gh = $('.fluctuation-risk-chart').data('guihua') || ''
  var f_risk_jj = $('.fluctuation-risk-chart').data('jijin') || ''
  var gh_data = f_risk_gh.split('|')
  gh_data = gh_data.map(function (item) {
    return parseFloat(item, 10)
  })
  var jj_data = f_risk_jj.split('|')
  jj_data = jj_data.map(function (item) {
    return parseFloat(item)
  })

  var fluctuation_risk_data = [{
    name: '好规划推荐方案',
    color: '#3669b3',
    data: gh_data
  }, {
    name: '激进投资方案（全部配置股票型基金）',
    color: '#cdcdcd',
    data: jj_data
  }]
  if ($('.fluctuation-risk-chart').length > 0) {
    new Highcharts.Chart({
      chart: {
        renderTo: $('.fluctuation-risk-chart')[0],
        type: 'line',
        marginTop: 35
      },
      credits: {
        enabled: false
      },
      title: {
        text: ''
      },
      xAxis: {
        categories: ['2010年', '2011年', '2012年', '2013年', '2014年1-6月']
      },
      yAxis: {
        title: {
          text: ''
        },
        labels: {
          formatter: function () {
            return this.value + '%'
          }
        }
      },
      plotOptions: {
        line: {
          dataLabels: {
            enabled: true,
            formatter: function () {
              return Highcharts.numberFormat(this.y, 2) + '%'
            }
          }
        },
        series: {
          lineWidth: 5
        }
      },
      tooltip: {
        formatter: function () {
          var format_name = this.series.name === '好规划推荐方案' ? '好规划推荐方案' : '激进投资方案'
          return '<b>' + this.x + '</b><br/>' +
            format_name + ': ' + Highcharts.numberFormat(this.y, 2) + '%'
        },
        valueSuffix: '%'
      },
      series: fluctuation_risk_data
    })
  }

  var predict_balance = $('.value-predict-chart').data('balance') || ''
  var predict_invest = $('.value-predict-chart').data('invest') || ''
  var predict_assets = $('.value-predict-chart').data('assets') || ''
  predict_balance = predict_balance.split('|')
  predict_invest = predict_invest.split('|')
  predict_assets = predict_assets.split('|')
  predict_balance = predict_balance.map(function (item) {
    return parseFloat(item)
  })
  predict_invest = predict_invest.map(function (item) {
    return parseFloat(item)
  })
  predict_assets = predict_assets.map(function (item) {
    return parseFloat(item)
  })
  var value_predict_data = [{
    name: '收支结余',
    color: '#FFB56E',
    data: predict_balance
  }, {
    name: '投资收益',
    color: '#70C862',
    data: predict_invest
  }, {
    name: '上年度可投资资产',
    color: '#727BC6',
    data: predict_assets
  }]
  if ($('.value-predict-chart').length > 0) {
    new Highcharts.Chart({
      chart: {
        renderTo: $('.value-predict-chart')[0],
        type: 'column'
      },
      credits: {
        enabled: false
      },
      title: {
        text: '资产增值预估表',
        margin: 30
      },
      xAxis: {
        categories: ['第一年', '第二年', '第三年', '第四年', '第五年']
      },
      yAxis: {
        min: 0,
        title: {
          text: ''
        },
        labels: {
          format: '{value}',
          formatter: function () {
            return this.value / 10000 + '万'
          }
        },
        stackLabels: {
          enabled: true,
          style: {
            fontWeight: 'bold',
            color: 'gray'
          }
        }
      },
      tooltip: {
        formatter: function () {
          return '<b>' + this.x + '</b><br/>' +
            this.series.name + ': ' + this.y + '<br/>' +
            '资产总值: ' + this.point.stackTotal
        }
      },
      plotOptions: {
        column: {
          stacking: 'normal',
          dataLabels: {
            enabled: true,
            color: 'white',
            style: {
              textShadow: '0 0 2px gray, 0 0 2px gray'
            }
          }
        }
      },
      series: value_predict_data
    })
  }
}

chap_2()
chap_5()
chap_6()

var predict_balance = $('.js-chart-target-column').data('balance') || ''
var predict_invest = $('.js-chart-target-column').data('invest') || ''
var predict_assets = $('.js-chart-target-column').data('assets') || ''
predict_balance = predict_balance.split('|')
predict_invest = predict_invest.split('|')
predict_assets = predict_assets.split('|')
predict_balance = predict_balance.map(function (item) { return parseFloat(item) })
predict_invest = predict_invest.map(function (item) { return parseFloat(item) })
predict_assets = predict_assets.map(function (item) { return parseFloat(item) })
var value_predict_data = [
  {name: '收支结余', color: '#ffa726', data: predict_balance},
  {name: '投资收益', color: '#9ccc65', data: predict_invest},
  {name: '上年度可投资资产', color: '#4e7da3', data: predict_assets}
]

new Highcharts.Chart({
  chart: {
    renderTo: $('.js-chart-target-column')[0],
    type: 'column'
  },
  credits: { enabled: false },
  title: false,
  xAxis: {
    categories: ['第一年', '第二年', '第三年', '第四年', '第五年']
  },
  yAxis: {
    min: 0,
    title: { text: '' },
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
        enabled: false
      }
    }
  },
  series: value_predict_data
})

var balance_ratio = $('.js-balance-chart-total').data('ratio') || 0
var balance_ratio_data = {
  name: '月结余',
  y: balance_ratio,
  color: '#26a69a'
}
var other_data = {
  name: 'other',
  y: 1 - balance_ratio,
  color: '#ddd'
}

if (balance_ratio > 0) {
  new Highcharts.Chart({
    chart: {
      renderTo: $('.js-balance-chart-total')[0],
      backgroundColor: '#f3f9ff',
      plotBackgroundColor: null,
      plotBorderWidth: null,
      margin: [0, 0, 0, 0],
      plotShadow: false
    },
    credits: { enabled: false },
    title: {
      text: ''
    },
    tooltip: {enabled: false},
    plotOptions: {
      pie: {
        allowPointSelect: false,
        cursor: 'default',
        showInLegend: false,
        dataLabels: {
          enabled: false
        },
        states: {
          hover: false
        }
      }
    },
    series: [{
      type: 'pie',
      data: [balance_ratio_data, other_data]
    }]
  })
}

var income = ['配偶月其他收入', '配偶月工资收入', '月其他收入', '月工资收入']
var outcome = ['餐饮娱乐', '交通通讯', '家居购物', '房租房贷', '其他支出']

var income_raw = $('.js-balance-chart').data('income').split(',')
var outcome_raw = $('.js-balance-chart').data('outcome').split(',')
var color = ['#cfd9db', '#26a69a', '#9ccc65', '#26c7d9', '#ffe0b2', '#5c4038', '#ffee58', '#8c6e63', '#ffa726']
var series_data = []

$.each(income, function (index, item) {
  var d = {
    'name': item,
    'data': [parseInt(income_raw[index], 10), 0],
    'color': color[index]
  }
  series_data.push(d)
})

$.each(outcome, function (index, item) {
  var d = {
    'name': item,
    'data': [0, parseInt(outcome_raw[index], 10)],
    'color': color[index + 4]
  }
  series_data.push(d)
})

new Highcharts.Chart({
  chart: {
    renderTo: $('.js-balance-chart')[0],
    type: 'bar'
  },
  credits: { enabled: false },
  title: '',
  xAxis: {
    categories: ['收入', '支出'],
    labels: {
      style: {
        fontSize: '14px',
        fontFamily: 'Microsoft YaHei, Helvetica'
      }
    },
    gridLineWidth: 0
  },
  yAxis: {
    title: '',
    gridLineWidth: 0,
    labels: {
      enabled: false
    }
  },
  legend: { enabled: false },
  tooltip: {
    formatter: function () {
      return this.series.name + ': ' + this.y
    }
  },
  plotOptions: {
    series: {
      stacking: 'normal'
    }
  },
  series: series_data
})

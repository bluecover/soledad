var moment = require('moment')

var annual_rates = $('.js-seven-chart').data('annual-rates')
var max_rate = -Infinity
var min_rate = Infinity

if (annual_rates) {
  annual_rates.map(function (arry) {
    arry[0] = moment.utc(arry[0], 'YYYY-MM-DD').valueOf()
    arry[1] < min_rate ? min_rate = arry[1] : null
    arry[1] > max_rate ? max_rate = arry[1] : null
  })
}

var seven_chart_dom = $('.js-seven-chart')[0]
if (seven_chart_dom) {

  new Highcharts.Chart({
    chart: {
      renderTo: seven_chart_dom,
      type: 'area'
    },
    credits: { enabled: false },
    legend: { enabled: false },
    title: {
      text: '七日年化收益率',
      floatting: true,
      align: 'left',
      style: {
        color: '#666',
        fontSize: '14px'
      },
      x: 0,
      y: 20
    },
    tooltip: {
      shadow: false,
      backgroundColor: '#6192b3',
      borderColor: '#6192b3',
      borderWidth: 1,
      borderRadius: 5,
      style: {
        color: '#fff'
      },
      formatter: function () {
        return moment(this.x).format('MM-DD') + '<br />' + this.y + '%'
      }
    },
    xAxis: {
      type: 'datatime',
      title: false,
      tickWidth: 0,
      lineWidth: 0,
      labels: {
        enabled: false
      }
    },
    yAxis: {
      title: false,
      gridLineWidth: 0,
      labels: {
        enabled: false
      },
      min: min_rate - (max_rate - min_rate),
      tickInterval: 0.01,
      max: max_rate
    },
    plotOptions: {
      area: {
        lineColor: '#6192b3',
        marker: {
          enabled: false,
          states: {
            hover: {
              fillColor: '#6192b3',
              lineColor: '#6192b3',
              lineWidthPlus: 1,
              radiusPlus: 1
            }
          }
        },
        fillOpacity: 0.7,
        fillColor: '#eee',
        threshold: -10
      }
    },
    series: [{
      data: annual_rates
    }]
  })
}

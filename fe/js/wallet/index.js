var moment = require('moment')

var annual_rates = $('.js-seven-chart').data('annual-rates')
var max_rate = -Infinity
var min_rate = Infinity
annual_rates.map(function (arry) {
  arry[0] = moment.utc(arry[0], 'YYYY-MM-DD').valueOf()
  arry[1] < min_rate ? min_rate = arry[1] : null
  arry[1] > max_rate ? max_rate = arry[1] : null
})

new Highcharts.Chart({
  chart: {
    renderTo: $('.js-seven-chart')[0],
    backgroundColor: '#fafafa',
    type: 'area',
    tickInterval: 0.01,
    events: {
      load: function () {
        var v = this.series[0].points[this.series[0].data.length - 1]
        this.tooltip.refresh(v)
      }
    }
  },
  credits: {
    enabled: false
  },
  legend: {
    enabled: false
  },
  title: {
    text: ''
  },
  tooltip: {
    shadow: false,
    backgroundColor: '#fb8c00',
    borderColor: '#fb8c00',
    borderWidth: 1,
    borderRadius: 5,
    followTouchMove: true,
    style: {
      color: '#fff'
    },
    formatter: function () {
      return moment(this.x).format('MM-DD') + '<br />' + this.y + '%'
    }
  },
  xAxis: {
    type: 'datetime',
    title: false,
    lineWidth: 1,
    tickWidth: 1,
    labels: {
      formatter: function () {
        return moment(this.value).format('MM-DD')
      }
    }
  },
  yAxis: {
    title: false,
    gridLineDashStyle: 'longdash',
    labels: {
      enabled: true,
      formatter: function () {
        return this.value + '%'
      }
    },
    min: min_rate - (max_rate - min_rate),
    max: max_rate
  },
  plotOptions: {
    area: {
      lineColor: '#fb8c00',
      marker: {
        enabled: false,
        states: {
          hover: {
            fillColor: '#fb8c00',
            lineColor: '#fb8c00',
            lineWidthPlus: 1,
            radiusPlus: 1
          }
        }
      },
      fillOpacity: 0.7,
      fillColor: '#f5f5f5',
      threshold: -10
    }
  },
  series: [{
    data: annual_rates
  }]
})

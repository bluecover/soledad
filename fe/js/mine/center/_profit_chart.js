var series_data = $('.js-profit-chart').data('amount')
var series_categories = $('.js-profit-chart').data('date')
var profit_chart_dom = $('.js-profit-chart')[0]

if (profit_chart_dom) {
  series_data = series_data.map(function (item) {
    var d = {
      color: '#6192b3',
      y: item
    }
    return d
  })

  if (series_data.length) {
    series_data[series_data.length - 1].color = '#6192b3'
  }

  new Highcharts.Chart({
    chart: {
      renderTo: profit_chart_dom,
      type: 'column',
      height: '166'
    },
    credits: { enabled: false },
    title: false,
    xAxis: {
      categories: series_categories,
      tickWidth: 0
    },
    yAxis: {
      title: false,
      gridLineDashStyle: 'longdash'
    },
    tooltip: {
      formatter: function () {
        return this.series.name + ': ' + this.y + '元'
      }
    },
    legend: { enabled: false },
    plotOptions: {
      column: {
        pointPadding: 0.2,
        borderWidth: 0
      }
    },
    series: [{
      name: '收益',
      data: series_data
    }]
  })

}

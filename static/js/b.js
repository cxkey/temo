
$(document).ready(function(e) {
    // 基于准备好的dom，初始化echarts实例
    var myChart = echarts.init(document.getElementById('main'));

    //// 指定图表的配置项和数据
    //var option = {
    //    title: {
    //        text: 'ECharts 入门示例'
    //    },
    //    tooltip: {},
    //    legend: {
    //        data:['销量']
    //    },
    //    xAxis: {
    //        data: ["衬衫","羊毛衫","雪纺衫","裤子","高跟鞋","袜子"]
    //    },
    //    yAxis: {},
    //    series: [{
    //        name: '销量',
    //        type: 'bar',
    //        data: [5, 20, 36, 10, 10, 20]
    //    }]
    //};

    var option = {
        title: {
            text: '总资产变化明细',
        },
        legend: {},
        tooltip : {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                label: {
                    backgroundColor: '#6a7985'
                }
            }
        },
        toolbox: {
            feature: { saveAsImage: {} }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                //data : ['周一','周二','周三','周四','周五','周六','周日']
                //data : ['1']
            }
        ],
        yAxis : [ { type : 'value' } ],
        series : [ ]
    };

    //// 使用刚指定的配置项和数据显示图表。
    myChart.setOption(option);

    var get_stat = function() {
        var stat_result = "#stat_result"
        $.ajax({  
            type: "get",  
            url: "/api/v1/statistics",
            //data: {'price': price, 'istype': istype},
            dataType: 'json',  
            contentType: "application/x-www-form-urlencoded; charset=utf-8",  
            beforeSend: function() { 
                return true;
            },
            success: function(d) { 
                //alert(JSON.stringify(d));
                //$(stat_result).html("<span style='color:red'>返回数据:" + JSON.stringify(d) + "</span>");
                if (d.result) {
                    myChart.hideLoading();
                    var dataset = d.info.dataset;
                    var series = []
                    for(var i=0; i<dataset.dimensions.length-1; i++) {
                        series.push({type: 'line',});
                    }
                    var option = {
                        dataset: dataset,
                        series: series,
                    }
                    console.log(option);
                    myChart.setOption(option);
                } else {
                }
            },
            error: function() {
                $(stat_result).html("<span style='color:red'>出错了</span>");
                return true;
            },
            complete: function() {
            }
        });  
    }
    get_stat();

    setInterval(function () {
        myChart.showLoading();
        get_stat();
    }, 5000);
});



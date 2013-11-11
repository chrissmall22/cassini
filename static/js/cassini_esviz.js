var now = new Date().getTime();
var data_size = 501; 
var data1 = randomData(data_size, now);
var data2 = randomData(data_size, now);
var data3 = randomData(data_size, now);
var data4 = randomData(data_size, now);
        
var data1_trunc = randomData_const(data_size, now, 1);
var data2_trunc = randomData_trunc(data_size, now, 30);
var data3_trunc = randomData_trunc(data_size, now, 25);
     
        
//Random time series data generator
function randomData(data_size, final_time){
  return d3.range(data_size).map(function(d,i){
    return {
              x:final_time - (data_size-i)*30000, //30 sec interval, time in seconds
              y:Math.random()*1000
            }
  })
}

function randomData_trunc(data_size, final_time, max){
  return d3.range(data_size).map(function(d,i){
    return {
              x:final_time - (data_size-i)*30000, //30 sec interval, time in seconds
              y:Math.round(Math.random()*1000 % max)
            }
  })
}

function randomData_const(data_size, final_time, c){
  return d3.range(data_size).map(function(d,i){
    return {
              x:final_time - (data_size-i)*30000, //30 sec interval, time in seconds
              y:c
            }
  })
}


d3.esnet.areachart().container("total_switches")
            .data([[data1_trunc]])
            .size({w:600, h:200})
            .margin({top:10, bottom:25, left:20, right:40})
            
d3.esnet.areachart().container("total_macs")
            .data([[data2_trunc]])
            .size({w:600, h:100})
            .margin({top:10, bottom:25, left:20, right:40})         

d3.esnet.areachart().container("total_users")
            .data([[data3_trunc]])
            .size({w:600, h:100})
            .margin({top:10, bottom:25, left:20, right:40})            
            
d3.esnet.areachart()
            .container("total_traffic")
            .data([[data1], [data3]])
            .size({w:600, h:200})
            .margin({top:10, bottom:25, left:20, right:40})
            .Tracker().Zoom()
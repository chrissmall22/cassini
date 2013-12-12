//////////////////////////////////////////
// Very flexible and easy to Areachart widget
//author : Gopal Vaswani (gvaswani@lbl.gov)
//Co-author: Jon Dugan (jdugan@lbl.gov)
// 
/////////////////////////////////////////




if (typeof d3.esnet != "object") d3.esnet = {};
d3.esnet.areachart = function (){
  
  var areachart = {},
  data= [[1,2],[2,1]],
  stacked = false,
  stack = d3.layout.stack().out(function out(d, y0, y){
      d.y0 = stacked ?  y0 : 0;
      d.y = y;
  }),
  m = {left:0, right:0, top:0, bottom:0},
  p = 0,
  h = 100, 
  w = 700,
  max,
  xscale,
  xpos,
  xpos_scale,
  initial_data_size,
  parent,
  color_mapping = [['#448fdd', '#a7cff9'],['#ff8a00','#ffc784']],
  yscale,
  yformat = d3.format(".2s"),
  xAxis = d3.svg.axis().ticks(10),
  yAxis = d3.svg.axis().orient("right").tickFormat(yformat).ticks(8),
  traker,
  index_position_mapping,
  extent;
  
  areachart.container = function(container){    
    //Container
    parent = d3.select("#"+container);
    parent.html(""); //clear anything inside the container div
    //SVG canvas
    parent.append("svg:svg")
      .append("svg:g")
        .attr("pointer-events", "all")
        .attr("class", "areagraph");
    
    parent.select(".areagraph").append("defs").append("clipPath")
        .attr("id", "clip")
      .append("rect")
    
    data.map(function(D,I){
      var klass = I===0? "up" : "down";
      parent.select(".areagraph").selectAll(klass)
        .data(D)
        .enter().append('svg:path')
          .attr("clip-path", "url(#clip)")
          .attr("class", klass)
          .attr("d", "M10 10") 
      })
      
    //Empty Gs for the axes
    parent.select(".areagraph").append("svg:g")
      .attr("class", "x axis")
      .attr("opacity", "0.7")
    parent.select(".areagraph").append("svg:g")
      .attr("class", "y axis")
      .attr("opacity", "0.7")
    
  
    parent.call(resize)
    return areachart;
  };
  
  areachart.size = function(S){
    if (!arguments.length) return {w:w + m.left + m.right + 2*p, h:h + m.top + m.bottom + 2*p};
    w = S.w; h = S.h;
    parent.call(resize);
    return rescale();
  }
  
  areachart.margin = function(M){
    if (!arguments.length) return m;
    //new margins
    if(M.left!=undefined) { m.left = M.left; }
    if(M.right!=undefined) { m.right = M.right; }
    if(M.top!=undefined) { m.top = M.top; }
    if(M.bottom!=undefined) { m.bottom = M.bottom; }
    
    parent.call(resize);
    return rescale();
  }
  
  areachart.data = function (D){
    if (!arguments.length) return data;
    
    data = D.map(function(d,i){ return stack(d); });
    max = d3.max(data.map(function(d,i){ 
      return d3.max(d3.merge(d).map(function(d,i){ 
        return Math.abs(d.y0 + d.y);
        }));
      }));
    if(data.length>1){
      data[1].map(function(bottomlayers, i){
        bottomlayers.map(function(d,i){ d.y0 = -d.y0;  d.y = -d.y;  return d;});
      });
    }
    initial_data_size = data[0][0].length;
    extent = [0,initial_data_size];
    index_position_mapping = d3.scale.linear().domain([0,w]).range(extent);
    return rescale();
  };
  //if we want to revisualize with default max (i.e. fixed scaling), the argument(mx) as false should be supplied.
  areachart.max = function(mx){
    if (!arguments.length) return max;
    if(mx){ 
      max = mx;
      }
    else{
      max = d3.max(data.map(function(d,i){ 
        return d3.max(d3.merge(d).map(function(d,i){ 
          return Math.abs(d.y0 + d.y);
          }));
        }));
    }
    return rescale();
  };
  
  areachart.stacked = function (bool){
    if (!arguments.length) return stacked;
	    stack.out(function out(d, y0, y) {
        d.y0 = bool ?  y0 : 0; //depenending on whether stack is needed or not
        d.y = y;
      })
  	data = data.map(function(d,i){ return stack(d); });
    max = d3.max(data.map(function(d,i){ 
      return d3.max(d3.merge(d).map(function(d,i){ 
        return Math.abs(d.y0 + d.y);
        }));
      }));
    return rescale();
  };
  
  
  /* X axis */
  areachart.xAxis = function(bool){
    if (!bool) {parent.call(resize); return areachart;}
    parent.call(resize);
    parent.select(".areagraph").select(".x.axis").call(x_axis);
    return areachart;
  };
  function x_axis(){
    xAxis.tickSize(-h).scale(xpos_scale);
    this.attr("transform", "translate(0" +  "," + h + ")")
    .call(xAxis).call(convert_to_date);
  }
  
  function convert_to_date (s){
    var txt = s.selectAll("g")
      .selectAll("text");
    txt.text("");
    txt.append("svg:tspan")
      .text(function(d,i){
        if(!data[0][0][d]){d=d-1;}
        return d3.time.format("%H:%M")(new Date(data[0][0][Math.round(d)].x)) 
        })
    txt.append("svg:tspan")
      .text(function(d,i){
        if(!data[0][0][d]){d=d-1;}
        return d3.time.format("%b %d")(new Date(data[0][0][Math.round(d)].x)) 
        })
      .attr("dy", 10).attr("dx", -30)
  }	  
  
  /* Y axis */
  areachart.yAxis = function(bool){
    if (!bool) {parent.call(resize); return areachart;}
    parent.call(resize);
    parent.select(".areagraph").select(".y.axis").call(y_axis);
    return areachart;
  };
  function y_axis(){
    yAxis.scale(yscale);
    this.attr("transform", "translate(" +  w + "," + "0)")
    .call(yAxis)
    .call(function(s){
       s.selectAll("g").selectAll("text").text(function(d,i){
         return yformat(Math.abs(d));
       })
    })
  }
  
  /*ZOOM*/
  areachart.Zoom = function(fun){
    var zoom = d3.behavior.zoom()
      .x(xpos_scale)
      //.y(yscale)
      .scaleExtent([1, 16])
      .on("zoom", function(){
        if(fun!=undefined){ fun(xpos_scale.domain()) }
        else{ onZoom(); }
        });
    parent.select(".areagraph").call(zoom);
    
    function onZoom(){
      var domain = xpos_scale.domain();
      if(domain[1]>initial_data_size){ domain[1]= initial_data_size;}
      if(domain[0]<3){domain[0]= 0;}
      update(domain);
      render_svg();
    }
    return areachart;
  };
  
  /*UPDATE*/
  areachart.update = function(dom){
    index_position_mapping.range(dom);
    xpos_scale.domain(dom);
    index_position_mapping.range(dom);
    return render_svg();
  };
  function update(dom){
    index_position_mapping.range(dom);
    xpos_scale.domain(dom);
    updateTracker();
  }
  
  /* TRACKER */
  areachart.Tracker = function(){
    tracker = parent.select(".areagraph").append('svg:g')
      .attr('class', 'tracker')
      .style('display', 'none');
  	
    tracker.append("svg:line")
      .attr("x1", 0).attr("y1", 0)
      .attr("x2", 0).attr("y2", h)
      .attr("stroke", "red");
    
    tracker.selectAll(".tracker_label")
      .data(data)
      .enter()
        .append("svg:text")
        .attr("class", "tracker_label")
        .attr("y", function(d,i){return i===0? 12 : h-3});
        
    parent.select(".areagraph").on("mousemove", function(){
      xpos = d3.svg.mouse(this)[0];
      //do not exceed the xposition more than graph width (for some reason)
      xpos = xpos > (w-1) ? (w-1) : xpos;
      var ypos = d3.svg.mouse(this)[1];
      updateTracker()
    });
    
    parent.select(".areagraph").on('mouseout', function(d){
      d3.selectAll(".tracker").style('display', 'none')
    });
    return areachart;
  };
  
  function updateTracker(){
    //var trackers = this.areagraph.selectAll(".tracker");
    var trackers = d3.selectAll(".tracker")
    var xindex = parseInt(index_position_mapping(xpos));
    trackers.style('display', 'block');

    trackers.each(function(d,i){
      d3.select(this).attr('transform', function(){
        return 'translate(' + xpos + ', 0)';
        });
      d3.select(this).selectAll('.tracker_label')
        .attr('x', function(d,i){return xpos > (w * 2/3) ? -5 : 5 ; })
        .attr('text-anchor', function(){ return xpos > (w * 2/3) ? 'end' : 'start'; })
        .text(function(d,i){
          return d.map(function(d,i){
            return d3.format(".3s")(Math.abs(d[xindex].y))
            }).join("  ");
        });
    })
  }
    
  /* RESIZE */
  function resize(s){
    //Container
    this
      .style("width", (w + m.left + m.right + 2*p) + "px")
      .style("height", (h + m.top + m.bottom + 2*p) + "px");
    
    //SVG canvas
    this.select("svg")
      .attr("width", (w + m.left + m.right + 2*p) + "px")
      .attr("height", (h + m.top + m.bottom + 2*p) + "px")
      .select(".areagraph")
        .attr("transform", "translate(" + (m.left + p) + "," + (m.top + p) + ")")
    
    this.select("#clip").select("rect")
      .attr("width", w)
      .attr("height", h);

    return areachart;
  }
  
  /* rescale primarily due to size or margin changes.*/
  function rescale(){    
    //xscale
    var sdate =  new Date(data[0][0].x);
    var edate =  new Date(data[0][0][data[0].length-1].x);
    xscale = d3.time.scale().domain([sdate, edate]).range([0, w]);
    //xpos_scale
    xpos_scale = d3.scale.linear().domain([0, data[0][0].length]).range([0, w]);
    yscale = d3.scale.linear();
    //yscale (If top and bottom(i.e data.length>1): modify the scale and bottom layers data)
    yscale = data.length>1 ? yscale.domain([max, 0, -max]).range([0, h/2, h]) : yscale.domain([max,0]).range([0, h]);
    index_position_mapping.domain([0,w]).range(extent);
    
    //resize the traker
    parent.select(".areagraph").selectAll(".tracker").select("line").attr("y2", h)
    parent.select(".areagraph").selectAll(".tracker_label").attr("y", function(d,i){return i===0? 12 : h-3});
    
    return render_svg();
  }
  
  function render_svg(){
    //Area generator
    var area = d3.svg.area()
      //.x(function(d,i) { return that.cfg.xscale(new Date(parseInt(d.x))); })
      .x(function(d,i) { return xpos_scale(i); })
      .y0(function(d) { return yscale(d.y0); })
      .y1(function(d) { return yscale(d.y+d.y0); })
      .interpolate("step-after");

    data.map(function(D,I){
      var klass = I===0? "up" : "down";
      parent.selectAll("path." + klass)
        .data(D)
          .attr("d", area)
          .style("fill", function(d,i) {return color_mapping[I][i];});
      })
    parent.select(".areagraph").select(".x.axis").call(x_axis);
    parent.select(".areagraph").select(".y.axis").call(y_axis);
      
    return areachart;
  }
  
  return areachart;
}

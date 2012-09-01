$(function() {
  $('#left').load('left.cgi', fixLinks);
  $('#right').load('right.cgi', fixLinks);
});

var fixLinks = function () {
  $('#left .leftlink a').click(function(event){
    event.preventDefault();
    var target = $(this).prop('target');
    if(!target) { target = 'left'; } 
    console.log(target);
    var href = $(this).prop('href');
    $( '#' + target ).load( href, fixLinks );
  });
  //$('#right a').click(function(event){
  //  event.preventDefault();
  //  var target = $(this).prop('target');
  //  if(!target) { target = 'right'; }
  //  var href = $(this).prop('href');
  //  $( '#' + target ).load( href, fixLinks );
  //});
};

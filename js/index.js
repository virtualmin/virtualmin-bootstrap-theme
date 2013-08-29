$(function() {
  $.get("/left.cgi", function(data) { handler(data, '/left.cgi', 'left') });
  //$('#left').load('/left.cgi');
  //$('#right').load('/right.cgi');
  $.get("/right.cgi", function(data) { handler(data, '/right.cgi', 'right') });

  // Attach events to a hrefs so they load in the right div (left or right)
  // .leftlink a, .mode a, .linkwithicon a
  $('#left').on("click", '.leftlink a, .mode a, .linkwithicon a', function(event){
    var target = $(this).prop('target');
    if(!target) { target = 'left'; } 
    var href = $(this).prop('href');
    console.log("target = ", target);
    $.get( href, function(data) { handler(data, href, target) });
    event.preventDefault();
  });
  // Attach events to hrefs so they load in the right div (mostly right),
  // without interfering with accordions, tabs, tables, etc.
  $('#right').on("click", '.accordion-inner a', function(event){
    var target = $(this).prop('target');
    if(!target) { target = 'right'; }
    var href = $(this).prop('href');
    console.log(href);
    $.get( href, function(data) { handler(data, href, target) });
    event.preventDefault();
  });
});

// handle modifying links, and attaching events
// href - The URL that was loaded that triggered the handler callback
// target = left or right (must be ID, as # will be appended
var handler = function (data, href, target) {
  // Insert data into div
  $( '#' + target ).html(data);

  console.log("href = ", href);
  // Convert relative URLs in #right to include directory
  var base_path = URI(href).directory();
  //var base_path = uri.directory() + '/';
  console.log(base_path);
  $('#right a:uri(is: relative)').each(function() {
    var cur_href = $(this).attr("href");
    $(this).attr("href", base_path+"/"+cur_href);
  });
};


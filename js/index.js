$(function() {
  $('#left').load('/left.cgi', null, handler() );
  $('#right').load('/right.cgi', null, handler() );

  // Attach events to a hrefs so they load in the right div (left or right)
  // .leftlink a, .mode a, .linkwithicon a
  $('#left').on("click", '.leftlink a, .mode a, .linkwithicon a', function(event){
    var target = $(this).prop('target');
    if(!target) { target = 'left'; } 
    var href = $(this).prop('href');
    console.log("target = ", target);
    $( '#' + target ).load( href, handler() );
    event.preventDefault();
  });
  // Attach events to a hrefs so they load in the right div (mostly right),
  // without interfering with accordions, tabs, tables, etc.
  $('#right').on("click", '.accordion-inner a', function(event){
    var target = $(this).prop('target');
    if(!target) { target = 'right'; }
    var href = $(this).prop('href');
    console.log(href);
    $( '#' + target ).load( href, handler() );
    event.preventDefault();
  });
});

// handle modifying links, and attaching events
// href - The URL that was loaded that triggered the handler callback
var handler = function (loaded_href) {
  // Convert relative URLs in #right to include directory
  if(loaded_href){
    var uri = $(loaded_href).uri();
    var base_path = uri.directory() + '/';
    $('#right a:uri(is: relative)').attr('href', basepath+$(this));
  }
};


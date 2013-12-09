(function () {
"use strict";

$(function() {
  $.get("/left.cgi", function(data) { loader(data, '/left.cgi', 'left'); });
  $.get("/right.cgi", function(data) { loader(data, '/right.cgi', 'right'); });

  // Print errors in a warning box in the right div
  $.ajaxSetup({
    error: function(xhr, status, error) {
      $('#right').prepend("<div class='alert alert-danger'>An AJAX error occured: " + status + "\nError: " + error + "</div>");
    }
  });

  // Attach events to left menu a hrefs
  // .leftlink a, .mode a, .linkwithicon a
  $('#left').on("click", '.leftlink a, .mode a, .linkwithicon a', function(event){
    var target = $(this).prop('target');
    if(!target) { target = 'left'; } 
    var href = $(this).prop('href');
    console.log("target = ", target);
    $.get( href, function(data) { loader(data, href, target); });
    event.preventDefault();
  });
  // Attach events to hrefs so they load in the right div (mostly right),
  // without interfering with accordions, tabs, tables, etc.
  $('#right').on("click", 'a.ui_link, .module-content .tab-content a, .panel-body a, .header a, .table a', function(event){
    var target = $(this).prop('target');
    if(!target) { target = 'right'; }
    var href = $(this).prop('href');
    console.log(href);
    $.get( href, function(data) { loader(data, href, target); });
    event.preventDefault();
  });

  //$('#right').on('submit', '.ui_form', function(event){
  $('.container-full').on('submit', '.ui_form, .navbar-form', function(event){
    var target = $(this).prop('target');
    if(!target) { target = 'right'; }
    if ( $(this).attr('enctype') == 'multipart/form-data' ) {
      var formData = new FormData($(this)[0]);
      $.ajax({
        processData: false,
        contentType: false,
        data: formData,
        type: $(this).attr('method'),
        url: $(this).attr('action'),
        success: function(response) {
          $('#' + target).html(response);
        }
      });
    } else {
      $.ajax({
        data: $(this).serialize(),
        type: $(this).attr('method'),
        url: $(this).attr('action'),
        success: function(response) {
          $('#' + target).html(response);
        }
      });
    }
    event.preventDefault();
  });
    
  // Attach events to navbar hrefs
  // .leftlink a, .mode a, .submit
  // XXX What about log out link? Needs to load into whole page..
  $('#topnav').on("click", '#mode a, .submit', function(event){
    var target = $(this).prop('target');
    //if(!target) { target = 'right'; }
    var href = $(this).prop('href');
    $(this).parent().parent().find('.active').removeClass('active');
    $(this).parent().addClass('active');
    $.get( href, function(data) { loader(data, href, target); });
    event.preventDefault();
  });

  // Dropdown menus in navbar
  $('#topnav').on("click", "#settings_drop a, #profile_drop a, #refresh", function(event){
    var target = $(this).prop('target');
    if(!target) { target = 'right'; }
    var href = $(this).prop('href');
    $.get( href, function(data) { loader(data, href, target); });
    event.preventDefault();
  });
});

// handle modifying links, and attaching events
// href - The URL that was loaded that triggered the handler callback
// target = left or right (must be ID, as # will be appended
var loader = function (data, href, target) {
  // Insert data into div
  $( '#' + target ).html(data);

  // Convert relative URLs in #right to include directory
  var base_path = URI(href).directory();

  //var base_path = uri.directory() + '/';
  //console.log(base_path);
  //$('#right .module-content a:uri(is: relative)').each(function() {
  //  var cur_href = $(this).attr("href");
  //  $(this).attr("href", base_path+"/"+cur_href);
  //});
};

}());

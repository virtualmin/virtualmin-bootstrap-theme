(function() {
    "use strict";

    $(function() {
        requestGet("/left.cgi", 'left');
        requestGet("/right.cgi", 'right');

        // Print errors in a warning box in the right div
        $.ajaxSetup({
            error: function(xhr, status, error) {
                $('#right').prepend("<div class='alert alert-danger'>An AJAX error occured: " + status + "\nError: " + error + "</div>");
                hideLoading('right');
                hideLoading('left');
            }
        });

        // Attach events to left menu a hrefs
        // .leftlink a, .mode a, .linkwithicon a
        $('#left').on("click", '.leftlink a, .mode a, .linkwithicon a', function(event) {
            var target = $(this).prop('target');
            var href = $(this).prop('href');
            requestGet(href, !target ? 'left' : target);
            event.preventDefault();
        });

        // Attach events to hrefs so they load in the right div (mostly right),
        // without interfering with accordions, tabs, tables, etc.
        $('#right').on("click", 'a:not([href^=""],[href^="mailto:"],[href^="#"])', function(event) {
            var target = $(this).prop('target');
            var href = $(this).prop('href');
            var onClick = $(this).attr('onclick');
            if ((href.indexOf('http') < 0 || href.indexOf(getCurrentDomain()) > -1) && (!onClick || onClick == "")) {
                requestGet(href, !target ? 'right' : target);
                event.preventDefault();
            }
        });

        // Form submit buttons
        //$('#right').on('submit', '.ui_form', function(event){
        $('.container-fluid').on('submit', '.ui_form, .navbar-form, .ui_buttons_form', function (event) {
            var target = !$(this).prop('target') ? 'right' : $(this).prop('target');
            showLoading(target);
            var href = $(this).attr('action');
            var method = $(this).attr('method');
            if ($(this).attr('enctype') == 'multipart/form-data') {
                var formData = new FormData($(this)[0]);
                $.ajax({
                    processData: false,
                    contentType: false,
                    data: formData,
                    type: method,
                    url: href,
                    success: function (response) {
                        if (target == 'right') {
                            changeRight(response, href);
                        } else {
                            changeLeft(response, href);
                        }
                    }
                });
            } else {
                $.ajax({
                    data: $(this).serialize(),
                    type: method,
                    url: href,
                    success: function (response) {
                        if (target == 'right') {
                            changeRight(response, href);
                        } else {
                            changeLeft(response, href);
                        }
                    }
                });
            }
            event.preventDefault();
        });

        // Config section select dropdown menu XXX make prev and next buts work.
        //$('#config_section').change(function() { XXX Why doesn't this work?
        $('#right').on('change', '#config_section', function(event) {
            $('#config_section_form').trigger('submit');
        });

        // Attach events to navbar hrefs
        // .leftlink a, .mode a, .submit
        $('#topnav').on("click", '#mode a, .submit', function(event) {
            var target = $(this).prop('target');
            var href = $(this).prop('href');
            $(this).parent().parent().find('.active').removeClass('active');
            $(this).parent().addClass('active');
            requestGet(href, target);
            event.preventDefault();
        });

        // Dropdown menus in navbar
        $('#topnav').on("click", "#settings_drop a, #profile_drop a, #refresh", function(event) {
            var target = $(this).prop('target');
            var href = $(this).prop('href');
            requestGet(href, !target ? 'right' : target);
            event.preventDefault();
        });
    });

    var requestGet = function (href, target) {
        showLoading(target);
        if (target == 'right') {
            $.get(href, function(data) { changeRight(data, href); });
        } else {
            $.get(href, function(data) { changeLeft(data, href); });
        }
    };

    var showLoading = function (target) {
        if ($('#' + target + ' .loading').is("*")) {
            $('#' + target + ' .loading').css({ 'display': 'block' });
        } else {
            $('#' + target).append('<div class="loading" style="display:block;"></div>');
        }
    };

    var hideLoading = function(target) {
        $('#' + target + ' .loading').css({ 'display': 'none' });
    };

    // Change right panel html
    // handle modifying links, and attaching events
    // href - The URL that was loaded that triggered the handler callback
    var changeRight = function (data, href) {
        href = fixHrefAddress(href);

        // Prevent bad HTML to break our function - Fix edit virtual server
        try {
            $('#right').html(data);
        } catch (e) { }

        // Hack to fix button table broken html - Fix edit virtual server
        $('#right .ui_buttons_table button[type=submit]').click(function (event) {
            if ($(this).parents("form").length == 0) {
                var form = $(this).closest('tr').prevAll('form').first();
                var input = $(this).closest('tr').prevAll('input[type=hidden]').first();
                if (!$.isEmptyObject(form)) {
                    if (!$.isEmptyObject(input)) {
                        form.append('<input type="hidden" name="' + input.attr('name') + '" value="' + input.attr('value') + '" />');
                    }
                    form.append('<input type="hidden" name="' + $(this).attr('name') + '" value="' + $(this).attr('value') + '" />');
                    form.submit();
                    event.preventDefault();
                }
            }
        });

        // Hack to fix submit button value when using ajax - Fix multiple submit button for same form
        $('#right form button[type=submit]').click(function (event) {
            var form = $(this).closest('form');
            form.append('<input type="hidden" name="' + $(this).attr('name') + '" value="' + $(this).attr('value') + '" />');
            form.submit();
            event.preventDefault();
        });

        // Hack to fix relative a urls - Fix back buttons
        $('#right a:not([href^="http"],[href^="https"],[href^=""],[href^="mailto:"],[href^="#"],[href^="/"],.ui_link)').each(function () {
            var lastIndex = href.lastIndexOf("/");
            if (lastIndex < 9) {
                href = href + '/';
                lastIndex = href.length;
            }
            $(this).attr('href', href.substring(0, lastIndex + 1) + $(this).attr('href'));
        });

        // Hack to fix relative form urls - Fix edit virtual server
        $('#right form:not([action^="http"],[action^="https"],[action^=""],[action^="/"])').each(function () {
            var lastIndex = href.lastIndexOf("/");
            if (lastIndex < 9) {
                href = href + '/';
                lastIndex = href.length;
            }
            $(this).attr('action', href.substring(0, lastIndex + 1) + $(this).attr('action'));
        });

    };

    // Change left panel html
    // handle modifying links, and attaching events
    // href - The URL that was loaded that triggered the handler callback
    var changeLeft = function (data, href) {
        href = fixHrefAddress(href);

        // Prevent bad HTML to break our function
        try {
            $('#left').html(data);
        } catch (e) { }

        // Hack to fix domain changer drop down menu
        $('.domainmenu select').removeAttr('onchange')
            .off('change')
            .change(
                function (event) {
                    var form = $(this).closest('form');
                    $.ajax({
                        processData: false,
                        contentType: false,
                        data: form.closest('form').serialize(),
                        type: form.closest('form').attr('method'),
                        url: form.closest('form').attr('action'),
                        success: function (response) {
                            changeLeft(response, form.closest('form').attr('action'));
                        }
                    });
                    var rightHref = "/virtual-server/summary_domain.cgi?dom=" + $(this).val();
                    requestGet(rightHref, 'right');
                    event.preventDefault();
                });
    };

    // Return current domain, cross browser version of window.location.origin
    var getCurrentDomain = function() {
        return window.location.protocol + "//" + window.location.host;
    };

    // Makes request URL absolute
    var fixHrefAddress = function (href) {
        var currentDomain = getCurrentDomain();
        if (href.indexOf('/') == 0) {
            href = currentDomain + href;
        }
        if (href.indexOf('://') == -1) {
            href = currentDomain + "/" + href;
        }
        return href;
    };
}());

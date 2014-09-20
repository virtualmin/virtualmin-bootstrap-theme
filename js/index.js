(function($) {
    "use strict";

    $(document).ready(function() {
        requestGet("/left.cgi", 'left');
        var uri = new URI();
        if (uri.fragment() != "") {
            var newUri = new URI(uri.fragment());
            requestGet(uri.pathname(newUri.pathname()).query(newUri.query()).hash('').toString(), 'right');
        } else {
            requestGet("/right.cgi", 'right');
        }
        

        // Attach events to left menu a hrefs
        // .leftlink a, .mode a, .linkwithicon a
        $('#leftContent').on("click", '.leftlink a, .mode a, .linkwithicon a', function(event) {
            var target = $(this).prop('target');
            var href = $(this).prop('href');
            requestGet(href, !target ? 'left' : target);
            event.preventDefault();
        });

        // Attach events to hrefs so they load in the right div (mostly right),
        // without interfering with accordions, tabs, tables, etc.
        $('#rightContent').on("click", 'a:not([href^=""],[href^="mailto:"],[href^="#"],[href^="javascript:"])', function (event) {
            var target = $(this).prop('target');
            var href = $(this).prop('href');
            var onClick = $(this).attr('onclick');
            if ((href.indexOf('http') < 0 || href.indexOf(getCurrentDomain()) > -1) && (!onClick || onClick == "")) {
                requestGet(href, !target ? 'right' : target);
                event.preventDefault();
            }
        });

        // Form submit buttons
        $('.container-fluid').on('submit', 'form', function(event) {
            var target = !$(this).prop('target') ? 'right' : $(this).prop('target');
            requestPost($(this), target);
            event.preventDefault();
        });

        // Config section select dropdown menu XXX make prev and next buts work.
        $('#rightContent').on('change', '#config_section', function () {
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
        $('#topnav').on("click", "#settings_drop a, #profile_drop a, #home", function(event) {
            var target = $(this).prop('target');
            var href = $(this).prop('href');
            requestGet(href, !target ? 'right' : target);
            event.preventDefault();
        });

        $(window).resize(function() {
            calculateColumnsSize();
        });
        calculateColumnsSize();

        $("#leftSide").mouseleave(function () {
            $("#leftSide .innerScroll").css({ 'padding-right': (getScrollBarWidth() + 10) + 'px', 'overflow': 'hidden' });
        });

        $("#leftSide").mouseenter(function () {
            $("#leftSide .innerScroll").css({ 'padding-right': '10px', 'overflow': 'auto' });
        });

        $("#leftSide").mouseleave();

        $(window).bind('popstate',
            function(event) {
                var state = event.originalEvent.state;
                if (state != null) {
                    if (state.type == 'get') {
                        requestGet(state.url, state.panel, true);
                    } else if (state.type == 'post') {
                        // We don't want user to accidentally send the data already posted by hitting back button
                        printError('As a security precaution, we will not resend posted data.');
                    }
                }
            });
    });

    // Set columns height to correct size
    var calculateColumnsSize = function() {
        $('.innerScroll').css(
            {
                'max-height': ($(window).height() - $('#topnav').height() - 40) + 'px',
                'min-height': ($(window).height() - $('#topnav').height() - 40) + 'px'
            }
        );
    };

    // Print errors in a warning box in the right div
    var printError = function(error) {
        $('#rightContent').prepend("<div class='alert alert-danger'>An AJAX error occured: " + error + "</div>");
    };

    // Send a GET request and update the panel
    var requestGet = function(href, target, noHistory) {
        showLoading(target);
        if (requestInProgress[target]) {
            return;
        }
        requestInProgress[target] = true;
        if (target == 'right' && !noHistory) {
            var uri = new URI(href);
            history.pushState({ type: 'get', url: href, panel: target }, document.title, (new URI()).query('').hash('').fragment(uri.pathname() + uri.search()));
        }
        $.ajax({
            url: href,
            success: function (response) {
                hideLoading(target);
                requestInProgress[target] = false;
                if (target == 'right') {
                    changeRight(response, href);
                } else {
                    changeLeft(response, href);
                }
            },
            error: function (xhr, status, error) {
                hideLoading(target);
                requestInProgress[target] = false;
                printError(error);
            }
        });
    };

    // Send a POST request for a form and update the panel
    var requestPost = function (form, target, noHistory) {
        showLoading(target);
        if (requestInProgress[target]) {
            return;
        }
        requestInProgress[target] = true;
        var href = form.attr('action');
        if (target == 'right' && !noHistory) {
            var uri = new URI(href);
            history.pushState({ type: 'post', url: href, panel: target }, document.title, (new URI()).query('').hash('').fragment(uri.pathname() + uri.search()));
        }
        var method = form.attr('method');
        if (form.attr('enctype') == 'multipart/form-data') {
            var formData = new FormData(form[0]);
            $.ajax({
                processData: false,
                contentType: false,
                data: formData,
                type: method,
                url: href,
                success: function (response) {
                    hideLoading(target);
                    requestInProgress[target] = false;
                    if (target == 'right') {
                        changeRight(response, href);
                    } else {
                        changeLeft(response, href);
                    }
                },
                error: function (xhr, status, error) {
                    hideLoading(target);
                    requestInProgress[target] = false;
                    printError(error);
                }
            });
        } else {
            $.ajax({
                data: form.serialize(),
                type: method,
                url: href,
                success: function (response) {
                    hideLoading(target);
                    requestInProgress[target] = false;
                    if (target == 'right') {
                        changeRight(response, href);
                    } else {
                        changeLeft(response, href);
                    }
                },
                error: function (xhr, status, error) {
                    hideLoading(target);
                    requestInProgress[target] = false;
                    printError(error);
                }
            });
        }
    };

    // Make loading hud visible on the desired panel
    var showLoading = function(target) {
        if (!$('#' + target + 'Side .loading').is("*")) {
            $('#' + target + 'Side').append('<div class="loading"></div>');
        }
        $('#' + target + 'Side .loading').fadeIn(200);
    };

    // Hide the loading hud - Currently only fires when an error occurred
    var hideLoading = function (target) {
        $('#' + target + 'Side .loading').fadeOut(200);
    };

    // Get scrollbar width
    var scrollWidthCache;
    function getScrollBarWidth() {
        if (scrollWidthCache === undefined) {
            var $outer = $('<div>').css({ visibility: 'hidden', width: 100, overflow: 'scroll' }).appendTo('body'),
                widthWithScroll = $('<div>').css({ width: '100%' }).appendTo($outer).outerWidth();
            $outer.remove();
            scrollWidthCache = 100 - widthWithScroll;
        }
        return scrollWidthCache;
    };

    // Change right panel html
    // handle modifying links, and attaching events
    // href - The URL that was loaded that triggered the handler callback
    var changeRight = function(data, href) {
        href = fixHrefAddress(href);

        // Hiding the old content
        $('#rightContent').fadeTo(200, 0.1, function () {
            // Prevent bad HTML to break our function - Fix edit virtual server
            try {
                $('#rightContent').html(data);
            } catch (e) {
            }

            // Hack to fix button table broken html - Fix edit virtual server
            $('#rightContent .ui_buttons_table button[type=submit]').click(function (event) {
                if ($(this).parents("form").length == 0) {
                    var form = $(this).closest('tr').prevAll('form').first();
                    var input = $(this).closest('tr').prevAll('input[type=hidden]').first();
                    if (form.is("*")) {
                        if (input.is("*")) {
                            form.append('<input type="hidden" name="' + input.attr('name') + '" value="' + input.attr('value') + '" />');
                        }
                        form.append('<input type="hidden" name="' + $(this).attr('name') + '" value="' + $(this).attr('value') + '" />');
                        form.submit();
                        event.preventDefault();
                    }
                }
            });

            // Hack to fix submit button value when using ajax - Fix multiple submit button for same form
            $('#rightContent form button[type=submit]').click(function (event) {
                if ($(this).parents("form").length > 0) {
                    var form = $(this).closest('form');
                    form.append('<input type="hidden" name="' + $(this).attr('name') + '" value="' + $(this).attr('value') + '" />');
                    form.submit();
                    event.preventDefault();
                }
            });

            // Hack to fix relative a urls - Fix back buttons
            $('#rightContent a:not([href^="http"], [href^="https"], [href^=""], [href^="mailto:"], [href^="#"], [href^="/"], [href^="javascript:"], .ui_link)').each(function () {
                var lastIndex = href.lastIndexOf("/");
                if (lastIndex < 9) {
                    href = href + '/';
                    lastIndex = href.length;
                }
                $(this).attr('href', href.substring(0, lastIndex + 1) + $(this).attr('href'));
            });

            // Hack to fix empty anchers
            $('#rightContent a[href^=""]').each(function () {
                $(this).attr('href', '/right.cgi');
            });

            // Hack to fix relative form urls - Fix edit virtual server
            $('#rightContent form:not([action^="http"], [action^="https"], [action^=""], [action^="/"])').each(function () {
                var lastIndex = href.lastIndexOf("/");
                if (lastIndex < 9) {
                    href = href + '/';
                    lastIndex = href.length;
                }
                $(this).attr('action', href.substring(0, lastIndex + 1) + $(this).attr('action'));
            });

            // We need to refresh left panel
            if (data.indexOf('top.left.location = top.left.location;') > -1 && lastLoadedUrlLeft != "") {
                requestGet(lastLoadedUrlLeft, 'left');
            }

            calculateColumnsSize();
            $("#rightSide .innerScroll").animate({ scrollTop: 0 }, "slow");
            $('#rightContent').fadeTo(200, 1);

            lastLoadedUrlRight = href;
        });
    };

    // A variable to prevent multiple request for one panel
    var requestInProgress = {
        "right": false,
        "left": false
    };

    // Last loaded url in left panel - GET or POST
    var lastLoadedUrlLeft = "";

    // Last loaded url in right panel - GET or POST
    var lastLoadedUrlRight = "";

    // Change left panel html
    // handle modifying links, and attaching events
    // href - The URL that was loaded that triggered the handler callback
    var changeLeft = function(data, href) {
        href = fixHrefAddress(href);

        // Hiding the old content
        $('#leftContent').fadeTo(200, 0.1, function () {
            // Prevent bad HTML to break our function
            try {
                $('#leftContent').html(data);
            } catch (e) {
            }

            // Hack to fix domain changer drop down menu
            $('.domainmenu select').removeAttr('onchange')
                .off('change')
                .change(
                    function(event) {
                        var form = $(this).closest('form');
                        requestPost(form, 'left');
                        var rightHref = "/virtual-server/summary_domain.cgi?dom=" + $(this).val();
                        requestGet(rightHref, 'right');
                        event.preventDefault();
                    });

            // We need to refresh right panel
            if (data.indexOf('top.right.location = top.right.location;') > -1 && lastLoadedUrlRight != "") {
                requestGet(lastLoadedUrlRight, 'right');
            }

            calculateColumnsSize();
            $("#leftSide .innerScroll").animate({ scrollTop: 0 }, "slow");
            $('#leftContent').fadeTo(200, 1);

            lastLoadedUrlLeft = href;
        });
    };

    // Return current domain, cross browser version of window.location.origin
    var getCurrentDomain = function() {
        return window.location.protocol + "//" + window.location.host;
    };

    // Makes request URL absolute
    var fixHrefAddress = function(href) {
        var currentDomain = getCurrentDomain();
        if (href.indexOf('/') == 0) {
            href = currentDomain + href;
        }
        if (href.indexOf('://') == -1) {
            href = currentDomain + "/" + href;
        }
        return href;
    };
}(jQuery));

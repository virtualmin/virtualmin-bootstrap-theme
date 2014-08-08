# Virtualmin Bootstrap Theme
# Icons copyright David Vignoni, all other theme elements copyright 2005-2013
# Virtualmin, Inc.

$main::cloudmin_no_create_links = 1;
$main::cloudmin_no_edit_buttons = 1;
$main::cloudmin_no_global_links = 1;

$main::mailbox_no_addressbook_button = 1;
$main::mailbox_no_folder_button = 1;

$main::basic_virtualmin_menu = 1;
$main::nocreate_virtualmin_menu = 1;
$main::nosingledomain_virtualmin_mode = 1;

# theme_header
sub theme_header
{
#return if ($main::done_webmin_header++);
my $ll;
print "<!DOCTYPE html>\n";
my $charset = defined($main::force_charset) ? $main::force_charset
                        : &get_charset();
$module_name = &get_module_name();
if (@_ > 0) {
    my $title = &get_html_title($_[0]);
	#print $_[7] if ($_[7]);
    print &get_html_status_line(0);
    }
my $dir = $current_lang_info->{'dir'} ? "dir=\"$current_lang_info->{'dir'}\""
                     : "";
#print "<div class='container'>\n";

if (@_ > 1) {
    my %this_module_info = &get_module_info(&get_module_name());
    print "<div class='header'><tr>\n";
    if ($gconfig{'sysinfo'} == 2 && $remote_user) {
		print "<div class='row'>\n";
        print "<div id='headln1' class='col-md-12'>\n";
        print &get_html_status_line(1);
        print "</div></div>\n";
        }
    	print "<div class='row'>\n";
    	# Title is just text
    	print "<div id='headln2l' class='col-md-8'><h2>",$_[0],"</h2>";
        print "<h4>$_[9]</h4>\n" if ($_[9]);
        print "</div>\n";
        }
    print "<div id='headln2r' class='col-md4 pull-right'>";
    if ($ENV{'HTTP_WEBMIN_SERVERS'} && !$tconfig{'framed'}) {
        print "<a href='$ENV{'HTTP_WEBMIN_SERVERS'}'>",
              "$text{'header_servers'}</a><br>\n";
        }
    if (!$_[5] && !$tconfig{'noindex'}) {
        my @avail = &get_available_module_infos(1);
        my $nolo = $ENV{'ANONYMOUS_USER'} ||
                  $ENV{'SSL_USER'} || $ENV{'LOCAL_USER'} ||
                  $ENV{'HTTP_USER_AGENT'} =~ /webmin/i;
        if ($gconfig{'gotoone'} && $main::session_id && @avail == 1 &&
            !$nolo) {
            print "<a href='$gconfig{'webprefix'}/session_login.cgi?logout=1'>",
                  "$text{'main_logout'}</a><br>";
            }
        elsif ($gconfig{'gotoone'} && @avail == 1 && !$nolo) {
            print "<a href=$gconfig{'webprefix'}/switch_user.cgi>",
                  "$text{'main_switch'}</a><br>";
            }
        elsif (!$gconfig{'gotoone'} || @avail > 1) {
            print "<a href='$gconfig{'webprefix'}/?cat=",
                  $this_module_info{'category'},
                  "'>$text{'header_webmin'}</a><br>\n";
            }
        }
    if (!$_[4] && !$tconfig{'nomoduleindex'}) {
        my $idx = $this_module_info{'index_link'};
        my $mi = $module_index_link || "/".&get_module_name()."/$idx";
        my $mt = $module_index_name || $text{'header_module'};
        print "<a href=\"$gconfig{'webprefix'}$mi\">$mt</a><br>\n";
        }
    if (ref($_[2]) eq "ARRAY" && !$ENV{'ANONYMOUS_USER'} &&
        !$tconfig{'nohelp'}) {
        print &hlink($text{'header_help'}, $_[2]->[0], $_[2]->[1]),
              "<br>\n";
        }
    elsif (defined($_[2]) && !$ENV{'ANONYMOUS_USER'} &&
           !$tconfig{'nohelp'}) {
        print &hlink($text{'header_help'}, $_[2]),"<br>\n";
        }
    if ($_[3]) {
        my %access = &get_module_acl();
        if (!$access{'noconfig'} && !$config{'noprefs'}) {
            my $cprog = $user_module_config_directory ?
                    "uconfig.cgi" : "config.cgi";
            print "<a href=\"$gconfig{'webprefix'}/$cprog?",
                  &get_module_name()."\">",
                  $text{'header_config'},"</a><br>\n";
            }
        }
	print "$_[6]\n" if ($_[6]);
    print "</div>\n";
    print "</div></div>\n"; # .header
	print "<div class='module-content'>\n"; # to allow selection of links
}

# theme_ui_post_header([subtext])
# Returns HTML to appear directly after a standard header() call
sub theme_ui_post_header
{
my ($text) = @_;
my $rv;
$rv .= "<div class='ui_post_header'>$text</div>\n" if (defined($text));
#$rv .= "<p>" if (!defined($text));
return $rv;
}

# theme_ui_pre_footer()
# Returns HTML to appear directly before a standard footer() call
sub theme_ui_pre_footer
{
my $rv;
$rv .= "</div>\n"; # .module-content
#$rv .= "</div>\n"; # .container-full?
$rv .= "</p>\n";
# XXX figure out where this ought to be... get rid of all the extras.
#$rv .= <<EOL;
#    <script src="/bootstrap/js/jquery-1.8.0.min.js"></script>
#    <script src="/bootstrap/js/bootstrap.js"></script>
#EOL
$rv .= "</body></html>\n";
return $rv;
}

# ui_print_footer(args...)
# Print HTML for a footer with the pre-footer line. Args are the same as those
# passed to footer()
sub theme_ui_print_footer
{
local @args = @_;
print &theme_ui_pre_footer();
&footer(@args);
}

sub theme_icons_table
{
my ($i, $need_tr);
my $cols = $_[3] ? $_[3] : 4;
my $per = int(100.0 / $cols);
print "<div class='panel panel-default'>\n";
print "<div class='panel-body'>\n";
print "<ul class='ui_icons_table'>\n";
for($i=0; $i<@{$_[0]}; $i++) {
	print "<li>\n";
	&generate_icon($_[2]->[$i], $_[1]->[$i], $_[0]->[$i],
		       $_[4], $_[5], $_[6], $_[7]->[$i], $_[8]->[$i]);
	print "</li>\n";
    }
print "</ul>\n" if ($need_tr);
print "</div>\n"; # .panel-body
print "</div>\n"; # .icons_table .panel-default
}

sub theme_generate_icon
{
my $w = !defined($_[4]) ? "width=48" : $_[4] ? "width=$_[4]" : "";
my $h = !defined($_[5]) ? "height=48" : $_[5] ? "height=$_[5]" : "";

print "<a href=\"/$module_name/$_[2]\" $_[3]>",
      "<div class='ui_icon'>\n",
	  "<img src=\"/$module_name/$_[0]\" alt=\"\" border=0 ",
      "$w $h></div><br>\n";
print "$_[1]</a>\n";
}

# theme_post_save_domain(&domain, action)
# Called by Virtualmin after a domain is updated, to refresh the left menu
sub theme_post_save_domain
{
my ($d, $action) = @_;
# Refresh left side, in case options have changed
print "<script>\n";
if ($action eq 'create') {
	# Select the new domain
	print "top.left.location = '$gconfig{'webprefix'}/left.cgi?dom=$d->{'id'}';\n";
	}
else {
	# Just refresh left
	print "top.left.location = top.left.location;\n";
	}
print "</script>\n";
}

# theme_post_save_domains([domain, action]+)
# Called after multiple domains are updated, to refresh the left menu
sub theme_post_save_domains
{
print "<script>\n";
print "top.left.location = top.left.location;\n";
print "</script>\n";
}

# theme_post_save_server(&server, action)
# Called by Cloudmin after a server is updated, to refresh the left menu
sub theme_post_save_server
{
my ($s, $action) = @_;
if ($action eq 'create' || $action eq 'delete' ||
    !$done_theme_post_save_server++) {
	print "<script>\n";
	print "top.left.location = top.left.location;\n";
	print "</script>\n";
	}
}

# theme_select_server(&server)
# Called by Cloudmin when a page for a server is displayed, to select it on the
# left menu.
sub theme_select_server
{
my ($server) = @_;
print <<EOF;
<script>
if (window.parent && window.parent.frames[0]) {
	var leftdoc = window.parent.frames[0].document;
	var leftform = leftdoc.forms[0];
	if (leftform) {
		var serversel = leftform['sid'];
		if (serversel && serversel.value != '$server->{'id'}' ||
		    !serversel) {
			//if (serversel) {
			//	// Need to change value of selector
			//	serversel.value = '$server->{'id'}';
			//	}
			window.parent.frames[0].location = '$gconfig{'webprefix'}/left.cgi?mode=vm2&sid=$server->{'id'}';
			}
		}
	}
</script>
EOF
}

sub theme_ui_link
{
my ($href, $text, $class) = @_;
return ("<a class='ui_link $class' href='".get_module_name."/$href'>$text</a>");
}

sub theme_ui_img
{
my ($src, $alt, $title, $class, $tags) = @_;
return ("<img src='".get_module_name."/".$src."' class='ui_img".($class ? " ".$class : "")."' alt='$alt' ".($title ? "title='$title'" : "").($tags ? " ".$tags : "").">");
}

sub theme_ui_form_columns_table
{
my ($cgi, $buttons, $selectall, $others, $hiddens,
       $heads, $width, $data, $types, $nosort, $title, $emptymsg, $formno) = @_;
my $rv;

# Build links
my @leftlinks = map { ui_link("$_->[0]", $_->[1]) }
               grep { $_->[2] ne 'right' } @$others;
my @rightlinks = map { ui_link("$_->[0]", $_->[1]) }
               grep { $_->[2] eq 'right' } @$others;
my $links;

# Add select links
if (@$data) {
    if ($selectall) {
        my $cbname;
        foreach my $r (@$data) {
            foreach my $c (@$r) {
                if (ref($c) && $c->{'type'} eq 'checkbox') {
                    $cbname = $c->{'name'};
                    last;
                    }
                }
            }
        if ($cbname) {
            unshift(@leftlinks, &select_all_link($cbname, $formno),
                    &select_invert_link($cbname, $formno));
            }
        }
    }

# Turn to HTML
if (@rightlinks) {
    $links = &ui_grid_table([ &ui_links_row(\@leftlinks),
                  &ui_links_row(\@rightlinks) ], 2, 100,
                    [ undef, "align=right" ]);
    }
elsif (@leftlinks) {
    $links = &ui_links_row(\@leftlinks);
    }

# Start the form, if we need one
if (@$data) {
    $rv .= &ui_form_start($cgi, "post");
    foreach my $h (@$hiddens) {
        $rv .= &ui_hidden(@$h);
        }
    $rv .= $links;
    }

# Add the table
$rv .= &ui_columns_table($heads, $width, $data, $types, $nosort, $title,
             $emptymsg);

# Add form end
$rv .= $links;
if (@$data) {
    $rv .= &ui_form_end($buttons);
    }

return $rv;
}

sub theme_ui_textbox
{
my ($name, $value, $size, $dis, $max, $tags) = @_;
$size = &ui_max_text_width($size);
return "<input type='text' class='form-control ui_textbox' name=\"".&quote_escape($name)."\" ".
       "value=\"".&quote_escape($value)."\" ".
       "size=$size ".($dis ? "disabled=true" : "").
       ($max ? " maxlength=$max" : "").
       " ".$tags.
       ">";
}

sub theme_ui_password
{
my ($name, $value, $size, $dis, $max, $tags) = @_;
$size = &ui_max_text_width($size);
return "<input class='form-control ui_password' ".
       "type=password name=\"".&quote_escape($name)."\" ".
       "value=\"".&quote_escape($value)."\" ".
       "size=$size ".($dis ? "disabled=true" : "").
       ($max ? " maxlength=$max" : "").
       " ".$tags.
       ">";
}

sub theme_ui_button
{
my ($label, $name, $dis, $tags) = @_;
return "<button type='button' class='btn btn-default".
       ($name ne '' ? " name=\"".&quote_escape($name)."\"" : "").
       " value=\"".&quote_escape($label)."\"".
       ($dis ? " disabled=true" : "").
       ($tags ? " ".$tags : "").">\n";
}

sub virtualmin_ui_show_cron_time
{
return &theme_virtualmin_ui_show_cron_time(@_)
    if (defined(&theme_virtualmin_ui_show_cron_time));
my ($name, $job, $offmsg) = @_;
&foreign_require("cron", "cron-lib.pl");
my $rv;
my $mode = !$job ? 0 : $job->{'special'} ? 1 : 2;
my $complex = $mode == 2 ? &cron::when_text($job, 1) : undef;
my $button = "<input type=button onClick='cfield = form.${name}_complex; hfield = form.${name}_hidden; chooser = window.open(\"cron_chooser.cgi?complex=\"+escape(hfield.value), \"cronchooser\", \"toolbar=no,menubar=no,scrollbars=no,resizable=yes,width=800,height=400\"); chooser.cfield = cfield; window.cfield = cfield; chooser.hfield = hfield; window.hfield = hfield;' value=\"...\">\n";
my $hidden = $mode == 2 ?
    join(" ", $job->{'mins'}, $job->{'hours'},
          $job->{'days'}, $job->{'months'}, $job->{'weekdays'}) : "";
return &ui_radio_table($name, $mode,
     [ $offmsg ? ( [ 0, $offmsg ] ) : ( ),
       $cron::config{'vixie_cron'} ? (
       [ 1, $text{'cron_special'},
           &ui_select($name."_special", $job->{'special'},
              [ map { [ $_, $cron::text{'edit_special_'.$_} ] }
                ('hourly', 'daily', 'weekly', 'monthly', 'yearly')
              ]) ] ) : ( ),
       [ 2, $text{'cron_complex'},
           &ui_textbox($name."_complex", $complex, 40, 0, undef,
                  "readonly=true")." ".$button ],
     ]).&ui_hidden($name."_hidden", $hidden);
}

# XXX UGLY! Needs to be updated to load into a popup within the page, so we
# have CSS and JavaScript available.
sub theme_virtualmin_ui_show_cron_time
{
my ($name, $job, $offmsg) = @_;
&foreign_require("cron", "cron-lib.pl");
my $rv;
my $mode = !$job ? 0 : $job->{'special'} ? 1 : 2;
my $complex = $mode == 2 ? &cron::when_text($job, 1) : undef;
my $button = "<button type='button' class='btn btn-default' onClick='cfield = form.${name}_complex; hfield = form.${name}_hidden; chooser = window.open(\"/virtual-server/cron_chooser.cgi?complex=\"+escape(hfield.value), \"cronchooser\", \"toolbar=no,menubar=no,scrollbars=no,resizable=yes,width=800,height=400\"); chooser.cfield = cfield; window.cfield = cfield; chooser.hfield = hfield; window.hfield = hfield;' value=\"...\"><span class='glyphicon glyphicon-time'></span></button>\n";
my $hidden = $mode == 2 ?
    join(" ", $job->{'mins'}, $job->{'hours'},
          $job->{'days'}, $job->{'months'}, $job->{'weekdays'}) : "";
return &ui_radio_table($name, $mode,
     [ $offmsg ? ( [ 0, $offmsg ] ) : ( ),
       $cron::config{'vixie_cron'} ? (
       [ 1, $text{'cron_special'},
           &ui_select($name."_special", $job->{'special'},
              [ map { [ $_, $cron::text{'edit_special_'.$_} ] }
                ('hourly', 'daily', 'weekly', 'monthly', 'yearly')
              ]) ] ) : ( ),
       [ 2, $text{'cron_complex'},
           &ui_textbox($name."_complex", $complex, 40, 0, undef,
                  "readonly=true")." ".$button ],
     ]).&ui_hidden($name."_hidden", $hidden);
}

# theme_select_domain(&domain)
# Called by Virtualmin when a page for a server is displayed, to select it on
# the left menu.
sub theme_select_domain
{
my ($d) = @_;
print <<EOF;
<script>
if (window.parent && window.parent.frames[0]) {
	var leftdoc = window.parent.frames[0].document;
	var leftform = leftdoc.forms[0];
	if (leftform) {
		var domsel = leftform['dom'];
		if (domsel && domsel.value != '$d->{'id'}') {
			// Need to change value
			// domsel.value = '$d->{'id'}';
			window.parent.frames[0].location = '$gconfig{'webprefix'}/left.cgi?mode=virtualmin&dom=$d->{'id'}';
			}
		}
	}
</script>
EOF
}

# theme_post_save_folder(&folder, action)
# Called after some folder is changed, to refresh the left frame. The action
# may be 'create', 'delete', 'modify' or 'read'
sub theme_post_save_folder
{
my ($folder, $action) = @_;
my $ref;
if ($action eq 'create' || $action eq 'delete' || $action eq 'modify') {
	# Always refresh
	$ref = 1;
	}
else {
	# Only refesh if showing unread count
	if (defined(&mailbox::should_show_unread) &&
	    &mailbox::should_show_unread($folder)) {
		$ref = 1;
		}
	}
if ($ref) {
	print "<script>\n";
	print "top.frames[0].document.location = top.frames[0].document.location;\n";
	print "</script>\n";
	}
}

sub theme_post_change_modules
{
print <<EOF;
<script>
var url = '' + top.left.location;
if (url.indexOf('mode=webmin') > 0) {
    top.left.location = url;
    }
</script>
EOF
}

sub theme_prebody
{
if ($script_name =~ /session_login.cgi/) {
	# Generate CSS link
#	print "<link rel='stylesheet' type='text/css' href='$gconfig{'webprefix'}/bootstrap/css/bootstrap.min.css'>\n";
#	print "<link rel='stylesheet' type='text/css' href='$gconfig{'webprefix'}/unauthenticated/virtual-server-style.css'>\n";
#	print "<link rel='stylesheet' type='text/css' href='$gconfig{'webprefix'}/css/webmin.css'>\n";
#	print "<!--[if IE]>\n";
#	print "<style type=\"text/css\">\n";
#	print "table.formsection, table.ui_table, table.loginform { border-collapse: collapse; }\n";
#	print "</style>\n";
#	print "<![endif]-->\n";
	}
if (get_module_name() eq "virtual-server") {
	# No need for Module Index link, as we have the left-side frame
	$tconfig{'nomoduleindex'} = 1;
	}
}

sub theme_prehead
{
	# Generate CSS link
#	print "<link rel='stylesheet' type='text/css' href='$gconfig{'webprefix'}/bootstrap/css/bootstrap.min.css'>\n";
#	print "<link rel='stylesheet' type='text/css' href='$gconfig{'webprefix'}/unauthenticated/virtual-server-style.css'>\n";
#	print "<link rel='stylesheet' type='text/css' href='$gconfig{'webprefix'}/css/webmin.css'>\n";
#	print "<!-- HTML5 shim, for IE6-8 support of HTML5 elements -->\n";
#	print "<!--[if lt IE 9]>]\n";
#	print "<script src='http://html5shim.googlecode.com/svn/trunk/html5.js\n'></script>\n";
#	print "<![endif]-->\n";
#print "<script>\n";
#print "var rowsel = new Array();\n";
#print "</script>\n";
#print "<script type='text/javascript' src='$gconfig{'webprefix'}/unauthenticated/sorttable.js'></script>\n";
#if ($ENV{'HTTP_USER_AGENT'} =~ /Chrome/) {
#	print "<style type=\"text/css\">\n";
#	print "textarea,pre { font-size:120%; }\n";
#	print "</style>\n";
#	}
}

sub theme_popup_prehead
{
return &theme_prehead();
}

# ui_table_start(heading, [tabletags], [cols], [&default-tds], [right-heading])
# A table with a heading and table inside
sub theme_ui_table_start
{
my ($heading, $tabletags, $cols, $tds, $rightheading) = @_;
if (! $tabletags =~ /width/) { $tabletages .= " width=100%"; }
if (defined($main::ui_table_cols)) {
  # Push on stack, for nested call
  push(@main::ui_table_cols_stack, $main::ui_table_cols);
  push(@main::ui_table_pos_stack, $main::ui_table_pos);
  push(@main::ui_table_default_tds_stack, $main::ui_table_default_tds);
  }
my $rv;
my $colspan = 1;

$rv .= "<div class='panel panel-default' $tabletags>\n";
if (defined($heading) || defined($rightheading)) {
		$rv .= "<div class='panel-heading'>\n";
        if (defined($heading)) {
                $rv .= "<h4>$heading</h4>"
                }
        if (defined($rightheading)) {
                $rv .= "<h4 class='pull-right'>$rightheading</h4>";
                $colspan++;
                }
		$rv .= "</div>\n";
        }
$rv .= "<div class='panel-body'>\n";
# XXX fixme see where cols makes a difference at this level and fix it somehow
$main::ui_table_cols = $cols || 4;
$main::ui_table_pos = 0;
$main::ui_table_default_tds = $tds;
return $rv;
}

# ui_table_row(label, value, [cols], [&td-tags])
# Returns HTML for a row in a table started by ui_table_start, with a 1-column
# label and 1+ column value.
sub theme_ui_table_row
{
my ($label, $value, $cols, $tds) = @_;
$cols ||= 1;
$tds ||= $main::ui_table_default_tds;
# Heuristically figure out the right grid layout...
# 4 cols with labels and values would be row, md-2, md-4, md-2, md-4, /row
# 1 cols with just a value would be 12
# 2 cols with label and value would be row, md-4, md-8, /row
# If tds has widths, we need to fit that into grid sizes, somehow.
# Bootstrap grid has 12 slots.
my $colwidth = 6; # XXX This is messy. I keep finding edge cases where fails.
if (defined ($label)) {
	$colwidth = 4;
}
if ($main::ui_table_cols == 4 && defined ($label)) {
	$colwidth = 2;
}
elsif ($main::ui_table_cols == 2) {
	$colwidth = 4;
}
elsif ($main::ui_table_cols == 1) {
	$colwidth = 12;
}

my $rv;
if ($main::ui_table_pos+$cols+1 > $main::ui_table_cols &&
    $main::ui_table_pos != 0) {
    # If the requested number of cols won't fit in the number
    # remaining, start a new row
    $rv .= "</div>\n";
    $main::ui_table_pos = 0;
    }

$rv .= "<div class='ui_form_pair row'>\n" if ($main::ui_table_pos%$main::ui_table_cols == 0);
if (defined($label)) {
	$rv .= "<div class='ui_form_label col-md-$colwidth'><p><strong>$label</strong></p></div>\n";
} 
$rv .= "<div class='ui_form_value col-md-" . $colwidth*2 . "'><p>$value</p></div>\n";
$main::ui_table_pos += $cols+(defined($label) ? 1 : 0);
if ($main::ui_table_pos%$main::ui_table_cols == 0) {
    $rv .= "</div>\n";
    $main::ui_table_pos = 0;
    }
return $rv;
}

# ui_table_end()
# The end of a table started by ui_table_start
sub theme_ui_table_end
{
my $rv;
if ($main::ui_table_cols == 4 && $main::ui_table_pos) {
  # Add an empty block to balance the table
  $rv .= &ui_table_row(" ", " ");
  }
if (@main::ui_table_cols_stack) {
  $main::ui_table_cols = pop(@main::ui_table_cols_stack);
  $main::ui_table_pos = pop(@main::ui_table_pos_stack);
  $main::ui_table_default_tds = pop(@main::ui_table_default_tds_stack);
  }
else {
  $main::ui_table_cols = undef;
  $main::ui_table_pos = undef;
  $main::ui_table_default_tds = undef;
  }
$rv .= "</div></div>\n";
return $rv;
}

# theme_ui_tabs_start(&tabs, name, selected, show-border)
# Render a row of tabs from which one can be selected. Each tab is an array
# ref containing a name, title and link.
sub theme_ui_tabs_start
{
my ($tabs, $name, $sel, $border) = @_;
my $rv;
$main::ui_tabs_selected = $sel;

print "<ul class='nav nav-tabs'>\n";
foreach my $t (@$tabs) {
	my $tabid = "tab_".$t->[0];
	my $defclass = $t->[0] eq $main::ui_tabs_selected ?
                        'active' : '';
	$rv .= "<li class='ui_tab $defclass'><a href='#$tabid' data-toggle='tab'>$t->[1]</a></li>\n";
}
$rv .= "</ul>\n<div class='tab-content'>\n";
return $rv;
}

sub theme_ui_tabs_start_tab
{
my ($name, $tab) = @_;
my $defclass = $tab eq $main::ui_tabs_selected ?
                        'active' : '';
my $rv = "<div id='tab_$tab' class='tab-pane $defclass ui_tabs_start'>\n";
return $rv;
}

sub theme_ui_tabs_end_tab
{
return "</div>\n";
}

sub theme_ui_tabs_end
{
return "</div>\n";
}

# theme_ui_columns_start(&headings, [width-percent], [noborder], [&tdtags], [title])
# Returns HTML for a multi-column table, with the given headings
sub theme_ui_columns_start
{
my ($heads, $width, $noborder, $tdtags, $title) = @_;
my ($href) = grep { $_ =~ /<a\s+href/i } @$heads;
my $rv;
$theme_ui_columns_row_toggle = 0;
my @classes;
#push(@classes, "ui_table") if (!$noborder);
push(@classes, "sortable") if (!$href);
#push(@classes, "ui_columns");
push(@classes, "table table-striped");
$rv .= "<table".(@classes ? " class='".join(" ", @classes)."'" : "").
    (defined($width) ? " width=$width%" : "").">\n";
if ($title) {
  $rv .= "<thead> <tr $tb class='ui_columns_heading'>".
	 "<td colspan=".scalar(@$heads)."><b>$title</b></td>".
	 "</tr> </thead> <tbody>\n";
  }
$rv .= "<thead> <tr class='ui_columns_heads'>\n";
my $i;
for($i=0; $i<@$heads; $i++) {
  $rv .= "<td ".$tdtags->[$i]."><b>".
         ($heads->[$i] eq "" ? "<br>" : $heads->[$i])."</b></td>\n";
  }
$rv .= "</tr></thead> <tbody>\n";
$theme_ui_columns_count++;
return $rv;
}

# theme_ui_columns_row(&columns, &tdtags)
# Returns HTML for a row in a multi-column table
sub theme_ui_columns_row
{
$theme_ui_columns_row_toggle = $theme_ui_columns_row_toggle ? '0' : '1';
my ($cols, $tdtags) = @_;
my $rv;
$rv .= "<tr class='ui_columns_row row$theme_ui_columns_row_toggle' onMouseOver=\"this.className='mainhigh'\" onMouseOut=\"this.className='mainbody row$theme_ui_columns_row_toggle'\">\n";
my $i;
for($i=0; $i<@$cols; $i++) {
	$rv .= "<td ".$tdtags->[$i].">".
	       ($cols->[$i] !~ /\S/ ? "<br>" : $cols->[$i])."</td>\n";
	}
$rv .= "</tr>\n";
return $rv;
}

# theme_ui_columns_end()
# Returns HTML to end a table started by ui_columns_start
sub theme_ui_columns_end
{
my $rv;
$rv = "</tbody> </table>\n";
if ($COLUMNS_WRAPPER_OPEN == 1) { # Last wrapper
	$rv .= "</td> </tr> </table>\n";
	}
$COLUMNS_WRAPPER_OPEN--;
return $rv;
}

# theme_ui_grid_table(&elements, columns, [width-percent], [tds], [tabletags],
#   [title])
# Given a list of HTML elements, formats them into a table with the given
# number of columns. However, themes are free to override this to use fewer
# columns where space is limited.
sub theme_ui_grid_table
{
my ($elements, $cols, $width, $tds, $tabletags, $title) = @_;
return "" if (!@$elements);

#my $rv = "<table class='well' " 
#       . ($width ? " width=$width%" : " width=100%")
#       . ($tabletags ? " ".$tabletags : "")
#       . "><tr><td>\n";
my $rv .= "<table class='ui_table ui_grid_table table table-striped'"
     . ($width ? " width=$width%" : "")
     . ($tabletags ? " ".$tabletags : "")
     . ">\n";
if ($title) {
	$rv .= "<thead><tr class='ui_grid_heading'> ".
	       "<td colspan=$cols><b>$title</b></td> </tr></thead>\n";
	}
$rv .= "<tbody>\n";
my $i;
for($i=0; $i<@$elements; $i++) {
  $rv .= "<tr class='ui_grid_row'>" if ($i%$cols == 0);
  $rv .= "<td ".$tds->[$i%$cols]." valign=top class='ui_grid_cell'>".
	 $elements->[$i]."</td>\n";
  $rv .= "</tr>" if ($i%$cols == $cols-1);
  }
if ($i%$cols) {
  while($i%$cols) {
    $rv .= "<td ".$tds->[$i%$cols]." class='ui_grid_cell'><br></td>\n";
    $i++;
    }
  $rv .= "</tr>\n";
  }
$rv .= "</table>\n";
$rv .= "</tbody>\n";
#$rv .= "</td></tr></table>\n"; # wrapper
return $rv;
}

# theme_ui_hidden_table_start(heading, [tabletags], [cols], name, status,
#                             [&default-tds], [rightheading])
# An accordion group (or just single hideable section) with a heading and 
# content section inside, which is collapsible
sub theme_ui_hidden_table_start
{
my ($heading, $tabletags, $cols, $name, $status, $tds, $rightheading) = @_;
my $rv;
my $divid = "hiddendiv_$name";
my $defclass = $status ? 'in' : ''; # Open or closed

$rv .= <<EOL;
<div class="panel-group" id='#$divid'>
<div class="panel panel-default">
<div class="panel-heading">
<h4 class="panel-title">
  <a class="accordion-toggle" href="#$divid" data-toggle="collapse">$heading</a>
</h4>
</div>

<div id="$divid" class="panel-collapse $defclass collapse">
<div class="panel-body">
EOL
$main::ui_table_cols = $cols || 4;
$main::ui_table_pos = 0;
$main::ui_table_default_tds = $tds;
return $rv;
}

# ui_hidden_table_end(name)
# Returns HTML for the end of table with hiding, as started by
# ui_hidden_table_start
sub theme_ui_hidden_table_end
{
my ($name) = @_;
my $rv = "</div></div></div></div>\n";
return $rv;
}

sub theme_ui_hidden_start
{
my ($title, $name, $status, $url) = @_;
my $rv;
my $divid = "hiddendiv_$name";
$rv .= "<button type='button' data-toggle='collapse' data-target='\#$divid'>$title</button>\n";
$rv .= "<div class='$defclass collapse' id='$divid'>\n";
return $rv;
}

sub theme_ui_hidden_end
{
my ($name) = @_;
return "</div> <!-- $name hidden_end -->\n";
}

# theme_select_all_link(field, form, text)
# Adds support for row highlighting to the normal select all
sub theme_select_all_link
{
my ($field, $form, $text) = @_;
$form = int($form);
$text ||= $text{'ui_selall'};
return "<a class='select_all' href='#' onClick='f = document.forms[$form]; ff = f.$field; ff.checked = true; r = document.getElementById(\"row_\"+ff.id); if (r) { r.className = \"mainsel\" }; for(i=0; i<f.$field.length; i++) { ff = f.${field}[i]; if (!ff.disabled) { ff.checked = true; r = document.getElementById(\"row_\"+ff.id); if (r) { r.className = \"mainsel\" } } } return false'>$text</a>";
}

# theme_select_invert_link(field, form, text)
# Adds support for row highlighting to the normal invert selection
sub theme_select_invert_link
{
my ($field, $form, $text) = @_;
$form = int($form);
$text ||= $text{'ui_selinv'};
return "<a class='select_invert' href='#' onClick='f = document.forms[$form]; ff = f.$field; ff.checked = !f.$field.checked; r = document.getElementById(\"row_\"+ff.id); if (r) { r.className = ff.checked ? \"mainsel\" : \"mainbody\" }; for(i=0; i<f.$field.length; i++) { ff = f.${field}[i]; if (!ff.disabled) { ff.checked = !ff.checked; r = document.getElementById(\"row_\"+ff.id); if (r) { r.className = ff.checked ? \"mainsel\" : \"mainbody row\"+((i+1)%2) } } } return false'>$text</a>";
}

# theme_select_status_link(name, form, &folder, &mails, start, end, status, label)
# Adds support for row highlighting to read mail module selector
# XXX can delete after Usermin 1.400
sub theme_select_status_link
{
my ($name, $formno, $folder, $mail, $start, $end, $status, $label) = @_;
$formno = int($formno);
my @sel;
for(my $i=$start; $i<=$end; $i++) {
	my $read = &get_mail_read($folder, $mail->[$i]);
	if ($status == 0) {
		push(@sel, ($read&1) ? 0 : 1);
		}
	elsif ($status == 1) {
		push(@sel, ($read&1) ? 1 : 0);
		}
	elsif ($status == 2) {
		push(@sel, ($read&2) ? 1 : 0);
		}
	}
my $js = "var sel = [ ".join(",", @sel)." ]; ";
$js .= "var f = document.forms[$formno]; ";
$js .= "for(var i=0; i<sel.length; i++) { document.forms[$formno].${name}[i].checked = sel[i]; var ff = f.${name}[i]; var r = document.getElementById(\"row_\"+ff.id); if (r) { r.className = ff.checked ? \"mainsel\" : \"mainbody row\"+((i+1)%2) } }";
$js .= "return false;";
return "<a class='select_status' href='#' onClick='$js'>$label</a>";
}

sub theme_select_rows_link
{
my ($field, $form, $text, $rows) = @_;
$form = int($form);
my $js = "var sel = { ".join(",", map { "\"".&quote_escape($_)."\":1" } @$rows)." }; ";
$js .= "for(var i=0; i<document.forms[$form].${field}.length; i++) { var ff = document.forms[$form].${field}[i]; var r = document.getElementById(\"row_\"+ff.id); ff.checked = sel[ff.value]; if (r) { r.className = ff.checked ? \"mainsel\" : \"mainbody row\"+((i+1)%2) } } ";
$js .= "return false;";
return "<a class='select_rows' href='#' onClick='$js'>$text</a>";
}

sub theme_ui_checked_columns_row
{
$theme_ui_columns_row_toggle = $theme_ui_columns_row_toggle ? '0' : '1';
my ($cols, $tdtags, $checkname, $checkvalue, $checked, $disabled, $tags) = @_;
my $rv;
my $cbid = &quote_escape(quotemeta("${checkname}_${checkvalue}"));
my $rid = &quote_escape(quotemeta("row_${checkname}_${checkvalue}"));
my $ridtr = &quote_escape("row_${checkname}_${checkvalue}");
my $mycb = $cb;
if ($checked) {
	$mycb =~ s/mainbody/mainsel/g;
	}
$mycb =~ s/class='/class='row$theme_ui_columns_row_toggle ui_checked_columns /;
$rv .= "<tr id=\"$ridtr\" $mycb onMouseOver=\"this.className = document.getElementById('$cbid').checked ? 'mainhighsel' : 'mainhigh'\" onMouseOut=\"this.className = document.getElementById('$cbid').checked ? 'mainsel' : 'mainbody row$theme_ui_columns_row_toggle'\">\n";
$rv .= "<td class='ui_checked_checkbox' ".$tdtags->[0].">".
       &ui_checkbox($checkname, $checkvalue, undef, $checked, $tags." "."onClick=\"document.getElementById('$rid').className = this.checked ? 'mainhighsel' : 'mainhigh';\"", $disabled).
       "</td>\n";
my $i;
for($i=0; $i<@$cols; $i++) {
	$rv .= "<td ".$tdtags->[$i+1].">";
	if ($cols->[$i] !~ /<a\s+href|<input|<select|<textarea/) {
		$rv .= "<label for=\"".
			&quote_escape("${checkname}_${checkvalue}")."\">";
		}
	$rv .= ($cols->[$i] !~ /\S/ ? "<br>" : $cols->[$i]);
	if ($cols->[$i] !~ /<a\s+href|<input|<select|<textarea/) {
		$rv .= "</label>";
		}
	$rv .= "</td>\n";
	}
$rv .= "</tr>\n";
return $rv;
}

sub theme_ui_radio_columns_row
{
my ($cols, $tdtags, $checkname, $checkvalue, $checked) = @_;
my $rv;
my $cbid = &quote_escape(quotemeta("${checkname}_${checkvalue}"));
my $rid = &quote_escape(quotemeta("row_${checkname}_${checkvalue}"));
my $ridtr = &quote_escape("row_${checkname}_${checkvalue}");
my $mycb = $cb;
if ($checked) {
	$mycb =~ s/mainbody/mainsel/g;
	}

$mycb =~ s/class='/class='ui_radio_columns /;
$rv .= "<tr $mycb id=\"$ridtr\" onMouseOver=\"this.className = document.getElementById('$cbid').checked ? 'mainhighsel' : 'mainhigh'\" onMouseOut=\"this.className = document.getElementById('$cbid').checked ? 'mainsel' : 'mainbody'\">\n";
$rv .= "<td ".$tdtags->[0]." class='ui_radio_radio'>".
       &ui_oneradio($checkname, $checkvalue, undef, $checked, "onClick=\"for(i=0; i<form.$checkname.length; i++) { ff = form.${checkname}[i]; r = document.getElementById('row_'+ff.id); if (r) { r.className = 'mainbody' } } document.getElementById('$rid').className = this.checked ? 'mainhighsel' : 'mainhigh';\"").
       "</td>\n";
my $i;
for($i=0; $i<@$cols; $i++) {
	$rv .= "<td ".$tdtags->[$i+1].">";
	if ($cols->[$i] !~ /<a\s+href|<input|<select|<textarea/) {
		$rv .= "<label for=\"".
			&quote_escape("${checkname}_${checkvalue}")."\">";
		}
	$rv .= ($cols->[$i] !~ /\S/ ? "<br>" : $cols->[$i]);
	if ($cols->[$i] !~ /<a\s+href|<input|<select|<textarea/) {
		$rv .= "</label>";
		}
	$rv .= "</td>\n";
	}
$rv .= "</tr>\n";
return $rv;
}

# theme_ui_nav_link(direction, url, disabled)
# Returns an arrow icon linking to provided url
sub theme_ui_nav_link
{
my ($direction, $url, $disabled) = @_;
my $alt = $direction eq "left" ? '<-' : '->';
if ($disabled) {
  return "<img alt=\"$alt\" align=\"middle\""
       . "src=\"$gconfig{'webprefix'}/images/$direction-grey.gif\">\n";
  }
else {
  return "<a href=\"$url\"><img alt=\"$alt\" align=\"top\""
       . "src=\"$gconfig{'webprefix'}/images/$direction.gif\"></a>\n";
  }
}

# theme_footer([page, name]+, [noendbody])
# Output a footer for returning to some page
sub theme_footer
{
my $i;
my $count = 0;
my %module_info = get_module_info(get_module_name());
for($i=0; $i+1<@_; $i+=2) {
	local $url = $_[$i];
	if ($url ne '/' || !$tconfig{'noindex'}) {
		if ($url eq '/') {
			$url = "/?cat=$module_info{'category'}";
			}
		elsif ($url eq '' && get_module_name() eq 'virtual-server' ||
		       $url eq '/virtual-server/') {
			# Don't bother with virtualmin menu
			next;
			}
		elsif ($url eq '' && get_module_name() eq 'server-manager' ||
		       $url eq '/server-manager/') {
			# Don't bother with Cloudmin menu
			next;
			}
		elsif ($url =~ /(view|edit)_domain.cgi/ &&
		       get_module_name() eq 'virtual-server' ||
		       $url =~ /^\/virtual-server\/(view|edit)_domain.cgi/) {
			# Don't bother with link to domain details
			next;
			}
		elsif ($url =~ /edit_serv.cgi/ &&
		       get_module_name() eq 'server-manager' ||
		       $url =~ /^\/virtual-server\/edit_serv.cgi/) {
			# Don't bother with link to system details
			next;
			}
		elsif ($url eq '' && get_module_name()) {
			$url = "/".get_module_name()."/".
			       $module_info{'index_link'};
			}
		elsif ($url =~ /^\?/ && get_module_name()) {
			$url = "/".get_module_name()."/$url";
			}
		$url = "$gconfig{'webprefix'}$url" if ($url =~ /^\//);
		if ($count++ == 0) {
			print theme_ui_nav_link("left", $url);
			}
		else {
			print "&nbsp;|\n";
			}
		print "&nbsp;<a href=\"$url\">",&text('main_return', $_[$i+1]),"</a>\n";
		}
	}
print "<br>\n";
#	print <<EOL;
#    <!-- Javascript ================================================== -->
#    <!-- Placed at the end of the document so the pages load faster -->
#    <script src="/bootstrap/js/jquery-1.8.0.min.js"></script>
#    <script src="/bootstrap/js/bootstrap.js"></script>
#    <script src="/js/index.js"></script>
#</body></html>
#EOL
print"</body></html>\n";
}

# Don't show virtualmin menu
sub theme_redirect
{
local ($orig, $url) = @_;
if (get_module_name() eq "virtual-server" && $orig eq "" &&
    $url =~ /^((http|https):\/\/([^\/]+))\//) {
	$url = "$1/right.cgi";
	}
print "Location: $url\n\n";
}

# XXX Need to set Save buttons to class btn-primary
sub theme_ui_button
{
my ($label, $name, $dis, $tags) = @_;
return "<button class='btn' type='button'".
       ($name ne '' ? " name=\"".&quote_escape($name)."\"" : "").
       " value=\"".&quote_escape($label)."\"".
       ($dis ? " disabled=true" : "").
       ($tags ? " ".$tags : "").">$label</button>\n";
}

# XXX Need to set Save buttons to class btn-primary
sub theme_ui_submit
{
my ($label, $name, $dis, $tags) = @_; 
return "<button class='btn ui_submit' type='submit'".
       ($name ne '' ? " name=\"".&quote_escape($name)."\"" : "").
       " value=\"".&quote_escape($label)."\"".
       ($dis ? " disabled=true" : "").
       ($tags ? " ".$tags : "").">$label</button>\n";

}

sub theme_ui_opt_textbox
{
my ($name, $value, $size, $opt1, $opt2, $dis, $extra, $max, $tags) = @_;
my $dis1 = &js_disable_inputs([ $name, @$extra ], [ ]);
my $dis2 = &js_disable_inputs([ ], [ $name, @$extra ]);
my $rv;
$size = &ui_max_text_width($size);
$rv .= &ui_radio($name."_def", $value eq '' ? 1 : 0,
                 [ [ 1, $opt1, "onClick='$dis1'" ],
                   [ 0, $opt2 || " ", "onClick='$dis2'" ] ], $dis)."\n";
$rv .= "<input class='form-control ui_opt_textbox' name=\"".&quote_escape($name)."\" ".
       "type='text' size=$size value=\"".&quote_escape($value)."\" ".
       ($dis ? "disabled=true" : "").
       ($max ? " maxlength=$max" : "").
       " ".$tags.
       ">\n";
$rv .= "<script>if ($ui_formcount < document.forms.length) { document.forms[$ui_formcount].$name.disabled = document.forms[$ui_formcount].${name}_def[0].checked; }</script>\n";
return $rv;
}

sub theme_file_chooser_button
{
my $form = defined($_[2]) ? $_[2] : 0;
my $chroot = defined($_[3]) ? $_[3] : "/";
my $add = int($_[4]);
my ($w, $h) = (400, 300);
if ($gconfig{'db_sizefile'}) {
        ($w, $h) = split(/x/, $gconfig{'db_sizefile'});
        }
return "<button class='btn' type='button' onClick='ifield = form.$_[0]; chooser = window.open(\"$gconfig{'webprefix'}/chooser.cgi?add=$add&type=$_[1]&chroot=$chroot&file=\"+escape(ifield.value), \"chooser\", \"toolbar=no,menubar=no,scrollbars=no,resizable=yes,width=$w,height=$h\"); chooser.ifield = ifield; window.ifield = ifield' value=\"...\">...</button>\n";
}

# XXX Temporary until ui-lib.pl valign stuff gets cleaned up
#
# theme_ui_columns_table(&headings, width-percent, &data, &types, no-sort, title,
#		   empty-msg)
# Returns HTML for a complete table.
# headings - An array ref of heading HTML
# width-percent - Preferred total width
# data - A 2x2 array ref of table contents. Each can either be a simple string,
#        or a hash ref like :
#          { 'type' => 'group', 'desc' => 'Some section title' }
#          { 'type' => 'string', 'value' => 'Foo', 'colums' => 3,
#	     'nowrap' => 1 }
#          { 'type' => 'checkbox', 'name' => 'd', 'value' => 'foo',
#            'label' => 'Yes', 'checked' => 1, 'disabled' => 1 }
#          { 'type' => 'radio', 'name' => 'd', 'value' => 'foo', ... }
# types - An array ref of data types, such as 'string', 'number', 'bytes'
#         or 'date'
# no-sort - Set to 1 to disable sorting by theme
# title - Text to appear above the table
# empty-msg - Message to display if no data
sub theme_ui_columns_table
{
my ($heads, $width, $data, $types, $nosort, $title, $emptymsg) = @_;
my $rv;

# Just show empty message if no data
if ($emptymsg && !@$data) {
	$rv .= &ui_subheading($title) if ($title);
	$rv .= "<b>$emptymsg</b><p>\n";
	return $rv;
	}

# Are there any checkboxes in each column? If so, make those columns narrow
my @tds;
my $maxwidth = 0;
foreach my $r (@$data) {
	my $cc = 0;
	foreach my $c (@$r) {
		if (ref($c) &&
		    ($c->{'type'} eq 'checkbox' || $c->{'type'} eq 'radio')) {
			$tds[$cc] .= " width=5" if ($tds[$cc] !~ /width=/);
			}
		$cc++;
		}
	$maxwidth = $cc if ($cc > $maxwidth);
	}
$rv .= &ui_columns_start($heads, $width, 0, \@tds, $title);

# Add the data rows
foreach my $r (@$data) {
	my $c0;
	if (ref($r->[0]) && ($r->[0]->{'type'} eq 'checkbox' ||
			     $r->[0]->{'type'} eq 'radio')) {
		# First column is special
		$c0 = $r->[0];
		$r = [ @$r[1..(@$r-1)] ];
		}
	# Turn data into HTML
	my @rtds = @tds;
	my @cols;
	my $cn = 0;
	$cn++ if ($c0);
	foreach my $c (@$r) {
		if (!ref($c)) {
			# Plain old string
			push(@cols, $c);
			}
		elsif ($c->{'type'} eq 'checkbox') {
			# Checkbox in non-first column
			push(@cols, &ui_checkbox($c->{'name'}, $c->{'value'},
					         $c->{'label'}, $c->{'checked'},
						 $c->{'tags'},
						 $c->{'disabled'}));
			}
		elsif ($c->{'type'} eq 'radio') {
			# Radio button in non-first column
			push(@cols, &ui_oneradio($c->{'name'}, $c->{'value'},
					         $c->{'label'}, $c->{'checked'},
						 $c->{'tags'},
						 $c->{'disabled'}));
			}
		elsif ($c->{'type'} eq 'group') {
			# Header row that spans whole table
			$rv .= &ui_columns_header([ $c->{'desc'} ],
						  [ "colspan=$width" ]);
			next;
			}
		elsif ($c->{'type'} eq 'string') {
			# A string, which might be special
			push(@cols, $c->{'value'});
			if ($c->{'columns'} > 1) {
				splice(@rtds, $cn, $c->{'columns'},
				       "colspan=".$c->{'columns'});
				}
			if ($c->{'nowrap'}) {
				$rtds[$cn] .= " nowrap";
				}
			}
		$cn++;
		}
	# Add the row
	if (!$c0) {
		$rv .= &ui_columns_row(\@cols, \@rtds);
		}
	elsif ($c0->{'type'} eq 'checkbox') {
		$rv .= &ui_checked_columns_row(\@cols, \@rtds, $c0->{'name'},
					       $c0->{'value'}, $c0->{'checked'},
					       $c0->{'disabled'},
					       $c0->{'tags'});
		}
	elsif ($c0->{'type'} eq 'radio') {
		$rv .= &ui_radio_columns_row(\@cols, \@rtds, $c0->{'name'},
					     $c0->{'value'}, $c0->{'checked'},
					     $c0->{'disabled'},
					     $c0->{'tags'});
		}
	}

$rv .= &ui_columns_end();
return $rv;
}

=pod
=head1 Bootstrap

Functions for generating Bootstrap CSS grids markup.

=cut

# ui_bs_grid_start(id, type)
# Return a boostrap grid row opening div.
sub theme_ui_bs_grid_start {
	my ($id, $type) = @_;
	return "<div id='grid_$id' class='row'>\n";
}

sub theme_ui_bs_grid_end {
	my ($id) = @_;
	return "</div> <!-- grid_$id -->\n";
}

# ui_yui_grid_section_start(id, first?)
# Return a yui grid markup section opening div.
sub theme_ui_yui_grid_section_start {
	my ($id, $first) = @_;
	if ($first) { return "<div id='grid_$id' class='yui-u first'>\n"; }
	else { return "<div id='grid_$id' class='yui-u'>\n"; }
}
sub theme_ui_yui_grid_section_end {
	my ($id) = @_;
	return "</div> <!-- grid_$id -->\n";
}

# ui_hlink(text, page, module, width, height)
# Returns HTML for a link that when clicked on pops up a window for a Webmin
# help page. The parameters are :
# text - Text for the link.
# page - Help page code, such as 'intro'.
# module - Module the help page is in. Defaults to the current module.
# width - Width of the help popup window. Defaults to 600 pixels.
# height - Height of the help popup window. Defaults to 400 pixels.

# The actual help pages are in each module's help sub-directory, in files with
# .html extensions.
sub theme_ui_hlink {
my $mod = $_[2] ? $_[2] : &get_module_name();
my $width = $_[3] || $tconfig{'help_width'} || $gconfig{'help_width'} || 600;
my $height = $_[4] || $tconfig{'help_height'} || $gconfig{'help_height'} || 400;
return "<a class='ui_hlink' onClick='window.open(\"$gconfig{'webprefix'}/help.cgi/$mod/$_[1]\", \"help\", \"toolbar=no,menubar=no,scrollbars=yes,width=$width,height=$height,resizable=yes\"); return false' href=\"$gconfig{'webprefix'}/help.cgi/$mod/$_[1]\">$_[0]</a>";
}

sub theme_ui_select
{
my ($name, $value, $opts, $size, $multiple, $missing, $dis, $js) = @_;
my $rv;
$rv .= "<select class='form-control ui_select' name=\"".&quote_escape($name)."\"".
       ($size ? " size=$size" : "").
       ($multiple ? " multiple" : "").
       ($dis ? " disabled=true" : "")." ".$js.">\n";
my ($o, %opt, $s);
my %sel = ref($value) ? ( map { $_, 1 } @$value ) : ( $value, 1 );
foreach $o (@$opts) {
    $o = [ $o ] if (!ref($o));
    $rv .= "<option value=\"".&quote_escape($o->[0])."\"".
           ($sel{$o->[0]} ? " selected" : "")." ".$o->[2].">".
           ($o->[1] || $o->[0])."\n";
    $opt{$o->[0]}++;
    }
foreach $s (keys %sel) {
    if (!$opt{$s} && $missing) {
        $rv .= "<option value=\"".&quote_escape($s)."\"".
               "selected>".($s eq "" ? "&nbsp;" : $s)."\n";
        }
    }
$rv .= "</select>\n";
return $rv;
}

sub theme_ui_textarea
{
my ($name, $value, $rows, $cols, $wrap, $dis, $tags) = @_;
$cols = &ui_max_text_width($cols, 1);
return "<textarea class='form-control ui_textarea' name=\"".&quote_escape($name)."\" ".
       "rows=$rows cols=$cols".($wrap ? " wrap=$wrap" : "").
       ($dis ? " disabled=true" : "").
       ($tags ? " $tags" : "").">".
       &html_escape($value).
       "</textarea>";
}

=head2 theme_ui_alert_box(msg, class)

Returns HTML for an alert box, with background color determined by $class.

$msg contains any text or HTML to be contained within the alert box, and
can include forms.

Classes of alert:

=item success - green

=item info - blue

=item warning - yellow

=item danger - red

=cut

sub theme_ui_alert_box
{
my ($msg, $class) = @_;
my $rv;

$rv .= "<div class='alert alert-$class'>";
$rv .= "$msg\n";
$rv .= "</div>\n";

return $rv;
}

=head2 theme_ui_form_start(script, method, [target], [tags])

Returns HTML for the start of a a form that submits to some script. The
parameters are :

=item script - CGI script to submit to, like save.cgi.

=item method - HTTP method, which must be one of 'get', 'post' or 'form-data'. If form-data is used, the target CGI must call ReadParseMime to parse parameters.

=item target - Optional target window or frame for the form.

=item tags - Additional HTML attributes for the form tag.

=cut
sub theme_ui_form_start
{
$ui_formcount ||= 0;
my ($script, $method, $target, $tags) = @_;
# add directory, unless already starts with a /
unless ( $script =~ /^\// )
{
  $script = "/" . get_module_name . "/$script";
}
my $rv;
$rv .= "<form class='ui_form' action='".&html_escape($script)."' ".
    ($method eq "post" ? "method=post" :
     $method eq "form-data" ?
        "method=post enctype=multipart/form-data" :
        "method=get").
    ($target ? " target=$target" : "").
        " ".$tags.
       ">\n";
return $rv;
}

1;


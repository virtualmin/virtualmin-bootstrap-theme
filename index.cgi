#!/usr/local/bin/perl

require "virtual-server-theme/bootstrap-theme-lib.pl";
&ReadParse();

# Work out which module to open by default
$hasvirt = &foreign_available("virtual-server");
$hasvm2 = &foreign_available("server-manager");
if ($in{'dom'} && $hasvirt) {
	# Caller has requested a specific domain ..
	&foreign_require("virtual-server", "virtual-server-lib.pl");
	$d = &virtual_server::get_domain($in{'dom'});
	if ($d) {
		$goto = &virtual_server::can_config_domain($d) ?
			"virtual-server/edit_domain.cgi?dom=$d->{'id'}" :
			"virtual-server/view_domain.cgi?dom=$d->{'id'}";
		$left = "left.cgi?dom=$d->{'id'}";
		}
	}
if (!$goto) {
	# Default is determined by theme or Webmin config,
	# defaults to system info page
	local $sects = &get_right_frame_sections();
	$minfo = &get_goto_module();
	if ($sects->{'list'} == 1 && $hasvirt) {
		$goto = "virtual-server/";
		}
	elsif ($sects->{'list'} == 2 && $hasvm2) {
		$goto = "server-manager/";
		}
	elsif ($minfo &&
               $minfo->{'dir'} ne 'virtual-server' &&
               $minfo->{'dir'} ne 'server-manager') {
		$goto = "$minfo->{'dir'}/";
		}
	else {
		$goto = "right.cgi?open=system&auto=status&open=updates&".
		  	"open=common&open=owner&open=reseller&open=vm2limits";
		}
	$left = "left.cgi";
	if ($minfo) {
		$left .= "?$minfo->{'category'}=1";
		}
	}

if ($gconfig{'os_version'} eq "*") {
	$ostr = $gconfig{'real_os_type'};
	}
else {
	$ostr = "$gconfig{'real_os_type'} $gconfig{'real_os_version'}";
	}
$host = &get_display_hostname();
if ($hasvirt) {
	# Show Virtualmin version
	%minfo = &get_module_info("virtual-server");
	$ver = $minfo{'version'};
	$title = $gconfig{'nohostname'} ? $text{'vmain_title2'} :
		 $gconfig{'showhost'} ?
			&text('vmain_title3', $ver, $ostr) :
			&text('vmain_title', $ver, $host, $ostr);
	}
elsif ($hasvm2) {
	# Show Cloudmin version
	%minfo = &get_module_info("server-manager");
	$ver = $minfo{'version'};
	$title = $gconfig{'nohostname'} ? $text{'mmain_title2'} :
		 $gconfig{'showhost'} ?
			&text('mmain_title3', $ver, $ostr) :
			&text('mmain_title', $ver, $host, $ostr);
	}
else {
	# Show Webmin version
	$ver = &get_webmin_version();
	$title = $gconfig{'nohostname'} ? $text{'main_title2'} :
	 	 $gconfig{'showhost'} ?
			&text('main_title3', $ver, $ostr) :
			&text('main_title', $ver, $host, $ostr);
	}
if ($gconfig{'showlogin'}) {
	$title = $remote_user." : ".$title;
	}
if ($gconfig{'showhost'}) {
	$title = $host." : ".$title;
	}

# Work out if we have a top frame
if ($hasvirt) {
	%vconfig = &foreign_config("virtual-server");
	}
$upperframe = $vconfig{'theme_topframe'} ||
	      $gconfig{'theme_topframe'};
$upperrows = $vconfig{'theme_toprows'} ||
	     $gconfig{'theme_toprows'} || 200;
if ($upperframe =~ /\$LEVEL|\$\{LEVEL/) {
	# Sub in user level
	$levelnum = &get_virtualmin_user_level();
	$level = $levelnum == 0 ? "master" :
		 $levelnum == 1 ? "reseller" :
		 $levelnum == 2 ? "domain" :
		 $levelnum == 3 ? "usermin" :
		 $levelnum == 4 ? "owner" : "unknown";
	$upperframe = &substitute_template($upperframe, { 'level' => $level });
	}

# Show frameset
&PrintHeader();
$cols = &get_left_frame_width();
$frame1 = "<div id='left' class='span4 sidebar'></div>"; # src='$left'
$frame2 = "<div id='right' class='span8'></div>"; # src='$goto'
$fscols = "$cols,*";
if ($current_lang_info->{'rtl'} || $current_lang eq "ar") {
	($frame1, $frame2) = ($frame2, $frame1);
	$fscols = "*,$cols";
	}

# Page header
print "<html>\n";
print "<head> <title>$title</title> </head>\n";

# Upper custom frame
if ($upperframe) {
	#print "<frameset rows='$upperrows,*' border=0>\n";
	if ($upperframe =~ /^\//) {
		# Local file to serve
		print "<div id='top' class='navbar navbar-fixed-top'></div>\n"; # src='top.cgi'
		}
	else {
		# Absolute URL
		print "<div id='top class='navbar navbar-fixed-top'></div>\n"; # src='$upperframe'
		}
	}

# Left and right sections
print "<div class='container'>\n";
print "<div class='row'>\n";
print $frame1,"\n";
print $frame2,"\n";
print "</div>\n";
print "</div>\n";
print "</html>\n";


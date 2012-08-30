#!/usr/bin/perl
# session_login.cgi
# Display the login form used in session login mode

$pragma_no_cache = 1;
#$ENV{'MINISERV_INTERNAL'} || die "Can only be called by miniserv.pl";
require './web-lib.pl';
require './ui-lib.pl';
&init_config();
&ReadParse();
if ($gconfig{'loginbanner'} && $ENV{'HTTP_COOKIE'} !~ /banner=1/ &&
    !$in{'logout'} && !$in{'failed'} && !$in{'timed_out'}) {
	# Show pre-login HTML page
	print "Set-Cookie: banner=1; path=/\r\n";
	&PrintHeader();
	$url = $in{'page'};
	open(BANNER, $gconfig{'loginbanner'});
	while(<BANNER>) {
		s/LOGINURL/$url/g;
		print;
		}
	close(BANNER);
	return;
	}
$sec = uc($ENV{'HTTPS'}) eq 'ON' ? "; secure" : "";
&get_miniserv_config(\%miniserv);
$sidname = $miniserv{'sidname'} || "sid";
print "Set-Cookie: banner=0; path=/$sec\r\n" if ($gconfig{'loginbanner'});
print "Set-Cookie: $sidname=x; path=/$sec\r\n" if ($in{'logout'});
print "Set-Cookie: testing=1; path=/$sec\r\n";
print "Content-type: text/html\n\n";

print <<EOF;
    <!DOCTYPE HTML>
    <!-- styles -->
    <link href="/unauthenticated/bootstrap.css" rel="stylesheet">
    <style type="text/css">
      body {
        padding-top: 60px;
        padding-bottom: 40px;
      }
    </style>
    <link href="/unauthenticated/bootstrap-responsive.css" rel="stylesheet">
EOF

if ($tconfig{'inframe'}) {
	# Framed themes lose original page
	$in{'page'} = "/";
	}

print "<div class='ui-login'>\n";
if (defined($in{'failed'})) {
	print "<h3>$text{'session_failed'}</h3><p>\n";
	}
elsif ($in{'logout'}) {
	print "<h3>$text{'session_logout'}</h3><p>\n";
	}
elsif ($in{'timed_out'}) {
	print "<h3>",&text('session_timed_out', int($in{'timed_out'}/60)),"</h3><p>\n";
	}
print "$text{'session_prefix'}\n";
print "<form action=$gconfig{'webprefix'}/session_login.cgi method=post>\n";
print "<input type=hidden name=page value='".&html_escape($in{'page'})."'>\n";
if ($gconfig{'realname'}) {
	$host = &get_display_hostname();
	}
else {
	$host = $ENV{'HTTP_HOST'};
	$host =~ s/:\d+//g;
	$host = &html_escape($host);
	}
print <<EOF;
<div class="container">
	<div class="well">
			<fieldset>
        			<label for="user">$text{'session_user'}</label>
				<input type="text" size="20" name="user" id="user_field" value="$in{'failed'}" /><p>
				<label for="pass">$text{'session_pass'}</label>
				<input name="pass" size="20" id="pass_field" type="password" />
				<p>
EOF
if ($vconfig{'theme_image'}) {
  # Show the hosting provider logo
  $link = $vconfig{'theme_link'};
  print "<a href='$link' target=_new>" if ($link);
  print "<img id='logo' src='$vconfig{'theme_image'}' border=0>";
  print "</a>\n" if ($link);
  }
else {
  print "<img id='logo' src='/unauthenticated/images/virtualminlogo.png' alt='Virtualmin' />\n";
  }
print <<EOF;
				<input type=submit value='$text{'session_login'}' class='btn' />
				</fieldset>
</div></div>
<script type="text/javascript">document.getElementById("pass_field").value = ""; document.getElementById("user_field").focus();</script>
EOF

#print "<tr> <td colspan=2 align=center>",
#      &text($gconfig{'nohostname'} ? 'session_mesg2' : 'session_mesg',
#	    "<tt>$host</tt>"),"</td> </tr>\n";
print "</form></div>\n";
print "$text{'session_postfix'}\n";


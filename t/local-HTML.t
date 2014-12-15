#!/usr/bin/perl
# Test the HTML output of all cgi and html files against HTML::Lint

use strict;
use warnings;
use HTML::Lint::Pluggable;
use Test::HTML::Lint tests => 3;                      # last test to print
use Cwd;

# Some Webmin variables to allow running CGI scripts as though Webmin is running
our $no_acl_check++;
our %ENV;
$ENV{'WEBMIN_CONFIG'} ||= "/etc/webmin";
$ENV{'WEBMIN_VAR'} ||= "/var/webmin";
$ENV{'MINISERV_CONFIG'} ||= $ENV{'WEBMIN_CONFIG'}."/miniserv.conf";
$ENV{'SERVER_ROOT'} ||= "/usr/libexec/webmin";
$ENV{'BASE_REMOTE_USER'} ||= "root";
$ENV{'REMOTE_USER'} ||= $ENV{'BASE_REMOTE_USER'};
our $trust_unknown_referers = 1;

chdir "/usr/libexec/webmin" or die "Can't change directory.";

BEGIN { push(@INC, "."); };

my @pages = ( "newleft.cgi",
	   );

foreach my $page (@pages) {
	$ENV{'SCRIPT_NAME'} = "/$page";
	$ENV{'SCRIPT_FILENAME'} = "$ENV{'SERVER_ROOT'}/bootstrap-theme/$page";
	require "bootstrap-theme/$page";
	my $content = sidebar();
	my $lint = new HTML::Lint::Pluggable;
	$lint->load_plugins(qw/HTML5/);

	html_ok( $lint, $content, "$page HTML validation");
}

my @htmlpages = ( "index.html" );

foreach my $page (@htmlpages) {
	open (my $fh, "<", "/usr/libexec/webmin/bootstrap-theme/$page") or die "Can't open file: $!\n";
	my $content = do { local $/; $fh };
	html_ok( $content, "$page HTML validation");
}

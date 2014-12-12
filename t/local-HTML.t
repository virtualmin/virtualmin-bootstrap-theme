#!/usr/bin/perl
# Test the HTML output of all cgi and html files against HTML::Lint

use strict;
use warnings;

use Test::HTML::Lint tests => 3;                      # last test to print
use Cwd;

# Some Webmin variables to allow running CGI scripts as though Webmin is running
our $no_acl_check++;
our %ENV;
$ENV{'WEBMIN_CONFIG'} ||= "/etc/webmin";
$ENV{'WEBMIN_VAR'} ||= "/var/webmin";
$ENV{'MINISERV_CONFIG'} ||= $ENV{'WEBMIN_CONFIG'}."/miniserv.conf";
$ENV{'SERVER_ROOT'} ||= "/usr/libexec/webmin";
our $trust_unknown_referers = 1;

chdir "/usr/libexec/webmin" or die "Can't change directory.";

BEGIN { push(@INC, "."); };

my @pages = ( "left.cgi",
		   "right.cgi",
	   );

foreach my $page (@pages) {
	my $content = system("$ENV{'SERVER_ROOT'}/bootstrap-theme/$page");
	print $content;
	html_ok( $content, "$page HTML is clean");
}

my @htmlpages = ( "index.html" );

foreach my $page (@htmlpages) {
	open (my $fh, "/usr/libexec/webmin/bootstrap-theme/$page") or die "Can't open file: $!\n";
	my $content = do { local $/; $fh };
	html_ok( $content, "$page HTML is clean");
}

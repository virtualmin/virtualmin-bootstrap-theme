#!/usr/local/bin/perl
# Output contents of top frame file

require "virtual-server-theme/virtual-server-theme-lib.pl";

$hasvirt = &foreign_available("virtual-server");
if ($hasvirt) {
	%vconfig = &foreign_config("virtual-server");
	}
$upperframe = $vconfig{'theme_topframe'} ||
	      $gconfig{'theme_topframe'};

&PrintHeader();
print &read_file_contents($upperframe);


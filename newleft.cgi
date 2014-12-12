#!/usr/local/bin/perl
# Show the left-side menu of Virtualmin domains, plus modules
use warnings;
use strict;

# Globals
our %gconfig;
our %in;
our %text;
our $did;
our $base_remote_user;
our %miniserv;
our %gaccess;
our $session_id;

our $trust_unknown_referers = 1;
require "bootstrap-theme/bootstrap-theme-lib.pl";
ReadParse();

popup_header("Virtualmin");

my $is_master;
# Is this user root?
if (foreign_available("virtual-server")) {
	foreign_require("virtual-server");
	$is_master = virtual_server::master_admin();
	}
elsif (foreign_available("server-manager")) {
	foreign_require("server-manager");
	$is_master = server_manager::can_action(undef, "global");
	}

# Find all left-side items from Webmin
my $sects = get_right_frame_sections();
my @leftitems = list_combined_webmin_menu($sects, \%in);
my ($lefttitle) = grep { $_->{'type'} eq 'title' } @leftitems;

use Data::Dumper;
print "<!-- leftitems = " . Dumper(@leftitems) . " -->\n";

# Default left-side mode
my $mode = $in{'mode'} ? $in{'mode'} :
	$sects->{'tab'} =~ /vm2|virtualmin|mail/ ? "items" :
	@leftitems ? "items" : "modules";

print "<section class='sidebar' role='navigation'>\n";
print "<ul class='sidebar-menu' id='side-menu'>\n";

if ($mode eq "modules") {
	# Work out what modules and categories we have
	my @cats = get_visible_modules_categories();
	my @catnames = map { $_->{'code'} } @cats;

	if ($gconfig{"notabs_${base_remote_user}"} == 2 ||
	    $gconfig{"notabs_${base_remote_user}"} == 0 && $gconfig{'notabs'}) {
		# Show modules in one list
		@leftitems = map { module_to_menu_item($_) }
				 (map { @{$_->{'modules'}} } @cats);
		}
	else {
		# Show all modules under categories
		@leftitems = ( );
		foreach my $c (@cats) {
			my $citem = { 'type' => 'cat',
				      'id' => $c->{'code'},
				      'desc' => $c->{'desc'},
				      'members' => [ ] };
			foreach my $minfo (@{$c->{'modules'}}) {
				push(@{$citem->{'members'}},
				     module_to_menu_item($minfo));
				}
			push(@leftitems, $citem);
			}
		}
	push(@leftitems, { 'type' => 'hr' });
	}

# Show system information link
push(@leftitems, { 'type' => 'item',
		   'id' => 'home',
		   'desc' => $text{'left_home'},
		   'link' => '/right.cgi',
		   'icon' => '/images/gohome.png' });

# Show refresh modules link
if ($mode eq "modules" && foreign_available("webmin")) {
	push(@leftitems, { 'type' => 'item',
			   'id' => 'refresh',
			   'desc' => $text{'main_refreshmods'},
			   'link' => '/webmin/refresh_modules.cgi',
			   'icon' => '/images/reload.png' });
	}

# Show Webmin search form
my $cansearch = $gaccess{'webminsearch'} ne '0' && !$sects->{'nosearch'};
if ($mode eq "modules" && $cansearch) {
	push(@leftitems, { 'type' => 'input',
			   'desc' => $text{'left_search'},
			   'name' => 'search',
			   'cgi' => '/webmin_search.cgi', });
	}

show_menu_items_list(\@leftitems, 0);

print "</ul>\n";
print "<section>\n";

popup_footer();

# show_menu_items_list(&list, indent)
# Actually prints the HTML for menu items
sub show_menu_items_list
{
my ($items, $indent) = @_;
foreach my $item (@$items) {
	my $icon;
	if ($item->{'type'} eq 'item') {
		# Link to some page
		my $t = $item->{'target'} eq 'new' ? '_blank' :
			$item->{'target'} eq 'window' ? '_top' : 'right';
		if ($item->{'icon'}) {
			$icon = lookup_icon(add_webprefix($item->{'icon'}));
			}
		print "<li class='leftlink'>\n";
		my $link = add_webprefix($item->{'link'});
		print "  <a href='$link' target=$t>";
		print "<i class='pull-left linkwithicon glyphicon glyphicon-$icon'></i>";
		print "$item->{'desc'}</a>\n";
		print "</li>\n";
		}
	elsif ($item->{'type'} eq 'cat') {
		# Start of a new category
		my $c = $item->{'id'};
		print "<li class='treeview'>\n";
		print "<a href='#'>";
		if ($item->{'icon'}) { print "<i class='pull-left glyphicon glyphicon-$item->{'icon'}'></i>"; }
		print "<span>$item->{'desc'}</span>";
		print "<i class='pull-right glyphicon glyphicon-chevron-left'></i>";
		print "</a>\n";
		print "<ul class='treeview-menu' id='cat$c'>\n";
		use Data::Dumper;
		print "<!-- " . Dumper($item->{'members'}) . "-->\n";
		show_menu_items_list($item->{'members'}, $indent+1);
		print "</ul></li><!-- treeview-menu cat$c -->\n";
		}
	elsif ($item->{'type'} eq 'html') {
		# Some HTML block
		print "<li class='leftlink'>",$item->{'html'},"</li>\n";
		}
	elsif ($item->{'type'} eq 'text') {
		# A line of text
		print "<li class='leftlink'>",
		      html_escape($item->{'desc'}),"</li>\n";
		}
	elsif ($item->{'type'} eq 'hr') {
		# Separator line
		print "<li class='divider'></li>\n";
		}
	elsif ($item->{'type'} eq 'menu' || $item->{'type'} eq 'input') {
		# For with an input of some kind
		print "<li class='leftlink'>";
		if ($item->{'cgi'}) {
			print "<form action='$item->{'cgi'}' target=right>\n";
			}
		else {
			print "<form>\n";
			}
		foreach my $h (@{$item->{'hidden'}}) {
			print ui_hidden(@$h);
			}
		print $item->{'desc'},"\n";
		if ($item->{'type'} eq 'menu') {
			my $sel = "";
			if ($item->{'onchange'}) {
				$sel = "window.parent.frames[1].location = ".
				       "\"$item->{'onchange'}\" + this.value";
				}
			print ui_select($item->{'name'}, $item->{'value'},
					 $item->{'menu'}, 1, 0, 0, 0,
					 "class='domainmenu' onChange='form.submit(); $sel' ");
			}
		elsif ($item->{'type'} eq 'input') {
			print ui_textbox($item->{'name'}, $item->{'value'},
					  $item->{'size'});
			}
		if ($item->{'icon'}) {
			my $icon = add_webprefix($item->{'icon'});
			#print "<input type=image src='$icon'>\n";
			}
		print "</form>\n";
		print "</li>";
		}
	elsif ($item->{'type'} eq 'title') {
		# Nothing to print here, as it is used for the tab title
		}
	}
}

# module_to_menu_item(&module)
# Converts a module to the hash ref format expected by show_menu_items_list
sub module_to_menu_item
{
my ($minfo) = @_;
return { 'type' => 'item',
	 'id' => $minfo->{'dir'},
	 'desc' => $minfo->{'desc'},
	 'link' => '/'.$minfo->{'dir'}.'/' };
}

# add_webprefix(link)
# If a URL starts with a / , add webprefix
sub add_webprefix
{
my ($link) = @_;
return $link =~ /^\// ? $gconfig{'webprefix'}.$link : $link;
}

# lookup_icon(category)
# Checks a map for which glyphicon to use for a menu category, if none, use generic
sub lookup_icon {
    my ($c) = @_;
    my %icon_map = (
        'tmpl_setting' => 'wrench',
        'tmpl_email' => 'envelope',
        'tmpl_custom' => 'cog',
        'tmpl_ip' => 'globe',
        'tmpl_check' => 'ok-sign',
        'tmpl_add' => 'plus-sign',
        'tmpl_backup' => 'hdd',
        'graph' => 'stats',
        'edit' => 'pencil',
        'group' => 'user',
        'email_go' => 'envelope',
        'page_code' => 'save',
        'page_edit' => 'edit',
        'cat_admin' => 'inbox',
        'cat_server' => 'th-list',
        'cat_logs' => 'flag',
        'cat_delete' => 'warning-sign',
        'cat_services' => 'star',
        'lang' => 'globe',
    );

    if (defined $icon_map{"$c"}) {
        return $icon_map{"$c"};
    } else {
        return "";
    }
}

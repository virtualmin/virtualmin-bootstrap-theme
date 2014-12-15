#!/usr/local/bin/perl
# Show the left-side menu of Virtualmin domains, plus modules
use warnings;
use strict;
use Cwd;
use lib cwd;


# Globals
our %gconfig;
our %in;
our %text;
our $did;
our $base_remote_user;
our %miniserv;
our %gaccess;
our $session_id;
our $charset;

our $trust_unknown_referers = 1;
require "bootstrap-theme/bootstrap-theme-lib.pl";
#require BootstrapTheme;

# If run as CGI or command line, print the HTML and exit. If loaded as a module, just initialize functions.
exit print sidebar(1, @ARGV) unless caller();

# Produce the HTML for a left hand side bar with menus
sub sidebar {
my ($CGI) = @_;
my $rv;
if ($CGI) { PrintHeader($charset); }
ReadParse();

$rv = simple_header("Virtualmin");

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

# Default left-side mode
my $mode = $in{'mode'} ? $in{'mode'} :
	$sects->{'tab'} =~ /vm2|virtualmin|mail/ ? "items" :
	@leftitems ? "items" : "modules";

$rv = "<section class='sidebar' role='navigation'>\n";
$rv .= "<ul class='sidebar-menu' id='side-menu'>\n";

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
		$rv .= "<li role='presentation' class='divider'></li>\n";
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
my $cansearch;
if ( defined $gaccess{'webminsearch'} && !$sects->{'nosearch'} ) { $cansearch++; };
if ($mode eq "modules" && $cansearch) {
	push(@leftitems, { 'type' => 'input',
			   'desc' => $text{'left_search'},
			   'name' => 'search',
			   'cgi' => '/webmin_search.cgi', });
	}

$rv .= menu_items_list(\@leftitems, 0);

$rv .= "</ul>\n";
$rv .= "</section>\n";

#$rv .= popup_footer();

return $rv;
} # sidebar

# menu_items_list(&list, indent)
# Actually prints the HTML for menu items
sub menu_items_list
{
my ($items, $indent) = @_;
my $rv;
foreach my $item (@$items) {
	my $icon;
	if ($item->{'type'} eq 'item') {
		# Link to some page
		my $t;
		if (defined $item->{'target'}) {
			$t = $item->{'target'} eq 'new' ? '_blank' : '_top';
			}
		else { $t = 'right'; }
		if (defined $item->{'icon'}) {
			$icon = lookup_icon(add_webprefix($item->{'icon'}));
			}
		$rv .= "<li class='leftlink'>\n";
		my $link = add_webprefix($item->{'link'});
		$rv .= "  <a href='$link' target=$t>";
		if ( $icon ) { $rv .= "<i class='pull-left linkwithicon glyphicon glyphicon-$icon'></i>"; }
		$rv .= "$item->{'desc'}</a>\n";
		$rv .= "</li>\n";
		}
	elsif ($item->{'type'} eq 'cat') {
		# Start of a new category
		my $c = $item->{'id'};
		$rv .= "<li class='treeview'>\n";
		$rv .= "<a href='#'>";
		if ($item->{'icon'}) { print "<i class='pull-left glyphicon glyphicon-$item->{'icon'}'></i>"; }
		$rv .= "<span>$item->{'desc'}</span>";
		$rv .= "<i class='pull-right glyphicon glyphicon-chevron-left'></i>";
		$rv .= "</a>\n";
		$rv .= "<ul class='treeview-menu' id='cat$c'>\n";
		use Data::Dumper;
		$rv .= "<!-- " . Dumper($item->{'members'}) . "-->\n";
		$rv .= menu_items_list($item->{'members'}, $indent+1);
		$rv .= "</ul></li><!-- treeview-menu cat$c -->\n";
		}
	elsif ($item->{'type'} eq 'html') {
		# Some HTML block
		$rv.= "<li class='leftlink'>" . $item->{'html'} . "</li>\n";
		}
	elsif ($item->{'type'} eq 'text') {
		# A line of text
		$rv .= "<li class='leftlink'>" . 
		      html_escape($item->{'desc'}) . "</li>\n";
		}
	elsif ($item->{'type'} eq 'hr') {
		# Separator line
		$rv .= "<li class='divider'></li>\n";
		}
	elsif ($item->{'type'} eq 'menu' || $item->{'type'} eq 'input') {
		# For with an input of some kind
		$rv .= "<li class='leftlink'>";
		if ($item->{'cgi'}) {
			$rv .= "<form action='$item->{'cgi'}' target=right>\n";
			}
		else {
			$rv .= "<form>\n";
			}
		foreach my $h (@{$item->{'hidden'}}) {
			$rv .= ui_hidden(@$h);
			}
		$rv .= $item->{'desc'}."\n" if $item->{'desc'};
		if ($item->{'type'} eq 'menu') {
			my $sel = "";
			if ($item->{'onchange'}) {
				$sel = "window.parent.frames[1].location = ".
				       "\"$item->{'onchange'}\" + this.value";
				}
			$rv .= ui_select($item->{'name'}, $item->{'value'},
					 $item->{'menu'}, 1, 0, 0, 0,
					 "class='domainmenu' onChange='form.submit(); $sel' ");
			}
		elsif ($item->{'type'} eq 'input') {
			$rv .= ui_textbox($item->{'name'}, $item->{'value'},
					  $item->{'size'});
			}
		if ($item->{'icon'}) {
			my $icon = add_webprefix($item->{'icon'});
			#print "<input type=image src='$icon'>\n";
			}
		$rv .= "</form>\n";
		$rv .= "</li>";
		}
	elsif ($item->{'type'} eq 'title') {
		# Nothing to print here, as it is used for the tab title
		}
	}
	return $rv;
}

# module_to_menu_item(&module)
# Converts a module to the hash ref format expected by menu_items_list
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

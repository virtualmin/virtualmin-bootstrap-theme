#!/usr/local/bin/perl
# Show the left-side menu of Virtualmin domains, plus modules

$trust_unknown_referers = 1;
require "virtual-server-theme/virtual-server-theme-lib.pl";
ReadParse();
@admincats = ( "tmpl", "create", "backup" );
%gaccess = get_module_acl(undef, "");

popup_header("Virtualmin");
print "<script type='text/javascript' src='$gconfig{'webprefix'}/unauthenticated/toggleview.js'></script>\n";

# Find out which modules we have
$hasvirt = foreign_available("virtual-server");
if ($hasvirt) {
	%minfo = get_module_info("virtual-server");
	%vconfig = foreign_config("virtual-server");
	$hasvirt = 0 if ($minfo{'version'} < 2.99);
	}
$hasmail = foreign_available("mailbox");
$hasvm2 = foreign_available("server-manager");

# Show the hosting provider logo
if ($hasvirt) {
	foreign_require("virtual-server", "virtual-server-lib.pl");
	$is_master = virtual_server::master_admin();
	}
if ($hasvm2) {
	foreign_require("server-manager", "server-manager-lib.pl");
	}
if (defined(&virtual_server::get_provider_link)) {
	(undef, $image, $link) = virtual_server::get_provider_link();
	}
if (!$image && defined(&server_manager::get_provider_link)) {
        (undef, $image, $link) = server_manager::get_provider_link();
        }
if ($image) {
	print "<a href='$link' target='_new'>" if ($link);
	print "<center><img src='$image' alt=''></center>";
	print "</a><br>\n" if ($link);
	}

# Work out the user's email address
if ($hasmail) {
	&foreign_require("mailbox", "mailbox-lib.pl");
	($fromaddr) = mailbox::split_addresses(
			mailbox::get_preferred_from_address());
	}

# Work out current mode
$sects = get_right_frame_sections();
$product = get_product_name();
$mode = $in{'mode'} ? $in{'mode'} :
	$sects->{'tab'} ? $sects->{'tab'} :
	$hasvirt ? "virtualmin" :
	$hasvm2 ? "vm2" :
	$hasmail ? "mail" : $product;

if ($mode eq "virtualmin" && $hasvirt) {
	# Get and sort the domains
	@alldoms = virtual_server::list_domains();
	@doms = virtual_server::list_visible_domains();

	# Work out which domain we are editing
	if (defined($in{'dom'})) {
		$d = virtual_server::get_domain($in{'dom'});
		}
	elsif (defined($in{'dname'})) {
		$d = virtual_server::get_domain_by("dom", $in{'dname'});
		if (!$d) {
			# Couldn't find domain by name, search by user instead
			$d = virtual_server::get_domain_by(
				"user", $in{'dname'}, "parent", "");
			}
		}
	elsif ($sects && $sects->{'dom'}) {
		$d = virtual_server::get_domain($sects->{'dom'});
		$d = undef if (!virtual_server::can_edit_domain($d));
		}

	# Make sure the selected domain is in the menu .. may not be for
	# alias domains if they are hidden
	if ($d && virtual_server::can_edit_domain($d)) {
		my @ids = map { $_->{'id'} } @doms;
		if (&indexof($d->{'id'}, @ids) < 0) {
			push(@doms, $d);
			}
		}
	@doms = virtual_server::sort_indent_domains(\@doms);

	# Fall back to first owned by this user, or first in list
	$d ||= virtual_server::get_domain_by("user", $remote_user,
					      "parent", "");
	$d ||= $doms[0];
	}
else {
	$d = { 'id' => $in{'dom'} };
	}
$did = $d ? $d->{'id'} : undef;

if ($mode eq "vm2" && $hasvm2) {
	# Get and sort managed servers
	@servers = server_manager::list_available_managed_servers_sorted();
	@allservers = server_manager::list_managed_servers();
	($server) = grep { $_->{'id'} eq $in{'sid'} } @servers;
	if (!$server && $sects && $sects->{'server'} ne '') {
		($server) = grep { $_->{'id'} eq $sects->{'server'} } @servers;
		}
	$server ||= $servers[0];
	}
$sid = $server ? $server->{'id'} : undef;

# Show virtualmin / folders / webmin mode selector
@has = ($hasvirt ? ( "virtualmin" ) : ( ),
	$hasmail ? ( "mail" ) : ( ),
	$hasvm2 ? ( "vm2" ) : ( ),
	$sects->{'nowebmin'} == 1 ||
	  ($sects->{'nowebmin'} == 2 && !$is_master) &&
	  $mode ne $product ? ( ) : ( $product ));
if (@has > 1) {
	print "<div class='mode'>";
	foreach $m (@has) {
		if ($m ne $mode) {
			print "<a href='left.cgi?mode=$m&amp;dom=$did'>";
			}
		else {
			print "<b>";
			}
		print "<img src='images/$m-small.png' alt='$m'> ".
		      $text{'has_'.$m};
		if ($m ne $mode) {
			print "</a>\n";
			}
		else {
			print "</b>\n";
			}
		}
	print "</div>";
	}

print "<div class='sidebar-nav'>\n";
if (($mode eq "webmin" || $mode eq "usermin") &&
    $gaccess{'webminsearch'} ne '0') {
	# Left form is for searching Webmin
	print "<form class='form-search' action='webmin_search.cgi' target='right' style='display:inline'>\n";
	$doneform = 1;
	}
elsif ($hasvirt || $hasvm2) {
	# Left form is for changing domain / server
	print "<form action=left.cgi style='display:inline'>\n";
	$doneform = 1;
	}
elsif ($mode eq "mail") {
	# Left form is for searching a mail folder
	@folders = mailbox::list_folders_sorted();
	$df = $mailbox::userconfig{'default_folder'};
	$dfolder = $df ? mailbox::find_named_folder($df, \@folders) :
			 $folders[0];
	print "<script>\n";
	print "function GetMailFolder()\n";
	print "{\n";
	print "var url = ''+window.parent.frames[1].location;\n";
	print "var qm = url.indexOf('?');\n";
	print "if (qm > 0) {\n";
	print "    var params = url.substring(qm+1).split('&');\n";
	print "    for(var i=0; i<params.length; i++) {\n";
	print "        var nv = params[i].split('=');\n";
	print "        if (nv[0] == 'id') {\n";
	print "            if (nv[1] != '1' && url.indexOf('view_mail.cgi') <= 0) {\n";
	print "                document.forms[0].id.value = unescape(nv[1]);\n";
	print "                }\n";
	print "            }\n";
	print "        else if (nv[0] == 'folder') {\n";
	print "            document.forms[0].folder.value = nv[1];\n";
	print "            }\n";
	print "        }\n";
	print "    }\n";
	print "}\n";
	print "</script>\n";
	print "<form class='form-search' action='mailbox/mail_search.cgi' target='right' onSubmit='GetMailFolder()' style='display:inline'>\n";
	print ui_hidden("simple", 1);
	print ui_hidden("folder", $dfolder->{'index'});
	print ui_hidden("id", undef);
	$doneform = 1;
	}

# Show login and Virtualmin access level
if ($fromaddr) {
	# Show email address and real name
	print $fromaddr->[1],"<br>\n" if ($fromaddr->[1]);
	print $fromaddr->[0],"\n";
	}
else {
	# Show login
	print text('left_login', $remote_user),"<br>\n";
	}
if (@doms) {
	# Show Virtualmin login level
	$level = virtual_server::master_admin() ? $text{'left_master'} :
		 virtual_server::reseller_admin() ? $text{'left_reseller'} :
		 virtual_server::extra_admin() ? $text{'left_extra'} :
		 $virtual_server::single_domain_mode ? $text{'left_single'} :
						       $text{'left_user'};
	print "$level<br>\n";
	}
elsif ($hasvm2) {
	# Show Cloudmin login level
	$level = $server_manager::access{'owner'} ? $text{'left_owner'}
						  : $text{'left_master2'};
	print "$level<br>\n";
	}
print "<hr>\n";

$selwidth = (get_left_frame_width() - 70)."px";
if ($mode eq "virtualmin" && @doms) {
	# Show Virtualmin servers this user can edit, plus links for various
	# functions within each
	print "<div class='domainmenu'>\n";
	print ui_hidden("mode", $mode);
	if ($virtual_server::config{'display_max'} &&
	    @doms > $virtual_server::config{'display_max'}) {
		# Show text field for domain name
		print $text{'left_dname'},
		      ui_textbox("dname", $d ? $d->{'dom'} : $in{'dname'}, 15);
		}
	else {
		# Show menu of domains
		my $sel;
		if (-r "$root_directory/virtual-server/summary_domain.cgi") {
			$sel = "; window.parent.frames[1].location = ".
			       "\"virtual-server/summary_domain.cgi?dom=\"+this.value";
			}
		print ui_select("dom", $did,
			[ map { [ $_->{'id'},
				  ("&nbsp;&nbsp;" x $_->{'indent'}).
				  virtual_server::shorten_domain_name($_),
				  $_->{'disabled'} ?
					"style='font-style:italic'" : "" ] }
			      @doms ],
			1, 0, 0, 0,
			"onChange='form.submit() $sel'".
			"style='width:$selwidth'");
		}
	print "<input type='image' src='images/ok.gif' alt='' class='goArrow'>\n";
	foreach $a (@admincats) {
		print ui_hidden($a, 1),"\n" if ($in{$a});
		}
	print "</div>\n";
	if (!$d) {
		if ($in{'dname'}) {
			print "\n";
			}
		}

	# Show domain creation link, if possible
	if (virtual_server::can_create_master_servers() ||
	    virtual_server::can_create_sub_servers()) {
		($rdleft, $rdreason, $rdmax) =
			virtual_server::count_domains("realdoms");
                ($adleft, $adreason, $admax) =
			virtual_server::count_domains("aliasdoms");
		if ($rdleft || $adleft) {
			print_virtualmin_link(
				{ 'url' => "virtual-server/domain_form.cgi?".
					   "generic=1&amp;gparent=$d->{'id'}",
				  'title' => $text{'left_generic'} },
				'leftlink');
			}
		else {
			print "<div class='leftlink'><b>",
			      text('left_nomore'),"</b></div>\n";
			}
		}

	if (!$d) {
		goto nodomain;
		}

	# Get actions and menus from Virtualmin
	@buts = virtual_server::get_all_domain_links($d);

	# Show 'objects' category actions at top level
	my @incat = grep { $_->{'cat'} eq 'objects' } @buts;
	foreach my $b (@incat) {
		print_virtualmin_link($b, 'leftlink');
		}

	# Show others by category (except those for creation, which appear
	# at the top)
	print "<div id='cats-accordion' class='accordion'>\n";
	print "<div class='accordion-group'>\n";
	my @cats = unique(map { $_->{'cat'} } @buts);
	foreach my $c (@cats) {
		next if ($c eq 'objects' || $c eq 'create');
		my @incat = grep { $_->{'cat'} eq $c } @buts;
		print_category_opener("cat_$c", \@cats,
				       $incat[0]->{'catname'},
		                       'cats-accordion');
		#print "<div class='itemhidden' id='cat_$c'>\n";
		my @incatsort = grep { !$_->{'nosort'} } @incat;
		if (@incatsort) {
			@incat = sort { ($a->{'title'} || $a->{'desc'}) cmp
                                        ($b->{'title'} || $b->{'desc'})} @incat;
			}
		foreach my $b (@incat) {
			print_virtualmin_link($b);
			}
		print_category_closer();
		}

	print "</div></div>\n"; # accordion-group accordion
	print "<hr>\n";
	nodomain:
	}
elsif ($mode eq "virtualmin") {
	# No domains
	print "<div class='leftlink'>";
	if (@alldoms) {
		print $text{'left_noaccess'};
		}
	else {
		print $text{'left_nodoms'};
		}
	print "</div>\n";

	# Show domain creation link
	if (virtual_server::can_create_master_servers() ||
	    virtual_server::can_create_sub_servers()) {
		print "<div class='leftlink'><a href='virtual-server/domain_form.cgi?generic=1' target=right>$text{'left_generic'}</a></div>\n";
		}
	}
elsif ($mode eq "vm2" && @servers) {
	# Show managed servers
	print "<div class='domainmenu'>\n";
	print ui_hidden("mode", $mode);
	print ui_select("sid", $sid,
		[ map { [ $_->{'id'}, ("&nbsp;&nbsp;" x $_->{'indent'}).
				      shorten_hostname($_) ] } @servers ],
		1, 0, 0, 0,
		"onChange='form.submit()' style='width:$selwidth'");
	print "<input type='image' src='images/ok.gif' alt='' class='goArrow'>\n";
	print "</div>\n";
	}
elsif ($mode eq "vm2") {
	# No servers
	print "<div class='leftlink'>";
	if (@allservers) {
		print $text{'left_novm2access'};
		}
	else {
		print $text{'left_novm2'};
		}
	print "</div>\n";
	}

if ($mode eq "virtualmin") {
	# Show Virtualmin global links
	my @buts = virtual_server::get_all_global_links();
	my @tcats = unique(map { $_->{'cat'} } @buts);
	print "<div id='global-accordion' class='accordion'>\n";
        print "<div class='accordion-group'>\n";

	foreach my $tc (@tcats) {
		my @incat = grep { $_->{'cat'} eq $tc } @buts;
		if ($tc) {
			# Show under section
			print_category_opener("tmpl_".$tc, \@tcats,
					       $incat[0]->{'catname'},
			                       'global-accordion');
			foreach my $l (@incat) {
				print_virtualmin_link($l);
				}
			print_category_closer();
			}
		else {
			# Show with icons
			foreach my $l (@incat) {
				print_virtualmin_link($l, 'aftericon', 1);
				}
			}
		}
		print"</div></div>\n";
	}

if ($mode eq "mail") {
	# Work out possible folder heirarchies
	foreach $f (@folders) {
		$sep = $f->{'name'} =~ /\// ? "/" : "\\.";
		$sepchar = $f->{'name'} =~ /\// ? "/" : ".";
		@w = split($sep, $f->{'name'});
		if (@w > 1) {
			$f->{'heir'} = join($sepchar, @w[0..$#w-1]);
			$heir{$f->{'heir'}} = 1;
			$heirdepth{$f->{'heir'}} = scalar(@w);
			$heircount{$f->{'heir'}}++;
			}
		}
	%heiropen = map { $_, 1 } split(/\0/, $in{'heiropen'});
	$heiropen{""} = 1;

	# Show mail folders
	foreach $f (@folders) {
		$fid = mailbox::folder_name($f);

		# Work out if a star is needed
		$star = $f->{'type'} == 6 &&
			$mailbox::special_folder_id &&
			$f->{'id'} == $mailbox::special_folder_id ?
			  "<img src='mailbox/images/special.gif' alt=special>" :
			  "";

		# Add unread message count
		$umsg = "";
		if (defined(mailbox::should_show_unread) &&
		    mailbox::should_show_unread($f)) {
			local ($c, $u) = mailbox::mailbox_folder_unread($f);
			$umsg = " ($u)" if ($u);
			}

		# Check if folder name is hierarchial
		if ($heir{$f->{'heir'}} == 1 && $heircount{$f->{'heir'}} > 1) {
			# Find parent category, skip if not open
			$pheir = $f->{'heir'};
			if ($pheir =~ /\//) {
				$pheir =~ s/\/[^\/]+$//;
				}
			elsif ($pheir =~ /\./) {
				$pheir =~ s/\.[^\.]+$//;
				}
			else {
				$pheir = undef;
				}
			next if ($pheir && !$heiropen{$pheir});

			print "<div class='leftlink'>";
			%copyopen = %heiropen;
			if ($heiropen{$f->{'heir'}}) {
				$img = "open.gif";
				delete($copyopen{$f->{'heir'}});
				}
			else {
				$img = "closed.gif";
				$copyopen{$f->{'heir'}} = 1;
				}
			$heirstr = join("&", map { "heiropen=".&urlize($_) }
						 keys %copyopen);
			$indent = "&nbsp;&nbsp;&nbsp;" x
				  ($heirdepth{$f->{'heir'}} - 2);
			print $indent.
			      "<a href='left.cgi?$heirstr'>",
			      "<img src=images/$img></a>",
			      html_escape($f->{'heir'});
			print "</div>\n";
			$heir{$f->{'heir'}} = 2;
			}

		next if ($f->{'heir'} && !$heiropen{$f->{'heir'}});

		# Show actual folder name
		$fname = $f->{'name'};
		$indent = "";
		if ($heir{$f->{'heir'}} && $heircount{$f->{'heir'}} > 1) {
			$fname =~ s/^\Q$f->{'heir'}\E.//;
			$indent = "&nbsp;&nbsp;&nbsp;" x
				  $heirdepth{$f->{'heir'}};
			}
		print "<div class='leftlink'>$indent",
		      "<a href='mailbox/index.cgi?id=".&urlize($fid)."'".
		      " target=right>$star$fname$umsg</a></div>\n";
		}

	# Show search box
	print "<div class='leftlink'>$text{'left_search'} ",
	      ui_textbox("search", undef, 15),"</div>\n";

	# Show manage folders, mail preferences and change password links
	%mconfig = %mailbox::config;
	if (!%mconfig) {
		%mconfig = foreign_config("mailbox");
		}
	print "<hr>\n";

	# Folder list link
	print "<div class='linkwithicon'><img src='images/mail-small.gif' alt=''>\n";
	$fprog = $mconfig{'mail_system'} == 4 &&
		 get_webmin_version() >= 1.227 ? "list_ifolders.cgi"
					       : "list_folders.cgi";
	print "<div class='aftericon'><a target=right href='mailbox/$fprog'>$text{'left_folders'}</a></div></div>\n";

	print "<div class='linkwithicon'><img src='images/address-small.gif' alt=''>\n";
	print "<div class='aftericon'><a target=right href='mailbox/list_addresses.cgi'>$text{'left_addresses'}</a></div></div>\n";

	# Preferences for read mail link
	if (!$mconfig{'noprefs'}) {
		print "<div class='linkwithicon'><img src='images/usermin-small.gif' alt=''>\n";
		print "<div class='aftericon'><a target=right href='uconfig.cgi?mailbox'>$text{'left_prefs'}</a></div></div>\n";
		}

	# Mail filter link, if installed and if not over-ridden
	if (foreign_available("filter")) {
		foreign_require("filter", "filter-lib.pl");
		if (!defined(filter::no_user_procmailrc) ||
		    !filter::no_user_procmailrc()) {
			# Forwarding link, unless it isn't available
			if (defined(filter::can_simple_forward) &&
			    filter::can_simple_forward()) {
				print "<div class='linkwithicon'><img src='images/forward.gif' alt=''>\n";
				print "<div class='aftericon'><a target=right href='filter/edit_forward.cgi'>$text{'left_forward'}</a></div></div>\n";
				}

			# Autoreply link, unless it isn't available
			if (defined(filter::can_simple_autoreply) &&
			    filter::can_simple_autoreply()) {
				print "<div class='linkwithicon'><img src='images/autoreply.gif' alt=''>\n";
				print "<div class='aftericon'><a target=right href='filter/edit_auto.cgi'>$text{'left_autoreply'}</a></div></div>\n";
				}

			# Filter mail link
			print "<div class='linkwithicon'><img src='images/filter.gif' alt=''>\n";
			print "<div class='aftericon'><a target=right href='filter/'>$text{'left_filter'}</a></div></div>\n";
			}
		}

	# Change password link
	if (foreign_available("changepass")) {
		print "<div class='linkwithicon'><img src='images/pass.gif' alt=''>\n";
		print "<div class='aftericon'><a target=right href='changepass/'>$text{'left_pass'}</a></div></div>\n";
		}
	}

if ($mode eq "vm2" && $server) {
	$status = $server->{'status'};
	$t = $server->{'manager'};

	# Show status of current server
	$statusmsg = server_manager::describe_status($server, 1, 0);
	print "<div class='leftlink'>",text('left_vm2status', $statusmsg),
	      "</div>\n";

	# Get actions for this system provided by Cloudmin
	@actions = grep { $_ && keys(%$_) > 0 }
			server_manager::get_server_actions($server);
	foreach $b (@actions) {
		$b->{'desc'} = $text{'leftvm2_'.$b->{'id'}}
			if ($text{'leftvm2_'.$b->{'id'}});
		}

	# Work out action categories, and show those under each
	my @cats = sort { $a cmp $b } &unique(map { $_->{'cat'} } @actions);
	print "<div id='action-accordion' class='accordion'>\n";
	print "<div class='accordion-group'>\n";

	foreach my $c (@cats) {
		my @incat = grep { $_->{'cat'} eq $c } @actions;
		if ($c) {
			# Start of opener
			print_category_opener("cat_$c", \@cats,
				$server_manager::text{'cat_'.$c} ||
				$incat[0]->{'catname'},
			        'action-accordion');
			#print "<div class='itemhidden' id='cat_$c'>\n";
			}
		foreach my $b (sort { $b->{'priority'} <=> $a->{'priority'} ||
				      ($a->{'title'} || $a->{'desc'}) cmp
				      ($b->{'title'} || $b->{'desc'})} @incat) {
			if ($b->{'link'} =~ /\//) {
				$url = $b->{'link'};
				}
			elsif ($b->{'link'}) {
				$url = "server-manager/$b->{'link'}";
				}
			else {
				$url = "server-manager/save_serv.cgi?id=$server->{'id'}&amp;$b->{'id'}=1";
				}
			$title = $b->{'title'} || $b->{'desc'};
			# XXX class=leftlink
			print_category_link($url, $title,
				     undef, undef, $b->{'target'}, !$c);
			}
		if ($c) {
			# End of opener
			print_category_closer();
			}
		}
	}
	print "</div></div>\n";

if ($mode eq "vm2") {
	# Get global settings, add Module Config
	@vservers = grep { $_->{'status'} eq 'virt' } @servers;
	($glinks, $gtitles, $gicons, $gcats) =
		server_manager::get_global_links(scalar(@vservers));
	$glinks = [ map { "server-manager/$_" } @$glinks ];
	$gcats = [ map { $_ || "settings" } @$gcats ];
	if (!$server_manager::access{'noconfig'}) {
		push(@$glinks, "config.cgi?server-manager");
		push(@$gtitles, $text{'left_vm2config'});
		push(@$gicons, undef);
		push(@$gcats, 'settings');
		}

	# Show global settings, under categories
	@ugcats = unique(@$gcats);
	if (@ugcats) {
		print "<hr>\n";
		}
	print "<div id='vm2cats-accordion' class='accordion'>\n";
	print "<div class='accordion-group'>\n";

	foreach $c (@ugcats) {
		print_category_opener($c, undef,
			       $server_manager::text{'cat_'.$c} ||
			       $text{'left_vm2'.$c},
		               'ugcats-accordion');
		#print "<div class='itemhidden' id='$c'>\n";
		for($i=0; $i<@$glinks; $i++) {
			next if ($gcats->[$i] ne $c);
			print_category_link($glinks->[$i], $gtitles->[$i]);
			}
		print_category_closer();
		}

	# Show add / create links
	@alllinks = server_manager::get_available_create_links();
	if (@alllinks) {
		print "<hr>\n";
		}
	@createlinks = grep { $_->{'create'} } @alllinks;
	@addlinks = grep { !$_->{'create'} } @alllinks;
	if (scalar(@createlinks) + scalar(@addlinks) <= 3) {
		# Collapse to one section
		@newlinks = ( @createlinks, @addlinks );
		@createlinks = @addlinks = ( );
		}
	foreach $ml ([ "create", \@createlinks ],
		     [ "add", \@addlinks ],
		     [ "new", \@newlinks ]) {
		($m, $l) = @$ml;
		if (@$l == 1) {
			$c = $l->[0];
			$form = $c->{'link'} ? $c->{'link'} :
				$c->{'create'} ? 'create_form.cgi' :
					         'add_form.cgi';
		print "<div class='leftlink'><a href='server-manager/$form?type=$c->{'type'}' target=right>$c->{'desc'}</a></div><br>\n";
			}
		elsif (@$l) {
			print_category_opener($m, undef,
					       $text{'left_vm2'.$m});
			#print "<div class='itemhidden' id='$m'>\n";
			foreach $c (@$l) {
				$form = $c->{'link'} ? $c->{'link'} :
				        $c->{'create'} ? 'create_form.cgi' :
						         'add_form.cgi';
				print_category_link(
				    "server-manager/$form?".
				    "type=$c->{'type'}", $c->{'desc'});
				}
			print_category_closer();
			}
		}

	# Show list of all systems
	print "<div class='linkwithicon'><img src='images/vm2-small.png' alt=''><b><div class='aftericon'><a href='server-manager/index.cgi' target=right>$text{'left_vm2'}</a></b></div></div>\n";
	print "</div></div>\n";
	}

if ($mode eq "webmin" || $mode eq "usermin") {
	# Work out what modules and categories we have
	@cats = get_visible_modules_categories();
	@catnames = map { $_->{'code'} } @cats;
	print "<div id='webmin-accordion' class='accordion'>\n";
	print "<div class='accordion-group'>\n";

	if ($gconfig{"notabs_${base_remote_user}"} == 2 ||
	    $gconfig{"notabs_${base_remote_user}"} == 0 && $gconfig{'notabs'}) {
		# Show modules in one list
		foreach $minfo (map { @{$_->{'modules'}} } @cats) {
			print_category_link("$minfo->{'dir'}/",
				     $minfo->{'desc'},
				     undef,
				     undef,
				     $minfo->{'noframe'} ? "_top" : "", 1);
			}
		}
	else {
		# Show all modules under categories
		foreach $c (@cats) {
			# Show category opener, plus modules under it
			print_category_opener($c->{'code'}, \@catnames,
				$c->{'unused'} ?
				"<font color=#888888>$c->{'desc'}</font>" :
				$c->{'desc'},
			        'webmin-accordion');
			#print "<div class='itemhidden' id='$c->{'code'}'>";
			foreach $minfo (@{$c->{'modules'}}) {
				print_category_link("$minfo->{'dir'}/",
					     $minfo->{'desc'},
					     undef,
					     undef,
					     $minfo->{'noframe'} ? "_top" : "");
				}
			print_category_closer();
			}
		}
	print"</div></div>\n";

	print "<hr>\n";
	}

# Show system information link
print "<div class='linkwithicon'><img src='images/gohome.png' alt=''>\n";
if ($mode eq "vm2") {
	$sparam = $server ? "&$server->{'id'}" : "";
	print "<div class='aftericon'><a target=right href='right.cgi?open=system&open=vm2servers&open=vm2limits&open=updates&open=owner$sparam'>$text{'left_home3'}</a></div></div>\n";
	}
elsif (get_product_name() eq 'usermin') {
	print "<div class='aftericon'><a target=right href='right.cgi?open=system&open=common'>$text{'left_home2'}</a></div></div>\n";
	}
else {
	$dparam = $d ? "&amp;dom=$d->{'id'}" : "";
	print "<div class='aftericon'><a target=right href='right.cgi?open=system&auto=status&open=updates&open=reseller$dparam'>$text{'left_home'}</a></div></div>\n";
	}

# Show refresh modules like
if ($mode eq "webmin" && foreign_available("webmin")) {
        print "<div class='linkwithicon'><img src='images/reload.png' alt=''>\n";
        print "<div class='aftericon'><a target=right href='webmin/refresh_modules.cgi'>$text{'main_refreshmods'}</a></div></div>\n";
	}

# Show logout link
&get_miniserv_config(\%miniserv);
if ($miniserv{'logout'} && !$ENV{'SSL_USER'} && !$ENV{'LOCAL_USER'} &&
    $ENV{'HTTP_USER_AGENT'} !~ /webmin/i) {
	print "<div class='linkwithicon'><img src='images/stock_quit.png' alt=''>\n";
	if ($main::session_id) {
		print "<div class='aftericon'><a target=_top href='session_login.cgi?logout=1'>$text{'main_logout'}</a></div>";
		}
	else {
		print "<div class='aftericon'><a target=_top href='switch_user.cgi'>$text{'main_switch'}</a></div>";
		}
	print "</div>\n";
	}

# Show link back to original Webmin server
if ($ENV{'HTTP_WEBMIN_SERVERS'}) {
	print "<div class='linkwithicon'><img src='images/webmin-small.gif' alt=''>\n";
	print "<div class='aftericon'><a target=_top href='$ENV{'HTTP_WEBMIN_SERVERS'}'>$text{'header_servers'}</a></div></div>";
	}


if (($mode eq "webmin" || $mode eq "usermin") &&
    $gaccess{'webminsearch'} ne '0') {
	# Show module/help search form
	print $text{'left_search'},"&nbsp;";
	print ui_textbox("search", undef, 15);
	}

print "</form>\n" if ($doneform);

# Search form for Virtualmin modules only
if (($mode eq "virtualmin" && $hasvirt ||
     $mode eq "vm2" && $hasvm2) && $gaccess{'webminsearch'} ne '0') {
	print "<form action=webmin_search.cgi target=right style='display:inline'>\n";
	print "<div class='leftlink'>$text{'left_search'} ",
	      ui_textbox("search", undef, 15),"</div>\n";
	@searchmods = ( );
	if ($mode eq "virtualmin") {
		push(@searchmods, "virtual-server", @virtual_server::plugins);
		}
	if ($mode eq "vm2") {
		push(@searchmods, "server-manager", @server_manager::plugins);
		}
	foreach my $m (@searchmods) {
		print ui_hidden("mod", $m);
		}
	print ui_hidden("title", $text{'left_vmsearch'});
	print ui_hidden("dom", $d->{'id'}) if ($d);
	print "</form>\n";
	}

footer();

# print_category_opener(name, &allcats, label)
# Prints out an open/close twistie for some category
sub print_category_opener
{
my ($c, $cats, $label, $parent) = @_;
my @others = grep { $_ ne $c } @$cats;
my $others = join("&", map { $_."=".$in{$_} } @others);
$others = "&$others" if ($others);
$others .= "&amp;dom=$did";
$others .= "&amp;mode=$mode";
$label = $c eq "others" ? $text{'left_others'} : $label;

# Show link to close or open catgory
print "<div class='accordion-heading'>\n";
print "<a class='accordion-toggle' data-toggle='collapse' data-parent='#$parent' data-target='#$c'> $label </a>\n";
#print "<a href=\"javascript:toggleview('$c','toggle$c')\" id='toggle$c'><img border='0' src='images/closed.gif' alt='[+]'></a>\n";
#print "<div class='aftericon'><a href=\"javascript:toggleview('$c','toggle$c')\" id='toggletext$c'><font color='#000000'>$label</font></a></div></div>\n";
print "</div>\n";
print "<div id='$c' class='accordion-body collapse'>\n";
print "  <div class='accordion-inner'>\n";
}

sub print_category_closer
{
print "</div></div>\n";
}

sub print_category_link
{
print category_link(@_);
}

sub category_link
{
my ($link, $label, $image, $noimage, $target, $noindent) = @_;
$target ||= "right";
return "<div class='leftlink'>" .
       "<a target='$target' href='$link'>$label</a></div>\n";
}

sub print_virtualmin_link
{
my ($l, $cls, $icon) = @_;
my $t = $l->{'target'} || "right";
if ($icon) {
	print "<div class='linkwithicon'><img src='images/$l->{'icon'}.png' alt=''>\n";
	}
print "<div class='$cls'>" if $cls;
print "<b>" if ($l->{'icon'} eq 'index');
print "<a href='$l->{'url'}' target=$t>$l->{'title'}</a>";
print "</b>" if ($l->{'icon'} eq 'index');
print "</div>" if $cls;
if ($icon) {
	print "</div>";
	}
print "\n";
}

sub shorten_hostname
{
my ($server) = @_;
return $server->{'short_host'} if ($server->{'short_host'});
my $show = $server->{'host'};
my $rv;
my $name_max = 20;
if (length($show) > $name_max) {
	# Show first and last max/2 chars, with ... between
	local $s = int($name_max / 2);
	$rv = substr($show, 0, $s)."...".substr($show, -$s);
	}
else {
	$rv = $show;
	}
$rv =~ s/ /&nbsp;/g;
return $rv;

}


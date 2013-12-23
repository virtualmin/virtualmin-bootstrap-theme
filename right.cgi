#!/usr/local/bin/perl
# Show server or domain information

$trust_unknown_referers = 1;
require "bootstrap-theme/bootstrap-theme-lib.pl";
&ReadParse();
use Time::Local;

# Work out system capabilities. Level 3 = usermin, 2 = domain owner,
# 1 = reseller, 0 = master, 4 = Cloudmin system owner
($hasvirt, $level, $hasvm2) = get_virtualmin_user_level();
%text = &load_language($current_theme);
%text = ( &load_language('virtual-server'), %text );
$bar_width = 100;
if ($hasvirt && $in{'dom'}) {
	$defdom = virtual_server::get_domain($in{'dom'});
	}

# Check for wizard redirect
if ($hasvirt && defined(&virtual_server::wizard_redirect)) {
	$redir = &virtual_server::wizard_redirect();
	if ($redir) {
		&redirect($redir);
		return;
		}
	}

# Work out which sections are open by default
foreach $o (split(/\0/, $in{'open'})) {
	push(@open, $o);
	}
foreach $o (split(/\0/, $in{'auto'})) {
	push(@open, $o);
	push(@auto, $o);
	}
if (!defined($in{'open'})) {
	@open = ( 'system', 'reseller', 'status', 'updates', 'common',
		  'vm2limits' );
	@auto = ( 'status' );
	}
%open = map { $_, indexof($_, @auto) >= 0 ? 2 : 1 } @open;

popup_header(undef);

# XXX disabled. This logic needs to move into index
if ( 0 && $hasvirt || $hasvm2) {
	# Show link for editing what appears
	$sects = get_right_frame_sections();
	if (!$sects->{'global'} ||
	    $hasvirt && virtual_server::master_admin() ||
	    $hasvm2) {
		print "<div align=right>";
		@links = ( "<a href='/edit_right.cgi' target='right'>$text{'right_edit'}</a>" );
		if ($hasvirt && virtual_server::master_admin()) {
			# Refresh collected info
			push(@links, "<a href='/right.cgi' target='right'>".
				     "$text{'right_recollect'}</a>");
			}
		@overlays = &list_virtualmin_theme_overlays();
		if (@overlays) {
			# Change theme overlay
			push(@links, "<a href='edit_overlay.cgi'>".
				     "$text{'right_overlay'}</a>");
			}
		if ($hasvirt) {
			# Virtualmin docs
			$doclink = get_virtualmin_docs($level);
			push(@links, "<a href='$doclink' target=_new>$text{'right_virtdocs'}</a>");
			}
		if ($hasvm2) {
			# Cloudmin docs
			$doclink = get_vm2_docs($level);
			push(@links, "<a href='$doclink' target=_new>$text{'right_vm2docs'}</a>");
			}
		if ($hasvirt && $virtual_server::config{'docs_link'}) {
			# Custom Virtualmin docs
			push(@links, "<a href='".
				$virtual_server::config{'docs_link'}.
				"' target=_new>".
				($virtual_server::config{'docs_text'} ||
				 $text{'right_virtdocs2'})."</a>");
			}
		if ($hasvm2 && $server_manager::config{'docs_link'}) {
			# Custom Cloudmin docs
			push(@links, "<a href='".
				$server_manager::config{'docs_link'}.
				"' target=_new>".
				($server_manager::config{'docs_text'} ||
				 $text{'right_virtdocs2'})."</a>");
			}
		print ui_links_row(\@links);
		print "</div>\n";
		$shown_config_link = 1;
		}
	}

# Check for custom URL
if ($sects->{'alt'} && !$in{'noalt'}) {
	$url = $sects->{'alt'};
	if ($shown_config_link) {
		# Show in iframe, so that the config link is visible
		print "<iframe src='$url' width=100% height=95% frameborder=0 ",
		      "marginwidth=0 marginheight=0>\n";
		}
	else {
		# Redirect whole frame
		print "<script type='text/javascript'>\n";
		print "document.location = '$url';\n";
		print "</script>\n";
		}
	footer();
	exit;
	}

if ($hasvirt) {
	# Check Virtualmin licence
	if (defined(&virtual_server::warning_messages)) {
		print virtual_server::warning_messages();
		}
	else {
		print virtual_server::licence_warning_message();
		}

	# See if module config needs to be checked
	if (virtual_server::need_config_check() &&
	    virtual_server::can_check_config()) {
		my $check = ui_form_start("/virtual-server/check.cgi");
		$check .= "<p><b>$text{'index_needcheck'}</b></p><p>\n";
		$check .= ui_submit($text{'index_srefresh'});
		$check .= ui_form_end();
        print (ui_alert_box($check, "warning"));
		}
	}

if ($hasvm2) {
	# Check Cloudmin licence or other warnings
	if (defined(&server_manager::warning_messages)) {
		print server_manager::warning_messages();
		}
	else {
		print server_manager::licence_error_message();
		}
	}

# Show Webmin notifications, if supported
if (foreign_check("webmin")) {
	foreign_require("webmin", "webmin-lib.pl");
	if (defined(&webmin::get_webmin_notifications)) {
		@notifs = webmin::get_webmin_notifications(1);
		}
	if (@notifs) {
		print ui_alert_box(@notifs, "warning");
		}
	}

if ($level == 0) {		# Master admin
	# Show Virtualmin master admin info
	$hasposs = foreign_check("security-updates");
	$canposs = foreign_available("security-updates");
	if ($hasvm2) {
		# Check if Cloudmin has collected own info
		my $me = &server_manager::get_managed_server(0);
		if ($me) {
			$meinfo = &server_manager::get_server_collected($me);
			}
		}
	if ($hasvirt) {
		# Get from Virtualmin's collected info
		$info = virtual_server::get_collected_info();
		@poss = $info ? @{$info->{'poss'}} : ( );
		@allposs = $info ? @{$info->{'allposs'}} : ( );
		@inst = $info ? @{$info->{'inst'}} : ( );
		}
	elsif ($meinfo && $meinfo->{'poss'}) {
		# Use own collected info
		@poss = @{$meinfo->{'poss'}};
		@allposs = @{$meinfo->{'allposs'}};
		@inst = @{$meinfo->{'inst'}};
		}
	elsif ($hasposs) {
		# Get possible updates directly from security-updates module
		foreign_require("security-updates", "security-updates-lib.pl");
		@poss = security_updates::list_possible_updates();
		if (defined(&security_updates::list_possible_installs)){
			@inst = security_updates::list_possible_installs();
			}
		}

	if (!$sects->{'nosystem'}) {
		# Show general system information
		print ui_hidden_table_start($text{'right_systemheader'},
		      "width=100%", 4,
			  "system", $open{'system'});

		# Host and login info
		$ip = $info && $info->{'ips'} ? $info->{'ips'}->[0]->[0] :
					&to_ipaddress(get_system_hostname());
		$ip = " ($ip)" if ($ip);
		print ui_table_row($text{'right_host'},
				   get_system_hostname().$ip, 1,
		      ["width='15%'", "width='35%'"]);

		if ($gconfig{'os_version'} eq '*') {
			print ui_table_row($text{'right_os'}, $gconfig{'real_os_type'}, 1,
			      ["width='15%'", "width='35%'"]); 
			}
		else {
			print ui_table_row($text{'right_os'},
			      "$gconfig{'real_os_type'} $gconfig{'real_os_version'}",
			      1, ["width='15%'", "width='35%'"]);
			}

		# Webmin/Usermin version
		if (get_product_name() eq 'webmin') {
			print ui_table_row($text{'right_webmin'}, get_webmin_version(),
			      1, ["width='15%'", "width='35%'"]);
			}
		else {
			print ui_table_row($text{'right_usermin'}, get_webmin_version(),
			      1, ["width='15%'", "width='35%'"]);
			}

		# Virtualmin / Cloudmin version
		if ($hasvirt) {
			print ui_table_row($text{'right_virtualmin'},
			      $virtual_server::module_info{'version'} . " " .
			      ($virtual_server::module_info{'virtualmin'} eq 'gpl'
			      ? 'GPL' : 'Pro'),
			      1, ["width='15%'", "width='35%'"]);
			}
		if ($hasvm2) {
			print ui_table_row($text{'right_vm2'},
			      $server_manager::module_info{'version'}
			      , 1, ["width='15%'", "width='35%'"]);
			}

		# Theme version
		my %current_theme_info = get_theme_info($current_theme);
		print ui_table_row($text{'right_themever'},
		      $current_theme_info{'version'}
		      , 1, ["width='15%'", "width='35%'"]);

		# System time and uptime
		my $tm = make_date(time());
		if (&foreign_available("time")) {
			$tm = "<a href=time/>$tm</a>";
			}
		&foreign_require("proc");
		my $uptime;
		my ($d, $h, $m) = &proc::get_system_uptime();
		if ($d) {
			$uptime = &text('right_updays', $d, $h, $m);
			}
		elsif ($m) {
			$uptime = &text('right_uphours', $h, $m);
			}
		elsif ($m) {
			$uptime = &text('right_upmins', $m);
			}
		$tm .= " , ".$uptime if ($uptime);
		print ui_table_row($text{'right_time'}, $tm
		      , 1, ["width='15%'", "width='35%'"]);

		# Kernel type
		if ($k = $info->{'kernel'}) {
			print ui_table_row($text{'right_kernel'},
			      text('right_kernelon', $k->{'os'},
			      $k->{'version'}, $k->{'arch'})
			      , 1, ["width='15%'", "width='35%'"]);
			}

		# Load and memory info
		{
			my @c;
			if ($info->{'load'}) {
				@c = @{$info->{'load'}};
				}
			elsif (foreign_check("proc")) {
				foreign_require("proc", "proc-lib.pl");
				if (defined(&proc::get_cpu_info)) {
					@c = proc::get_cpu_info();
					}
				}
			if (@c) {
				print ui_table_row($text{'right_cpu'},
				      text('right_loadgraph',
                      $c[0], history_link("load", 1),
                      $c[1], history_link("load5", 1),
                      $c[2], history_link("load15", 1))
				      , 1, ["width='15%'", "width='35%'"]);
				}
			}
		# Running processes
		if ($info->{'procs'}) {
			if (foreign_available("proc")) {
				print ui_table_row($text{'right_procs'},
				      "<a href=proc/>$info->{'procs'}</a>"
				      . " " . history_link("procs", 1)
				      , 1, ["width='15%'", "width='35%'"]);
				}
			else {
				print ui_table_row($text{'right_procs'}, $info->{'procs'}
				      . history_link("procs", 1)
				      , 1, ["width='15%'", "width='35%'"]);	
				}
			}

		# Memory used
		if ($info->{'mem'}) {
			@m = @{$info->{'mem'}};
			}
		elsif (foreign_check("proc")) {
			foreign_require("proc", "proc-lib.pl");
			if (defined(&proc::get_memory_info)) {
				@m = proc::get_memory_info();
				}
			}
		if (@m && $m[0]) {
			print ui_table_row($text{'right_real'},
			      text('right_used',
			           nice_size($m[0]*1024), nice_size(($m[0]-$m[1])*1024))
			      . " " . history_link("memused", 1)
			      . "<br>" . bar_chart($m[0], $m[0]-$m[1], 1)
			      , 1, ["width='15%'", "width='35%'"]);
			}
		if (@m && $m[2]) {
			print ui_table_row($text{'right_virt'},
			      text('right_used',
			           nice_size($m[2]*1024),
			           nice_size(($m[2]-$m[3])*1024))
			      . " " . history_link("swapused", 1)
			      . "<br>" . bar_chart($m[2], $m[2]-$m[3], 1)
			      , 1, ["width='15%'", "width='35%'"]);
			}

		# Disk space on local drives
		if ($info->{'disk_total'}) {
			($total, $free) = ($info->{'disk_total'},
					   $info->{'disk_free'});
			}
		elsif (foreign_check("mount")) {
			foreign_require("mount", "mount-lib.pl");
			if (defined(&mount::local_disk_space)) {
				($total, $free) = mount::local_disk_space();
				}
			}
		if ($total) {
			print ui_table_row($text{'right_disk'},
			      text('right_used', nice_size($total),
			           nice_size($total-$free))
			      . " " . history_link("diskused", 1)
			      . "<br>" . bar_chart($total, $total-$free, 1)
			      , 1, ["width='15%'", "width='35%'"]);
			}

		@pkgmsgs = ( );
		if (!$sects->{'noupdates'} && $hasposs && !@poss && $canposs) {
			# Re-assure the user that everything is up to date
			push(@pkgmsgs, &text('right_upall',
				     "security-updates/index.cgi?mode=all"));
			}
		if (!$sects->{'noupdates'} && $hasposs && @inst && $canposs) {
			# Tell the user about extra packages
			push(@pkgmsgs, text('right_upinst', scalar(@inst),
				     "security-updates/index.cgi?mode=new"));
			}
		if (!$sects->{'noupdates'} && $hasposs && @allposs &&
		    scalar(@allposs) != scalar(@poss) && $canposs) {
			# Tell the user about non-virtualmin packages
			push(@pkgmsgs, &text('right_upsys', scalar(@allposs),
			     "security-updates/index.cgi?mode=updates&all=1"));
			}
		if (@pkgmsgs) {
			print ui_table_row($text{'right_pkgupdesc'},
			      join("<br>\n", @pkgmsgs), 3);
			}

		print ui_hidden_table_end("system");
		}

	# Check for package updates
	if (!$sects->{'noupdates'} && $hasposs && @poss && $canposs) {
		# Show updates section
		print ui_hidden_table_start($text{'right_updatesheader'},
		      "width=100%", 1,
              "updates", $open{'updates'});

		print ui_form_start("security-updates/update.cgi");
		print text(
			@poss > 1 ? 'right_upcount' : 'right_upcount1',
			scalar(@poss),
			'security-updates/index.cgi?mode=updates'),"<p>\n";
		print ui_columns_start([ $text{'right_upname'},
					  $text{'right_updesc'},
					  $text{'right_upver'} ], "80%");
		%sinfo = get_module_info("security-updates");
		foreach $p (@poss) {
			print ui_columns_row([
			 $p->{'name'}, $p->{'desc'}, $p->{'version'} ]);
			print ui_hidden("u",
			  $sinfo{'version'} >= 1.7 && $p->{'update'} ?
			     $p->{'update'}."/".$p->{'system'} : $p->{'name'});
			}
		print ui_columns_end();
		print ui_form_end([ [ undef, $text{'right_upok'} ] ]);
		print ui_hidden_table_end("updates");
		}

	# Show Virtualmin feature statuses
	if ($hasvirt && !$sects->{'nostatus'} && $info->{'startstop'} &&
	    virtual_server::can_stop_servers()) {
		my @ss = @{$info->{'startstop'}};
		my $mid = int((@ss-1) / 2);
		my $status_open = $open{'status'};
		if ($status_open == 2) {
			# Open if something is down
			@down = grep { !$_->{'status'} } @ss;
			$status_open = @down ? 1 : 0;
			}
		print ui_hidden_table_start($text{'right_statusheader'},
		      "width=100%", 4, "status", $status_open);
		print "<div class='row'><div class='col-md-6'>\n";
		print status_grid(@ss[0 .. $mid]);
		print "</div><div class='col-md-6'>\n";
		print status_grid(@ss[$mid+1 .. $#ss]);
		print "</div></div>\n";
		print ui_hidden_table_end('rightstat');
		}

	# New features for master admin
	show_new_features(0);

	if ($hasvirt && !$sects->{'novirtualmin'} && $info->{'fcount'}) {
		# Show Virtualmin information
		print ui_hidden_table_start($text{'right_virtheader'},
		      "width=100%", 1, "virtualmin", $open{'virtualmin'});
		print "<table>\n";
		my $i = 0;
		foreach my $f (@{$info->{'ftypes'}}) {
			my $cur = int($info->{'fcount'}->{$f});
			my $extra = $info->{'fextra'}->{$f};
			my $max = $info->{'fmax'}->{$f};
			my $hide = $info->{'fhide'}->{$f};
			print "<tr class='ui_form_pair'>\n" if ($i%2 == 0);
			print "<td class='ui_form_label' width=25%>",$text{'right_f'.$f},"</td>\n";
			my $hlink = $f eq "doms" || $f eq "users" ||
			       $f eq "aliases" ? history_link($f, 1) : "";
			if ($extra < 0 || $hide) {
				print "<td class='ui_form_value' width=25%>",$cur," ",$hlink,
				      "</td>\n";
				}
			else {
				print "<td class='ui_form_value' width=25%>",
					text('right_out', $cur, $max)," ",
					$hlink,"</td>\n";
				}
			print "</tr>\n" if ($i%2 == 1);
			$i++;
			}
		print "</table>\n";
		print ui_hidden_table_end("virtualmin");
		}

	if ($hasvirt && !$sects->{'noquotas'} && $info->{'quota'} &&
	    @{$info->{'quota'}}) {
		# Show quota graphs
		print ui_hidden_table_start($text{'right_quotasheader'},
		      "width=100%", 1,
		      "quotas",
		      $open{'quotas'} || &any_over_quota($info->{'quota'}));
		show_quotas_info($info->{'quota'}, $info->{'maxquota'});
		print ui_hidden_table_end("quotas");
		}

	if ($hasvirt && !$sects->{'nobw'} && 
	    $virtual_server::config{'bw_active'}) {
		# Show bandwidth graph by domain
		my @doms = virtual_server::list_domains();
		my @bwdoms = grep { !$_->{'parent'} &&
		                    defined($_->{'bw_usage'}) } @doms;

		print ui_hidden_table_start($text{'right_bwheader'},
		      "width=100%", 1, "bw",
		      $open{'bw'} || &any_over_bandwidth(\@doms));
		if (@bwdoms) {
			show_bandwidth_info(\@doms);
			}
		else {
			print ui_table_row(undef, $text{'right_bwnone'}, 2);
			}
		print ui_hidden_table_end("bw");
		}

	if ($hasvirt && !$sects->{'noips'} && $info->{'ips'}) {
		# Show virtual IPs used
		print ui_hidden_table_start($text{'right_ipsheader'},
		      "width=100%", 1, "ips", $open{'ips'});
		print "<table>\n";
		foreach my $ipi (@{$info->{'ips'}}) {
			print "<tr class='ui_form_pair'>\n";
			print "<td class='ui_form_label' width=30%>$ipi->[0]</td>\n";
			print "<td>",$ipi->[1] eq 'def' ? $text{'right_defip'} :
				     $ipi->[1] eq 'reseller' ?
					text('right_reselip', $ipi->[2]) :
				     $ipi->[1] eq 'shared' ?
					$text{'right_sharedip'} :
					$text{'right_ip'},"</td>\n";
			if ($ipi->[3] == 1) {
				print "<td class='ui_form_value'><tt>$ipi->[4]</tt></td>\n";
				}
			else {
				print "<td class='ui_form_value'>",text('right_ips', $ipi->[3]),	
				      "</td>\n";
				}
			print "</tr>\n";
			}
		print "</table>\n";
		if ($info->{'ipranges'}) {
			# Show IP ranges for allocation
			print &ui_hr();
			print "<table>\n";
			foreach my $r (@{$info->{'ipranges'}}) {
				print "<tr class='ui_form_pair'>\n";
				print "<td class='ui_form_label' width=30%>",
				      $r->[0],"</td>\n";
				print "<td class='ui_form_value'>",
				      &text('right_iprange', $r->[1], $r->[2]),
				      "</td>\n";
				print "</tr>\n";
				}
			print "</table>\n";
			}
		print ui_hidden_table_end("ips");
		}

	# Show system programs information section
	if ($hasvirt && !$sects->{'nosysinfo'} && $info->{'progs'} &&
	    virtual_server::can_view_sysinfo()) {
		print ui_hidden_table_start($text{'right_sysinfoheader'},
		      "width=100%", 1, "sysinfo", $open{"sysinfo"});
		print "<table>\n";
		@info = @{$info->{'progs'}};
		for($i=0; $i<@info; $i++) {
			print "<tr class='ui_form_pair'>\n" if ($i%2 == 0);
			print "<td class='ui_form_label'><b>$info[$i]->[0]</b></td>\n";
			print "<td class='ui_form_value'>$info[$i]->[1]</td>\n";
			print "</tr>\n" if ($i%2 == 1);
			}
		print "</table>\n";
		print ui_hidden_table_end("sysinfo");
		}

	# Show Cloudmin server summary by status and by type
	if ($hasvm2) {
		print ui_hidden_table_start($text{'right_vm2serversheader'},
		      "width=100%", 4, "vm2servers", $open{'vm2servers'},
		      [ "width=30%" ]);
		@servers = server_manager::list_managed_servers();
		show_vm2_servers(\@servers, 1);
		print ui_hidden_table_end('vm2servers');
		}

	# Show licenses
	@lics = ( );
	if ($hasvirt && 
	    read_env_file($virtual_server::virtualmin_license_file,
			   \%vserial) &&
	    $vserial{'SerialNumber'} ne 'GPL') {
		# Show Virtualmin serial and key
		push(@lics, [ $text{'right_vserial'},
			      $vserial{'SerialNumber'} ]);
		push(@lics, [ $text{'right_vkey'},
			      $vserial{'LicenseKey'} ]);
		push(@lbuts, [ "/virtual-server/licence.cgi",
			       $text{'right_vlcheck'} ]);

		# Add allowed domain counts
		($dleft, $dreason, $dmax, $dhide) =
			virtual_server::count_domains("realdoms");
		push(@lics, [ $text{'right_vmax'},
		      $dmax <= 0 ? $text{'right_vunlimited'} : $dmax ]);
		push(@lics, [ $text{'right_vleft'},
		      $dleft < 0 ? $text{'right_vunlimited'} : $dleft ]);

		# Add allowed system counts
		my %lstatus;
		read_file($virtual_server::licence_status, \%lstatus);
		if ($lstatus{'used_servers'}) {
			push(@lics, [ $text{'right_smax'},
			    $lstatus{'servers'} || $text{'right_vunlimited'} ]);
			push(@lics, [ $text{'right_sused'},
			    $lstatus{'used_servers'} ]);
			}

		# Show license expiry date
		if ($lstatus{'expiry'} =~ /^203[2-8]-/) {
			push(@lics, [ $text{'right_expiry'},
				      $text{'right_expirynever'} ]);
			}
		elsif ($lstatus{'expiry'}) {
			push(@lics, [ $text{'right_expiry'},
				      $lstatus{'expiry'} ]);
			$ltm = &parse_license_date($lstatus{'expiry'});
			if ($ltm) {
				$days = int(($ltm - time()) / (24*60*60));
				push(@lics, [ $text{'right_expirydays'},
				    $days < 0 ? &text('right_expiryago', -$days)
			       		      : $days ]);
				}
			}
		$hasvirt_lic = 1;
		}

	if ($hasvm2 &&
	    read_env_file($server_manager::licence_file, \%sserial) &&
	    $sserial{'SerialNumber'} ne 'GPL') {
		if ($hasvirt_lic) {
			push(@lics, [ undef, &ui_hr(), 4 ]);
			}

		# Show Cloudmin serial 
		push(@lics, [ $text{'right_sserial'},
			      $sserial{'SerialNumber'} ]);
		push(@lics, [ $text{'right_skey'},
			      $sserial{'LicenseKey'} ]);
		push(@lbuts, [ "/server-manager/licence.cgi",
			       $text{'right_slcheck'} ]);

		# Add allowed system counts
		my %lstatus;
		read_file($server_manager::licence_status, \%lstatus);
		@allservers = grep { &server_manager::is_virtual_server($_) }
                                   &server_manager::list_managed_servers();
		push(@lics, [ $text{'right_vm2max'},
			      $lstatus{'servers'} > 0 ?
				$lstatus{'servers'} :
				$text{'right_vunlimited'} ]);
		push(@lics, [ $text{'right_vm2used'},
				scalar(@allservers) ]);

		# Show license expiry date
		if ($lstatus{'expiry'} =~ /^203[2-8]-/) {
			push(@lics, [ $text{'right_expiry'},
				      $text{'right_expirynever'} ]);
			}
		elsif ($lstatus{'expiry'}) {
			push(@lics, [ $text{'right_expiry'},
				      $lstatus{'expiry'} ]);
			$ltm = &parse_license_date($lstatus{'expiry'});
			if ($ltm) {
				$days = int(($ltm - time()) / (24*60*60));
				push(@lics, [ $text{'right_expirydays'},
				    $days < 0 ? &text('right_expiryago', -$days)
			       		      : $days ]);
				}
			}
		$hasvm2_lic = 1;
		}

	if (@lics) {
		local $tb = undef;
		local $cb = undef;
		$h = $hasvirt_lic && $hasvm2_lic ?
			$text{'right_licenceheader_virt_vm2'} :
		     $hasvirt_lic ?
			$text{'right_licenceheader'} :
		        $text{'right_licenceheader_vm2'};
		print ui_hidden_table_start(
		      $h, "width=100%", 4, "licence", $open{'licence'});
		foreach my $l (@lics) {
			print ui_table_row(@$l);
			}
		print ui_table_row(undef,
		    ui_links_row(
			[ map { "<a href='$_->[0]'>$_->[1]</a>" } @lbuts ]), 4);
		print ui_hidden_table_end('licence');
		}
	}
elsif ($level == 1) {		# Reseller
	# Show a reseller info about his domains
	@doms = grep { virtual_server::can_edit_domain($_) }
		     virtual_server::list_domains();
	$info = virtual_server::get_collected_info();
	@qdoms = grep { virtual_server::can_edit_domain($_->[0]) }
		      @{$info->{'quota'}};

	# Domain and feature counts
	if (!$sects->{'novirtualmin'}) {
		print ui_hidden_table_start($text{'right_resellerheader'},
		      'width=100%', 1, 'reseller', $open{'reseller'});
		show_domains_info(\@doms);
		print ui_hidden_table_end('reseller');
		}

	# Show quotas across reseller-owned domains
	if (!$sects->{'noquotas'} && @qdoms) {
		print ui_hidden_table_start($text{'right_quotasheader'},
		      'width=100%', 1, 'quotas',
		      $open{'quotas'} || &any_over_quota(\@qdoms));
		show_quotas_info(\@qdoms, $info->{'maxquota'});
		print ui_hidden_table_end('quotas');
		}

	# Show bandwidth across reseller-owned domains
	if (!$sects->{'nobw'} && $virtual_server::config{'bw_active'}) {
		my @bwdoms = grep { !$_->{'parent'} &&
		                    defined($_->{'bw_usage'}) } @doms;
		print ui_hidden_table_start($text{'right_bwheader'},
		      'width=100%', 1, 'bw',
		      $open{'bw'} || &any_over_bandwidth(\@bwdoms));
		if (@bwdoms) {
			show_bandwidth_info(\@doms);
			}
		else {
			print ui_table_row(undef, $text{'right_bwnone'}, 2);
			}
		print ui_hidden_table_end();
		}

	# New features for reseller
	show_new_features(0);
	}
elsif ($level == 2) {		# Domain owner
	# Show a server owner info about one domain
	$ex = virtual_server::extra_admin();
	if ($ex) {
		$d = virtual_server::get_domain($ex);
		}
	else {
		$d = virtual_server::get_domain_by(
			"user", $remote_user, "parent", "");
		}

	print ui_table_start($text{'right_header3'}, "width=100%", 4);

	print ui_table_row("<b>$text{'right_login'}</b>",
	      $remote_user);

	print ui_table_row("<b>$text{'right_from'}</b>",
	      $ENV{'REMOTE_HOST'});

	if ($hasvirt) {
		print ui_table_row("<b>$text{'right_virtualmin'}</b>",
		      $virtual_server::module_info{'version'});
		}
	else {
		print ui_table_row("<b>$text{'right_virtualmin'}</b>",
		      $text{'right_not'});
		}

	$dname = defined(&virtual_server::show_domain_name) ?
		&virtual_server::show_domain_name($d) : $d->{'dom'};
	print ui_table_row("<b>$text{'right_dom'}</b>",
	      $dname);

	@subs = ( $d, virtual_server::get_domain_by("parent", $d->{'id'}) );
	@reals = grep { !$_->{'alias'} } @subs;
	@mails = grep { $_->{'mail'} } @subs;
	($sleft, $sreason, $stotal, $shide) =
		virtual_server::count_domains("realdoms");
	if ($sleft < 0 || $shide) {
		print ui_table_row("<b>$text{'right_subs'}</b>",
		      scalar(@reals));
		}
	else {
		print ui_table_row("<b>$text{'right_subs'}</b>",
		      text('right_of', scalar(@reals), $stotal));
		}

	@aliases = grep { $_->{'alias'} } @subs;
	if (@aliases) {
		($aleft, $areason, $atotal, $ahide) =
			virtual_server::count_domains("aliasdoms");
		if ($aleft < 0 || $ahide) {
			print ui_table_row("<b>$text{'right_aliases'}</b>",
			      scalar(@aliases));
			}
		else {
			print ui_table_row("<b>$text{'right_aliases'}</b>",
			      text('right_of', scalar(@aliases), $atotal));
			}
		}

	# Users and aliases info
	$users = virtual_server::count_domain_feature("mailboxes", @subs);
	($uleft, $ureason, $utotal, $uhide) =
		virtual_server::count_feature("mailboxes");
	$msg = @mails ? $text{'right_fusers'} : $text{'right_fusers2'};
	if ($uleft < 0 || $uhide) {
		print ui_table_row("<b>$msg</b>",
		      $users);
		}
	else {
		print ui_table_row("<b>$msg</b>",
		      text('right_of', $users, $utotal));
		}

	if (@mails) {
		$aliases = virtual_server::count_domain_feature("aliases",
								@subs);
		($aleft, $areason, $atotal, $ahide) =
			virtual_server::count_feature("aliases");
		if ($aleft < 0 || $ahide) {
			print ui_table_row("<b>$text{'right_faliases'}</b>",
			      $aliases);
			}
		else {
			print ui_table_row("<b>$text{'right_faliases'}</b>",
			      text('right_of', $aliases, $atotal));
			}
		}

	# Databases
	$dbs = virtual_server::count_domain_feature("dbs", @subs);
	($dleft, $dreason, $dtotal, $dhide) =
		virtual_server::count_feature("dbs");
	if ($dleft < 0 || $dhide) {
		print ui_table_row("<b>$text{'right_fdbs'}</b>",
		      $dbs);
		}
	else {
		print ui_table_row("<b>$text{'right_fdbs'}</b>",
		      text('right_of', $dbs, $dtotal));
		}

	if (!$sects->{'noquotas'} &&
	    virtual_server::has_home_quotas()) {
		# Disk usage for all owned domains
		$homesize = virtual_server::quota_bsize("home");
		$mailsize = virtual_server::quota_bsize("mail");
		($home, $mail, $db) = virtual_server::get_domain_quota($d, 1);
		$usage = $home*$homesize + $mail*$mailsize + $db;
		$limit = $d->{'quota'}*$homesize;
		if ($limit) {
			print &ui_table_row($text{'right_quota'},
				text('right_of', nice_size($usage),
				     &nice_size($limit)), 3);
			print &ui_table_row(" ",
				bar_chart_three($limit, $usage-$db, $db,
						$limit-$usage), 3);
			}
		else {
			print &ui_table_row($text{'right_quota'},
				nice_size($usage), 3);
			}
		}

	if (!$sects->{'nobw'} &&
	    $virtual_server::config{'bw_active'} && $d->{'bw_limit'}) {
		# Bandwidth usage and limit
		print &ui_table_row($text{'right_bw'},
		   &text('right_of', &nice_size($d->{'bw_usage'}),
			&text(
			'edit_bwpast_'.$virtual_server::config{'bw_past'},
			&nice_size($d->{'bw_limit'}),
			$virtual_server::config{'bw_period'})), 3);
		print &ui_table_row(" ",
		   &bar_chart($d->{'bw_limit'}, $d->{'bw_usage'}, 1), 3);
		}

	print ui_table_end();

	# New features for domain owner
	show_new_features(0);
	}
elsif ($level == 3) {		# Usermin
	# Show user's information
	print ui_hidden_table_start($text{'right_header5'},
				    "width=100%", 4, "system", $open{'system'});

	# Login name and real name
	print ui_table_row($text{'right_login'}, $remote_user);
	@uinfo = getpwnam($remote_user);
	if ($uinfo[6]) {
		$uinfo[6] =~ s/,.*$// if ($uinfo[6] =~ /,.*,/);
		print ui_table_row($text{'right_realname'},
			&html_escape($uinfo[6]));
		}

	# Host and login info
	print ui_table_row($text{'right_host'},
		&get_display_hostname());

	print ui_table_row($text{'right_os'},
		$gconfig{'os_version'} eq '*' ? $gconfig{'real_os_type'} :
			"$gconfig{'real_os_type'} $gconfig{'real_os_version'}");

	# Usermin version
	print ui_table_row($text{'right_usermin'},
		&get_webmin_version());

	# System time
	$tm = &make_date(time());
	print ui_table_row($text{'right_time'}, $tm);

	# Disk quotas
	if (&foreign_installed("quota")) {
		&foreign_require("quota", "quota-lib.pl");
		$n = &quota::user_filesystems($remote_user);
		$usage = 0;
		$quota = 0;
		for($i=0; $i<$n; $i++) {
			if ($quota::filesys{$i,'hblocks'}) {
				$quota += $quota::filesys{$i,'hblocks'};
				$usage += $quota::filesys{$i,'ublocks'};
				}
			elsif ($quota::filesys{$i,'sblocks'}) {
				$quota += $quota::filesys{$i,'sblocks'};
				$usage += $quota::filesys{$i,'ublocks'};
				}
			}
		if ($quota) {
			$bsize = undef;
			if (defined(&quota::quota_block_size)) {
				$bsize = &quota::quota_block_size();
				}
			$bsize ||= $quota::config{'block_size'};
			$bsize ||= 1024;
			print ui_table_row($text{'right_uquota'},
				text('right_out',
					&nice_size($usage*$bsize),
					&nice_size($quota*$bsize)), 3);
			print ui_table_row(" ",
				bar_chart($quota, $usage, 1), 3);
			}
		}
	print ui_hidden_table_end();

	# Common modules
	@commonmods = grep { &foreign_available($_) }
			   ( "filter", "changepass", "gnupg", "file", "mysql",
			     "postgresql", "datastore" );
	if (@commonmods) {
		print ui_hidden_table_start($text{'right_header7'},
			"width=100%", 2, $open{'common'});
		foreach $mod (@commonmods) {
			%minfo = &get_module_info($mod);
			print ui_table_row($minfo{'desc'},
				"<a href='$mod/'>".
				($text{'common_'.$mod} || $minfo{'longdesc'}).
				"</a>");
			}
		print ui_hidden_table_end();
		}
	}
elsif ($level == 4) {
	# Show a Cloudmin system owner information about his systems
	print ui_hidden_table_start($text{'right_ownerheader'},
			"width=100%", 4, "owner", $open{'owner'},
		        [ "width=30%" ]);

	print ui_table_row($text{'right_login'}, $remote_user);
	print ui_table_row($text{'right_from'}, $ENV{'REMOTE_HOST'});
	print ui_table_row($text{'right_vm2'}
	      , $server_manager::module_info{'version'});
	print ui_table_row($text{'right_vm2real'}
	      , $server_manager::access{'real'});
	print ui_table_row($text{'right_vm2email'}
	      , $server_manager::access{'email'});

	@servers = &server_manager::list_available_managed_servers_sorted();
	if (@servers == 1) {
		# Show primary system here
		$s = $servers[0];
		if (&server_manager::can_action($s, "view")) {
			print ui_table_row("<b>$text{'right_vm2one'}</b>"
			      , "<a href='server-manager/edit_serv.cgi?id=$s->{'id'}'>$s->{'host'}</a>");
			}
		else {
			print ui_table_row("<b>$text{'right_vm2one'}</b>"
			      , $s->{'host'});
			}
		}

	print ui_hidden_table_end();

	# New features for domain owner
	show_new_features(0);

	# Show a list of his systems
	if (@servers > 1) {
		print ui_hidden_table_start($text{'right_vm2serversheader'},
		      "width=100%", 4, "vm2servers", $open{'vm2servers'},
		      [ "width=30%" ]);
		show_vm2_servers(\@servers, 1);
		print ui_hidden_table_end('vm2servers');
		}

	# Show limits and counts
	if (defined(&server_manager::get_owner_limits) &&
	    &server_manager::supports_plans()) {
		$limits = &server_manager::get_owner_limits();
		$plan = &server_manager::get_owner_plan();
		if ($limits) {
			print ui_hidden_table_start(
			    $text{'right_vm2limitsheader'},
			    "width=100%", 4, "vm2limits", $open{'vm2limits'},
			    [ "width=30%", undef, "width=30%" ]);
			show_vm2_limits($limits, $plan);
			print ui_hidden_table_end('vm2servers');
			}
		}
	}

# See if any plugins have defined sections
if ($hasvirt) {
	foreach $s (&list_right_frame_sections()) {
		next if (!$s->{'plugin'});
		next if ($sects->{'no'.$s->{'name'}});
		print ui_hidden_table_start($s->{'title'}, "width=100%",
		      1, $s->{'name'}, $s->{'status'});
		print $s->{'html'};
		print ui_hidden_table_end($s->{'name'});
		}
	}

footer();

# status_grid(@services)
# Returns HTML for a table of service statuses and actions
sub status_grid
{
my @services = @_;
my $rv;

$rv = ui_columns_start([ $text{'right_status_service'}
      , $text{'right_status_up'}
      , $text{'right_status_actions'} ]);

foreach my $status (@services) {
	my $label;
	# Manage link and stats? 
	if ($status->{'links'} && @{$status->{'links'}}) {
		foreach my $l (@{$status->{'links'}}) {
			if ($l->{'manage'}) {
				$label = "<a href='$l->{'link'}'>$status->{'name'}</a>";
				}
			elsif ($l->{'stat'}) {
				#print history_link($l->{'stat'}, 1);
				}
			}
		}
		$label = $status->{'name'} if (!$label);
		# Start or stop button?
	my $action = ($status->{'status'} ? "stop_feature.cgi" :
	              "start_feature.cgi");
	my $action_icon = ($status->{'status'} ?
	   "<img src='images/stop.png' alt=$status->{'desc'} />" :
	   "<img src='images/start.png' alt=$status->{'desc'} />");
	my $action_link = "<a href='virtual-server/$action?"
	   . "feature=$status->{'feature'}"
	   . "&redirect=/right.cgi'"
	   . " title='$status->{'desc'}'>"
	   . "$action_icon</a>";

	# Restartable?			
	my $restart_link = ($status->{'status'}
	   ? "<a href='virtual-server/restart_feature.cgi?"
	     . "feature=$status->{'feature'}"
	     . "&redirect=/right.cgi'"
	     . " title='$status->{'restartdesc'}'>"
	     . "<img src='images/reload.png'"
	     . "alt='$status->{'restartdesc'}'></a>\n"
	   : ""); # Nothing, if not running

	$rv .= ui_columns_row([$label,
	      (!$status->{'status'} ?
	      "<img src='images/down.gif' alt='Stopped' title='Stopped' />" :
	      "<img src='images/up.gif' alt='Running' title='Running' />")
	      , $action_link
	      . "&nbsp;" . $restart_link]);
	}

$rv .= ui_columns_end();

return $rv;
}

# bar_chart(total, used, blue-rest)
# Returns HTML for a bar chart of a single value
sub bar_chart
{
my ($total, $used, $blue) = @_;
my $rv;
# XXX Fixme: We need span sr-only for accessibility
my $used_value = int($bar_width*$used/$total)+1;
$rv .= sprintf "<div class='progress'><div class='progress-bar' role='progressbar' aria-valuenow='$used_value' aria-valuemin='0' aria-valuemax='100' style='width: $used_value\%;'> <span class='sr-only'>$used_value% Used</span> </div>";
#if ($blue) {
#  $rv .= sprintf "<div class='bar bar-success' style='width: %s%%;' ></div>",
#    $bar_width - int($bar_width*$used/$total)-1;
#  }
$rv .= "</div>\n";
return $rv;
}

# bar_chart_three(total, used1, used2, used3)
# Returns HTML for a bar chart of three values, stacked
sub bar_chart_three
{
my ($total, $used1, $used2, $used3) = @_;
my $rv;
my $w1 = int($bar_width*$used1/$total)+1;
my $w2 = int($bar_width*$used2/$total);
my $w3 = int($bar_width*$used3/$total);
my $w4 = int($bar_width - $w1 - $w2 - $w3);
$rv .= "<div class='progress'>\n";
if ($w1) {$rv .= sprintf "<div class='progress-bar progress-bar-success' aria-valuenow='%s' aria-valuemin='0' aria-valuemax='100' style='width: %s%%;'> </div>", $w1;}
if ($w2) {$rv .= sprintf "<div class='progress-bar progress-bar-info' aria-valuenow='%s' aria-valuemin='0' aria-valuemax='100' style='width: %s%%;'> </div>", $w2;}
if ($w3) {$rv .= sprintf "<div class='progress-bar progress-bar-warning' aria-valuenow='%s' aria-valuemin='0' aria-valuemax='100' style='width: %s%%;'> </div>", $w3;}
#if ($w4) {$rv .= sprintf "<div class='bar bar-danger' style='width: %s%%;'> </div>", $w4;}
$rv .= "</div>";
return $rv;
}

# show_domains_info(&domains)
# Given a list of domains, show summaries of feature usage
sub show_domains_info
{
# Count features for specified domains
local @doms = @{$_[0]};
local %fcount = map { $_, 0 } @virtual_server::features;
$fcount{'doms'} = 0;
foreach my $f (@virtual_server::features,
	       'doms', 'dbs', 'mailboxes', 'aliases', 'quota', 'bw') {
	$fcount{$f} = &virtual_server::count_domain_feature($f, @doms);
	}

# Show counts for features, including maxes
$bsize = &virtual_server::has_home_quotas() ?
		&virtual_server::quota_bsize("home") : undef;
print "<table width=100%>\n";
my $i = 0;
foreach my $f ("doms", "dns", "web", "ssl", "mail",
	       "dbs", "mailboxes", "aliases", "quota", "bw") {
	local $cur = int($fcount{$f});
	next if ($cur < 0);
	local ($extra, $reason, $max, $hide) =
		&virtual_server::count_feature($f);
	print "<tr class='ui_form_pair'>\n" if ($i%2 == 0);
	print "<td class='ui_form_label' width=25%>",
	      $text{'right_f'.$f},"</td>\n";
	local $hlink = $f eq "doms" || $f eq "users" || $f eq "aliases" ?
		&history_link($f, 1) : "";
	if ($f eq "bw") {
		$cur = &nice_size($cur);
		$max = &nice_size($max);
		}
	elsif ($f eq "quota" && $bsize) {
		$cur = &nice_size($cur * $bsize);
		$max = &nice_size($max * $bsize);
		}
	if ($extra < 0 || $hide) {
		print "<td class='ui_form_value' width=25%>",
		      $cur," ",$hlink,"</td>\n";
		}
	else {
		print "<td class='ui_form_value' width=25%>",
		      &text('right_out', $cur, $max)," ",$hlink,"</td>\n";
		}
	print "</tr>\n" if ($i%2 == 1);
	$i++;
	}

print "</table>\n";
}

sub any_over_quota
{
local ($quota) = @_;
foreach my $q (@$quota) {
	return 1 if ($q->[2] && $q->[1]+$q->[3] >= $q->[2]);
	}
return 0;
}

# show_quotas_info(&quotas, maxquota)
# Show disk usage by various domains
sub show_quotas_info
{
local ($quota, $maxquota) = @_;
local @quota = @$quota;
local $max = $sects->{'max'} || $default_domains_to_show;
if (@quota) {
	# If showing by percent used, limit to those with a limit
	if ($sects->{'qshow'}) {
		@quota = grep { $_->[2] } @quota;
		}
	
	if ($sects->{'qsort'}) {
		# Sort by percent used
		@quota = grep { $_->[2] } @quota;
		@quota = sort { ($b->[1]+$b->[3])/$b->[2] <=>
				($a->[1]+$a->[3])/$a->[2] } @quota;
		}
	else {
		# Sort by usage
		@quota = sort { $b->[1]+$b->[3] <=> $a->[1]+$a->[3] } @quota;
		}

	# Show message about number of domains being displayed
	print "<table width=100%>\n";
	if (@quota > $max) {
		@quota = @quota[0..($max-1)];
		$qmsg = &text('right_quotamax', $max);
		}
	elsif ($level == 0) {
		$qmsg = $text{'right_quotaall'};
		}
	else {
		$qmsg = $text{'right_quotayours'};
		}

	# Show links to graphs
	print "<tr class='ui_form_pair'> <td class='ui_form_value' colspan=2>$qmsg ",
	      &history_link("quotalimit", 1)," ",
	      &history_link("quotaused", 1),"</td> </tr>\n";

	# The table of domains
	foreach my $q (@quota) {
		print "<tr class='ui_form_pair'>\n";
		my $ed = virtual_server::can_config_domain($q->[0]) ?
			"edit_domain.cgi" : "view_domain.cgi";
		$dname = virtual_server::show_domain_name($q->[0]);
		print "<td class='ui_form_label' width=20%><a href='virtual-server/$ed?",
		      "dom=$q->[0]->{'id'}'>$dname</a></td>\n";
		print "<td class='ui_form_value' width=50% nowrap>";
		if ($sects->{'qshow'}) {
			# By percent used
			$qpc = int($q->[1]*100 / $q->[2]);
			$dpc = int($q->[3]*100 / $q->[2]);
			print &bar_chart_three(
			    100,
			    $qpc,
			    $dpc,
			    100-$qpc-$dpc
			    );
			}
		else {
			# By actual usage
			print &bar_chart_three(
			    $maxquota,		# Highest quota
			    $q->[1],		# Domain's disk usage
			    $q->[3],		# DB usage
			    $q->[2] ? $q->[2]-$q->[1]-$q->[3] : 0,  # Leftover
			    );
			}
		print "</td>\n";

		# Percent used, if available
		if ($q->[2]) {
			local $pc = int(($q->[1]+$q->[3])*100 / $q->[2]);
			$pc = "&nbsp;$pc" if ($pc < 10);
			print "<td class='ui_form_value' nowrap>",$pc,"% - ",
				     &text('right_out',
					   &nice_size($q->[1]+$q->[3]),
					   &nice_size($q->[2])),"</td>\n";
			}
		else {
			print "<td class='ui_form_value'>",&nice_size($q->[1]+$q->[3]),"</td>\n";
			}
		print "</tr>\n";
		}
	print "</table>\n";
	}
}

sub any_over_bandwidth
{
local ($doms) = @_;
foreach my $d (@$doms) {
	if ($d->{'bw_limit'} && $d->{'bw_usage'} >= $d->{'bw_limit'}) {
		return 1;
		}
	}
return 0;
}

# show_bandwidth_info(&domains)
# Show a table of bandwidth usage for all domains this user can access
sub show_bandwidth_info
{
# Filter domains
local @doms = @{$_[0]};
local @doms = grep { !$_->{'parent'} } @doms;

if ($sects->{'qsort'}) {
	# Sort by percent used
	@doms = grep { $_->{'bw_limit'} } @doms;
	@doms = sort { $b->{'bw_usage'}/$b->{'bw_limit'} <=>
		       $a->{'bw_usage'}/$a->{'bw_limit'} } @doms;
	}
else {
	# Sort by usage
	@doms = sort { $b->{'bw_usage'} <=> $a->{'bw_usage'} } @doms;
	}

# Work out highest usage or limit
my $maxbw = 0;
foreach my $d (@doms) {
	$maxbw = $d->{'bw_limit'} if ($d->{'bw_limit'} > $maxbw);
	$maxbw = $d->{'bw_usage'} if ($d->{'bw_usage'} > $maxbw);
	}
return if (!$maxbw);	# No bandwidth yet

# Show message about number of domains being displayed
local $max = $sects->{'max'} || $default_domains_to_show;
print "<table width=100%>\n";
if (@doms > $max) {
	@doms = @doms[0..($max-1)];
	$qmsg = &text('right_quotamax', $max);
	}
else {
	$qmsg = $text{'right_quotaall'};
	}
print "<tr class='ui_form_pair'> <td class='ui_form_value' colspan=2>$qmsg</td> </tr>\n";

# The table of domains
foreach my $d (@doms) {
	print "<tr class='ui_form_pair'>\n";
	my $ed = virtual_server::can_config_domain($d) ?
		"edit_domain.cgi" : "view_domain.cgi";
	$dname = virtual_server::show_domain_name($d);
	print "<td class='ui_form_label' width=20%><a href='virtual-server/$ed?",
	      "dom=$d->{'id'}'>$dname</a></td>\n";
	print "<td class='ui_form_value' width=50% nowrap>";
	$pc = $d->{'bw_limit'} ? int($d->{'bw_usage'}*100 / $d->{'bw_limit'})
			       : undef;
	if ($sects->{'qshow'}) {
		# By percent used
		print bar_chart_three(
		    100,
		    $pc,
		    0,
		    $pc > 100 ? 0 : 100-$pc,
		    );
		}
	else {
		# By actual usage
		print bar_chart_three(
		    $maxbw,		# Highest usage
		    $d->{'bw_usage'},	# Domain's bandwidth
		    0,
		    $d->{'bw_usage'} > $d->{'bw_limit'} ? 0 :
		    $d->{'bw_limit'} ? $d->{'bw_limit'}-$d->{'bw_usage'}
				     : 0,  # Leftover
		    );
		}
	print "</td>\n";

	# Percent used, if available
	if ($d->{'bw_limit'}) {
		$pc = "&nbsp;$pc" if ($pc < 10);
		print "<td class='ui_form_value' nowrap>",$pc,"% - ",
			     &text('right_out',
				   &nice_size($d->{'bw_usage'}),
				   &nice_size($d->{'bw_limit'})),"</td>\n";
		}
	else {
		print "<td class='ui_form_value'>",&nice_size($d->{'bw_usage'}),"</td>\n";
		}
	print "</tr>\n";
	}
print "</table>\n";
}

# collapsed_header(text, name)
sub collapsed_header
{
local ($text, $name) = @_;
print "<br><font style='font-size:16px'>";
local $others = join("&", map { "open=$_" } grep { $_ ne $name } @open);
$others = "&$others" if ($others);
if ($open{$name}) {
	print "<img src=images/open.gif border=0>\n";
	print "<a href='right.cgi?$others'>$text</a>";
	}
else {
	print "<img src=images/closed.gif border=0>\n";
	print "<a href='right.cgi?open=$name$others'>$text</a>";
	}
print "</font><br>\n";
return $open{$name};
}

# show_toggleview(name, id, status, header)
# Prints HTML for an open/close toggler
sub show_toggleview
{
local ($name, $id, $status, $header) = @_;
local $img = $status ? "open" : "closed";
local $cls = $status ? "itemshown" : "itemhidden";
print "<a href=\"javascript:toggleview('$name','$id')\" id='$id'><img border='0' src='images/$img.gif' alt='[&ndash;]'></a>";
print "<a href=\"javascript:toggleview('$name','$id')\" id='$id'><b> $header</b></a><p>";
print "<div class='$cls' id='$name'>";
}

# history_link(stat, [notd])
# If history is being kept and the user can view it, output a graph link
sub history_link
{
local ($stat, $notd) = @_;
if ($hasvirt &&
    defined(&virtual_server::can_show_history) &&
    &virtual_server::can_show_history()) {
	local $msg = $text{'history_stat_'.$stat};
	return ($notd ? "" : "<td>").
	       "<a href='virtual-server/history.cgi?stat=$stat'>".
	       "<img src=images/graph.png border=0 title='$msg'></a>".
	       ($notd ? "" : "</td>")."\n";
	}
return undef;
}

sub show_new_features
{
my ($nosect) = @_;
my $newhtml;
if ($hasvirt && !$sects->{'nonewfeatures'} &&
    defined(&virtual_server::get_new_features_html) &&
    ($newhtml = virtual_server::get_new_features_html($defdom))) {
	# Show new features HTML for Virtualmin
	if ($nosect) {
		print "<h3>$text{'right_newfeaturesheader'}</h3>\n";
		}
	else {
		print ui_hidden_table_start($text{'right_newfeaturesheader'},
		      "width=100%", 2,
		      "newfeatures", 1);
		}
	print &ui_table_row(undef, $newhtml, 2);
	if (!$nosect) {
		print ui_hidden_table_end("newfeatures");
		}
	}
if ($hasvm2 && !$sects->{'nonewfeatures'} &&
    defined(&server_manager::get_new_features_html) &&
    ($newhtml = server_manager::get_new_features_html(undef))) {
	# Show new features HTML for Cloudmin
	if ($nosect) {
		print "<h3>$text{'right_newfeaturesheadervm2'}</h3>\n";
		}
	else {
		print ui_hidden_table_start($text{'right_newfeaturesheadervm2'},
		      "width=100%", 2,
		      "newfeaturesvm2", 1);
		}
	print &ui_table_row(undef, $newhtml, 2);
	if (!$nosect) {
		print ui_hidden_table_end("newfeaturesvm2");
		}
	}
}

# show_vm2_servers(&servers, showtypes?)
# Prints a summary of Cloudmin systems
sub show_vm2_servers
{
local ($servers, $showtypes) = @_;

# Count up systems by type and status and usage
my %c;
foreach my $s (@$servers) {
	$c{'all'}++;
	if (&server_manager::is_parent_server($s)) {
		$c{'host'}++;
		}
	my $virt = &server_manager::is_virtual_server($s);
	$c{$virt ? 'virt' : 'real'}++;	
	if ($s->{'status'} eq 'nowebmin' ||
	    $s->{'status'} eq 'novirt' ||
	    $s->{'status'} eq 'virt' ||
	    $s->{'status'} eq 'alive') {
		$c{'up'}++;
		}
	else {
		$c{'down'}++;
		}
	my $mfunc = "server_manager::type_".$s->{'manager'}."_get_memory_size";
	if (defined(&$mfunc)) {
		my $mem = &$mfunc($s);
		if ($mem) {
			$c{'mem'} += $mem;
			}
		}
	my $dfunc = "server_manager::type_".$s->{'manager'}."_get_disk_size";
	if (defined(&$dfunc)) {
		my $disk = &$dfunc($s);
		if ($disk) {
			$c{'disk'} += $disk;
			}
		}
	}

# Show in a form
foreach my $f ('all', 'host', 'virt', 'real', 'up', 'down', 'mem', 'disk') {
	print &ui_table_row($text{'right_vm2count'.$f},
		$f eq 'mem' || $f eq 'disk' ? &nice_size($c{$f})
					    : int($c{$f}));
	}
}

# Output a table of VM2 system owners limits and usage
sub show_vm2_limits
{
my ($limits, $plan) = @_;

# Account plan name
if ($plan) {
	print ui_table_row($text{'right_vm2plan'},
		$plan->{'desc'}, 3);
	}

foreach my $l (@server_manager::plan_limit_types) {
	$n = &indexof($l, @server_manager::nice_plan_limit_types) >= 0;
	$nice = $n ? &nice_size($limits->{$l}) :
		$l eq "cpu" ? $limits->{$l}."%"
			    : $limits->{$l};
	$nicemax = $n ? &nice_size($limits->{'max_'.$l}) :
		   $l eq "cpu" ? $limits->{'max_'.$l}."%"
		      	       : $limits->{'max_'.$l};
	$msg1 = $limits->{$l} || !$limits->{$l.'_unlimited'} ?
               		$nice : $text{'right_vunlimited'};
	$msg2 = $limits->{'max_'.$l} ? $nicemax : $text{'right_vunlimited'};
	if ($limits->{'max_'.$l} &&
	    $limits->{$l} > $limits->{'max_'.$l}) {
		$msg1 = "<font color=red>$msg1</font>";
		$msg2 = "<font color=red>$msg2</font>";
		}
	print ui_table_row($text{'right_vm2c'.$l}, $msg1);
	print ui_table_row($text{'right_vm2m'.$l}, $msg2);
	}
}

sub parse_license_date
{
if ($_[0] =~ /^(\d{4})-(\d+)-(\d+)$/) {
	return eval { timelocal(0, 0, 0, $3, $2-1, $1-1900) };
	}
return undef;
}

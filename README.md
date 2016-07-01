virtualmin-bootstrap-theme
==========================

NOTE: This theme is not complete or functional. Authentic Theme is where your attention should be directed for a feature-complete, responsive, and fully functional, Bootstrap-based theme for Webmin, Virtualmin, Usermin, and Cloudmin.

Responsive Bootstrap theme for Webmin, Virtualmin, Cloudmin, and Usermin

Installing
----------

Fork the git repo into your home directory (wherever you normally put your src)

Make a symbolic link in your Webmin installation directory:

  # cd /usr/libexec/webmin
  
  # ln -s /path/to/virtualmin-bootstrap-theme bootstrap-theme
  
  # cd bootstrap-theme
  
  And, if your perl is installed in /usr/bin (this applies to almost everyone), do this:
  
  # find . -name "*.cgi" -type f -exec sed -i 's/#!\/usr\/local\/bin\/perl/#!\/usr\/bin\/perl/g' {} \;
  
Install the JSON::XS Perl module (this should be readily available from most OS software repos). The package name on 
CentOS/Fedora/RHEL is perl-JSON-XS, and on Debian/Ubuntu it is libjson-xs-perl. This module is used to encode/decode JSON
for sending serialized data structures back and forth between Webmin and the browser. It is not used heavil yet, but will
eventually be how most data goes back and forth.

What's broken?
--------------

This theme doesn't work in a variety of interesting ways.

See WISHLIST for some of those ways. WISHLIST is a list of things that need to be changed in Webmin proper for this theme
to be usable for all Webmin modules. Some of those tasks are simple, but very time-consuming, and would be well-served by
more people tackling the problems.

The theme itself has the following broken bits:

Back button doesn't work correctly. One solution may be to use jQuery BBQ or the History API to store history data, and a
function to handle URI-to-state translation. i.e. a query string like ?l=v&r=/apache/edit_vhosts.cgi might be used to store a screen state of the Virtualmin menu open in the left panel and a page in the Apache module open in the right pane.

Numerous quirks need fixing and bits of polishing need doing. Many of the quirks are happening because Webmin still has a lot of legacy cruft from before ui_lib function existed, or because of assumptions Webmin makes about the UI. But, many others are just polish that's needed in the theme.

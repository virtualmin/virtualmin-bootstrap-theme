virtualmin-bootstrap-theme
==========================

NOTE: Theme is currently under development. It is not yet functional.

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

Back button doesn't work.

Submit buttons don't work correctly, if there is more than one form on a page. Currently, one event is being attached to
the forms on a page, but it isn't specific to individual forms. I don't know how to attach an event to every form on a page
and include all of the necessary information to process the correct form based on which form was submitted. The only way
I've been able to make this work is by explicitly including the ID of every form in the JavaScript (index.js), but this is
not scalable to all of Webmin, which has thousands of forms with different IDs. This may be the most important piece of
the JavaScript puzzle in getting the theme into a usable state. Seems like it ought to be easy, but I'm been banging
my head on it for ages. JavaScript is not my strong suit.

Numerous quirks need fixing and bits of polishing need doing.



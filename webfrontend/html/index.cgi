#!/usr/bin/perl

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


##########################################################################
# Modules
##########################################################################
use LoxBerry::System;
use LoxBerry::Web;

use CGI qw/:standard/;
use warnings;
use strict;

##########################################################################
# Variables
##########################################################################

# Version of this script
my $version = LoxBerry::System::pluginversion() . "-1";

my  $cgi = new CGI;
my  $plugin_cfg;
my  $lang;

# Define your plugin title, help and help link 
my $plugintitle = "Sample Plugin V$version";
my $helplink = "https://www.loxforum.com/forum/projektforen/loxberry/entwickler/84645-best-practise-perl-programmierung-im-loxberry";
my $helptemplate = "help_myloxberry.html";

##########################################################################
# Read Settings
##########################################################################

print STDERR "Global variables from LoxBerry::System\n";
print STDERR "Homedir:     $lbhomedir\n";
print STDERR "Plugindir:   $lbplugindir\n";
print STDERR "CGIdir:      $lbcgidir\n";
print STDERR "HTMLdir:     $lbhtmldir\n";
print STDERR "Templatedir: $lbtemplatedir\n";
print STDERR "Datadir:     $lbdatadir\n";
print STDERR "Logdir:      $lblogdir\n";
print STDERR "Configdir:   $lbconfigdir\n";


# Read plugin config
$plugin_cfg 	= new Config::Simple("$lbconfigdir/pluginconfig.cfg") or die $plugin_cfg->error();
my %pcfg = $plugin_cfg->vars();
my $pname = $pcfg{'MAIN.SCRIPTNAME'};

# Import form data to namespace (easier access)
$cgi->import_names('R');
# Now access form variables by: $R::formvariable

##########################################################################
# Initialize html templates
##########################################################################

# See:
# http://www.perlmonks.org/?node_id=65642
# http://search.cpan.org/~samtregar/HTML-Template-2.6/Template.pm 

# Main
my $maintemplate = HTML::Template->new(
	filename => "$lbtemplatedir/main.html",
	global_vars => 1,
	loop_context_vars => 1,
	die_on_bad_params => 0,
	associate => $plugin_cfg,
);

##########################################################################
# Translations
##########################################################################

# LoxBerry's template system will auto-detect users language.
# To test the translations, you can call your cgi with ?lang=xx
# This section overrides the language detection of LoxBerry::Web
if ($R::lang) {
	$LoxBerry::Web::lang = substr($R::lang, 0, 2);
}

# Get language from LoxBerry::Web
$lang = lblanguage();

%L = LoxBerry::Web::readlanguage($maintemplate, "language.ini");
# In the HTML Template, all phrases are now accessible with <TMPL_VAR SECTION.PHRASE>
# In the code, phrases are accessible with $L{'SECTION.PHRASE'}.

##########################################################################
# Create some variables for the Template
##########################################################################

###
# As an example: we create a select list for a form in two different ways
###

# First create a select list for a from - data is taken from the Plugin 
# Config file. We are using the HTML::Template Loop function. You should
# be familiar with Hashes and Arrays in Perl.
#
# Please see https://metacpan.org/pod/HTML::Template
# Please see http://www.perlmonks.org/?node_id=65642
#
# This is the prefered way, because code and style is seperated. But
# it is a little bit complicated. If you could not understand this,
# please see next example.

# Create an array with the sections we would like to read. These
# Sections exist in the plugin config file.
# See https://wiki.selfhtml.org/wiki/Perl/Listen_bzw._Arrays
my @sections = ("SECTION1","SECTION2","SECTION3");

# Now we put the options from the 3 sections into a (new) hash (we check if
# they exist at first). This newly created hash will be referenced in an array.
# Perl only allows referenced hashes in arrays, so we are not allowed to
# overwrite the single hashes!
my $i = 0;
my @array;
foreach (@sections) {
        if ( $plugin_cfg->param("$_.NAME") ) {
                %{"hash".$i} = ( # Create a new hash each time, e.g. %hash1, %hash2 etc.
                OPTION_NAME	=>	$plugin_cfg->param("$_.NAME"),
                ID		=>	$plugin_cfg->param("$_.ID"),
                );
                push (@array, \%{"hash".$i}); 	# Attach a reference to the newly created
						# hash to the array
                $i++;
	}	
}
# Let the Loop with name "SECTIONS" be available in the template
$maintemplate->param( SECTIONS => \@array );

# This was complicated? Yes, it is because you have to understand hashes and arrays in Perl.
# We can do the very same if we mix code and style here. It's not as "clean", but it is
# easier to understand.

# Again we read the options from the 3 sections from our config file. But we now will create
# the select list for the form right here - not as before in the template.
my $selectlist;
foreach (@sections) {
        if ( $plugin_cfg->param("$_.NAME") ) {
		# This appends a new option line to $selectlist
		$selectlist .= "<option value='".$plugin_cfg->param("$_.ID")."'>".$plugin_cfg->param("$_.NAME")."</option>\n";
	}
}
# Let the Var $selectlist with the name SELECTLIST be available in the template
$maintemplate->param( SELECTLIST => $selectlist );

###
# As an example: we create some vars for the template
###
$maintemplate->param( PLUGINNAME => $pname );
$maintemplate->param( ANOTHERNAME => "This is another Name" );


##########################################################################
# Print Template
##########################################################################

# LoxBerry::Web header
LoxBerry::Web::lbheader($plugintitle, $helplink, $helptemplate);

# Main
print $maintemplate->output;

# LoxBerry::Web footer
LoxBerry::Web::lbfooter();

exit;

#!/usr/bin/perl -w

use Net::NTP;
use CGI;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use LWP;
use HTTP::Date;
use POSIX;
use strict;

my $urlstring;
my $q=new CGI;

$urlstring = $q->param('urlstring');
print $q->header(-expires=>'now');
print $q->start_html( -title=>'Web Server Time Cop', -style=>{'src'=>'/css/gen.css'} );
print $q->h1('Web Time Cop');
print $q->p(
	#$q->a({-href=>"http://validator.w3.org/check?uri=referer"},
	$q->img({-src=>"http://www.w3.org/Icons/valid-xhtml10-blue",
		-alt=>"Valid XHTML 1.0 Transitional", -height=>"31", -width=>"88"})#)
  );
#<p>
    #<a href="http://validator.w3.org/check?uri=referer"><img
        #src="http://www.w3.org/Icons/valid-xhtml10"
        #alt="Valid XHTML 1.0 Transitional" height="31" width="88" /></a>
  #</p>
print $q->p(<<EOT);
This tool serves a single purpose: to verify that a web server has the correct time.
It takes a single web site URL as an argument and compares the time returned by the site with NTP. The path or query after the hostname is not necessary, but the tool will use them if provided.
EOT

print $q->p(<<EOT);
When the site to be tested is chosen, it would be wise to run the tool four or five times for verification. 
The reason for this is due to the fact that any load balanced sites might return different date values depending on which load balanced server provides the response.
EOT

print $q->p(<<EOT);
<em>Please Note</em> that a difference of more than 1 second between the server time and NTP time is undesireable and should be addressed by verifying that NTP is indeed running on the server.
EOT

print $q->start_form(-method=>'GET', -action=>'/ntpweb/', -enctype=>&CGI::URL_ENCODED);
print $q->div("Please input a web URL.");
print $q->div($q->textfield(-name=>"urlstring", -default=>$urlstring, -size=>100, -maxlength=>1000));
print $q->div($q->submit());
print $q->endform;
print $q->hr;

if ($urlstring =~ /\w\.\w/)
	{
	( my $host, my $path) = $urlstring =~ m#(?:\w{3,5}://)?([^/]+)/?(.*)?#;

	my $lwp = LWP::UserAgent->new(max_redirect=>0);
	my $response = $lwp->head("http://$host/$path");
	print $q->p($host);

	my %ntphash = get_ntp_response();
	if ($response->code < 500)
		{
		my $serverdate = $response->header( 'date' );
		my $serverdateint = str2time($serverdate);
		my $ntpdateint =  floor($ntphash{'Receive Timestamp'});
		my $ntpdate =  time2str($ntpdateint);

		print $q->div("Server Time is " . $serverdate);
		print $q->div("NTP Time is " . $ntpdate);

		my $difference = abs($serverdateint - $ntpdateint);
		my $style = ($difference < 2) ? "color: green" : "color: red";
		print $q->div( {-style => $style}, "Difference is " . abs($serverdateint - $ntpdateint) ." seconds");
		}
	else
		{
		print $q->div({-style=>"color: red;"}, "Domain did not return a valid http response");
		}

	}

print $q->end_html;

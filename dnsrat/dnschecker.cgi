#!/usr/bin/perl -w

use Net::DNS;
use Net::IP;
use CGI;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use XML::Dumper;
use strict;

my $res = Net::DNS::Resolver->new(persistent_udp=>1);
my $resnr = Net::DNS::Resolver->new(recurse=>0, udp_timeout=>5);
my $sixtofour = Net::IP->new('2002::/16');
my $arrayref;
my %soas;
my %arecords;
my %aaaarecords;
my %nsrecords;
my @listofrr;
my $q=new CGI;
my $domlist = $q->param('ListofDomains');
$domlist =~ s/\s//g;
my @alldomains = split(/,/, $domlist);


print $q->header(-expires=>'now');
print $q->start_html( -title=>'DNS Rat', -style=>{'src'=>'/css/gen.css'} );

print $q->h1('The DNS Rat');
print $q->p('This is the DNS Rat. It\'s function is to expose all of the mistakes that DNS administrators and network operators make when adding or changing DNS records.');
print $q->p('Let\'s try to keep this page as close to empty as possible. We can do that by adhering to just a couple of rules.');

print $q->ol($q->li('CNAMEs should only point to A records. Period.'),
	$q->li('Only one A record should point to any particular IP address.'),
	$q->li('Each zone should have at least two NS records configured.'));

print $q->p('If you run this tool on any Active Directory domain, please be careful interpreting the output. Microsoft breaks some DNS rules (not surprisingly) as it manages the AD namespace.');

#%><?xml version="1.0" encoding="iso-8859-1"?>
#<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" 
#   "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
#<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en-US"><head><title>DNS Rat</title>
#<link rel="stylesheet" type="text/css" href="/css/gen.css" />
#</head>
#<body>
#<h1>The DNS Rat</h1>
#<p>This is the DNS Rat. It's function is to expose all of the mistakes that DNS administrators and network operators make when adding or changing DNS records.</p>
#<p>Let's try to keep this page as close to empty as possible. We can do that by adhering to just a couple of rules.</p>
#<ol><li>CNAMEs should only point to A records. Period.</li> <li>Only one A record should point to any particular IP address.</li></ol>
#<p>If you run this tool on any Active Directory domain, please be careful interpreting the output. Microsoft breaks some DNS rules (not surprisingly) as it manages the AD namespace.</p>



print $q->start_form(-method=>'GET', -action=>'/dnsrat', -enctype=>&CGI::URL_ENCODED);
print $q->div("Please input a comma delimited list of domains in the field.");
print $q->div($q->textfield(-name=>"ListofDomains", -default=>$domlist, -size=>100, -maxlength=>1000));
print $q->div($q->submit());
print $q->endform;
print $q->hr;


#foreach (qw(rye.avon.com avon.com na.avonet.net sa.avonet.net ap.avonet.net eu.avonet.net))
foreach my $domain (@alldomains)
	{
	my $query = $res->query($domain, "SOA");
  	if ($query)
		{
		my $soa = ($query->answer)[0]->mname;
		$soas{$domain} = $soa;
		}
	} 
foreach my $domain (keys %soas)
	{
	$res->nameservers($soas{$domain});
	push (@listofrr, $res->axfr($domain));
	}

$res->nameservers('134.65.0.1', '134.65.0.2');

foreach my $rr (@listofrr)
	{
	if ($rr->type eq "A")
		{
		my $address = $rr->address;
		my $name = $rr->name;

		next if ($address eq '255.255.255.255');

		unless ($arecords{$address})
			{
			$arecords{$address} = [];
			}

		$arrayref = $arecords{$address};
		my $found = grep(/\Q$name/, @$arrayref);
		if ($found == 0)
			{
			push (@$arrayref, $name);
			}
		}
	elsif ($rr->type eq "AAAA")
		{
		my $address = Net::IP->new($rr->address);
		my $name = $rr->name;

		$aaaarecords{$address->short} = [] unless ($aaaarecords{$address->short});

		$arrayref = $aaaarecords{$address->short};
		my $found = grep(/\Q$name/, @$arrayref);
		if ($found == 0)
			{
			push (@$arrayref, $name);
			}

		if ($sixtofour->overlaps($address) == $IP_B_IN_A_OVERLAP)
			{
			print $q->div({-style=>"color: violet;"}, "$name has a 6to4 address of " . $address->short);
			}
		}
	elsif ($rr->type eq "NS")
		{
		my $domainname = $rr->name;
		my $nsname = $rr->nsdname;
		$nsrecords{$domainname} = [] unless ($nsrecords{$domainname});

		$arrayref = $nsrecords{$domainname};
		my $found = grep(/\Q$nsname/, @$arrayref);
		if ($found == 0)
			{
			push (@$arrayref, $nsname);
			}
		}
	elsif ($rr->type eq "CNAME")
		{
		my $rrcname = $rr->cname;
		my $responsepacket = $res->query($rrcname);
		unless ($responsepacket)
			{
			print $q->div({-style=>"color: red;"},"CNAME of ",$rr->name, " points to $rrcname which doesn't exist.");
			next;
			}
		my @answer = $responsepacket->answer;
		my $type = $answer[0]->type;
		if ($type ne "A")
			{
			print $q->div({-style=>"color: blue;"},"CNAME ", $rr->name, " points to ", $answer[0]->name, " which is not an A record.");
			}
		}
	elsif ($rr->type eq "PTR")
		{
		my @dottedquad = $rr->name =~ /(\d+)\.(\d+)\.(\d+)\.(\d+)\./;
		my $matchip = join (".", reverse(@dottedquad));
		my $ptrdname = $rr->ptrdname;
		my $responsepacket = $res->query($ptrdname, 'A');
		next unless ($responsepacket);
		my ($answeradd) = $responsepacket->answer;
		if ($answeradd->address ne $matchip)
			{
			print $q->div({-style=>"color: orange;"},"PTR value for $matchip points to $ptrdname, but this does not match A record.");
			}
		}
	}

foreach my $nsrecord (keys %nsrecords)
	{
	$arrayref  = $nsrecords{$nsrecord};

	print $q->div({-style=>"color: purple"},
		"Only 1 NS record for $nsrecord")
		if (@$arrayref == 1);

	foreach my $rrns (@$arrayref)
		{
		my $responsepacket = $res->query($rrns);
		unless ($responsepacket)
			{
			print $q->div({-style=>"color: red;"},"$nsrecord contains NS of $rrns which doesn't exist.");
			next;
			}

		my @answer = $responsepacket->answer;
		my $type = $answer[0]->type;

		if ($type ne "A")
			{
			print $q->div({-style=>"color: blue;"},"$nsrecord contains NS of  $rrns, which is not an A record.");
			next;
			}

		$resnr->nameservers($rrns);							#From here down, check to ensure that the secondary
		$responsepacket = $resnr->send($nsrecord, 'NS');	#actually does have the zone configured.

		if ($responsepacket)
			{
			print $q->div({-style=>"color: blue;"},"$nsrecord contains $rrns as NS, but the server appears not to be configured.") unless ($responsepacket->header->aa);
			}
		else
			{
			print $q->div({-style=>"color: red;"}, "For $nsrecord, no response from NS $rrns.");
			}
		}
	}

foreach my $address (keys %arecords)
	{
	$arrayref = $arecords{$address};
	if (@$arrayref > 1)
		{
		print $q->div("Multiple A records for $address, specifically", $q->ul($q->li($arrayref)));
		}
	}

foreach my $address (keys %aaaarecords)
	{
	$arrayref = $aaaarecords{$address};
	if (@$arrayref > 1)
		{
		print $q->div("Multiple AAAA records for $address, specifically", $q->ul($q->li($arrayref)));
		}
	}
print $q->end_html;

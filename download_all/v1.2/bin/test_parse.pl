#!/share/nas2/genome/bin/perl
use strict;
use warnings;
use FindBin qw($Bin $Script);
use Getopt::Long;
use POSIX qw/strftime/;
use LWP::UserAgent;

my $od=$ARGV[0];
parse_xml_files("$od/data_study/current_xml","pro");
parse_xml_files("$od/data_sample/current_xml","sample");
parse_xml_files("$od/data_exper/current_xml","expr");
sub parse_xml_files{
	my $xml_dir=shift;
	my $type=shift;
	my $ua = LWP::UserAgent->new;
	$ua->timeout(3600);
	my $url='http://10.3.129.218:8079/highFlux/analysis?type='.$type.'&path='.$xml_dir;
	my $req = HTTP::Request->new(GET => $url);
	my $res = $ua->request($req);
	if($res->is_success){
		print strftime('%Y-%m-%d  %H:%M:%S',localtime())."parse $type successful \n";
	}
	else{
		print strftime('%Y-%m-%d  %H:%M:%S',localtime())."parse $type faile. Error: ".$res->status_line."\n";
		#die "parse $xml_dir failed";
	}
} 

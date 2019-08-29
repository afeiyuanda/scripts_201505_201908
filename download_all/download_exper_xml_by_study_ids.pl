#!/share/nas2/genome/bin/perl
use strict;
use warnings;
use XML::Simple;
use LWP::Simple;
use FindBin qw($Bin $Script);
use POSIX qw/strftime/;
use LWP::UserAgent;
use Getopt::Long;
use Try::Tiny;

my ($od,$study_id);
GetOptions(
	"od:s"=>\$od,
    "study_id:s"=>\$study_id,
	"help|h"=>\&USAGE,
)or &USAGE;
&USAGE unless($od);

####make directory
mkdir $od  unless (-d $od);
my $prefix=strftime('%Y%m%d%H%M%S',localtime());
my @studyids=split(/,/,$study_id);
my @experiments_ids_list;
foreach my $id(@studyids){
    my $get_exper_ids_url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=sra&tool=PubCrawler_3.0&email=xiayh@biomarker.com.cn&retmax=9999999&retmode=xml&term='.$id.'[bioproject:exp]';
    push @experiments_ids_list,get_ids($get_exper_ids_url);
}

my $i=1;
while( my @list = splice( @experiments_ids_list,0,200) ) {
    my $idstr=join(',',@list);
    print "/share/nas2/genome/bin/perl $Bin/download_xml_and_check.pl -type exper -idlist $idstr -outxml $od/${prefix}_${i}.xml\n";
    system "/share/nas2/genome/bin/perl $Bin/download_xml_and_check.pl -type exper -idlist $idstr -outxml $od/${prefix}_${i}.xml";
    $i++;
}
parse_xml_files("$od","expr");



####################

sub get_ids{
    my $web_url=shift;
    my @idlist; 
	my $try_times=5;
	while($try_times>0){
		my $flag=0;
		my $xml_text=get $web_url;
		if($xml_text){
			try{
				my $xs = XML::Simple->new;
				my $xml_in = $xs->XMLin($xml_text,ForceArray =>qr/^Id$/);
				foreach my $a ($xml_in->{'IdList'}->{'Id'}){
					if($a){
						push @idlist,@$a;
					}
				}
				$flag=1;
			};
		}
		last if($flag==1);
		$try_times--;
	}
    return @idlist;
}

sub parse_xml_files{
	my $xml_dir=shift;
	my $type=shift;
	my $ua = LWP::UserAgent->new;
	$ua->timeout(3600);
	my $url='http://10.3.129.219:8080/highFlux/analysis?type='.$type.'&path='.$xml_dir;
	my $req = HTTP::Request->new(GET => $url);
	my $res = $ua->request($req);
	if($res->is_success){
		print strftime('%Y-%m-%d  %H:%M:%S',localtime())." parse $type successful \n";
	}
	else{
		print strftime('%Y-%m-%d  %H:%M:%S',localtime())." parse $type faile. Error: ".$res->status_line."\n";
		#die "parse $xml_dir failed";
	}
} 


sub USAGE {
    my $usage=<<"USAGE";
        Options:
        -od <directory>   update directory
        -study_id         study id. eg:280256 or 20357,280256
        
        use:
        1. /share/nas1/qing/toolkits/SRA_update/download_all/download_exper_xml_by_study_ids.pl -od ./test -study_id 20357,280256
        2. /share/nas1/qing/toolkits/SRA_update/download_all/download_exper_xml_by_study_ids.pl -od ./test -study_id 20357
USAGE
    print $usage;
    exit;
}

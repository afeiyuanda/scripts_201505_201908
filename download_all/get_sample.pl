#!/share/nas2/genome/bin/perl
use strict;
use warnings;
use XML::Simple;
use LWP::Simple;
use FindBin qw($Bin $Script);
use Getopt::Long;
use POSIX;

my $od;
GetOptions(
	"od:s"=>\$od,
	"help|h"=>\&USAGE,
)or &USAGE;
&USAGE unless($od);

####make directory
mkdir  "$od/work_sh"  unless (-d "$od/work_sh");
mkdir "$od/data_sample" unless (-d "$od/data_sample");
my $current_time=strftime("%Y%m%d",localtime());
my $current_time_samples="$od/data_sample/$current_time";
mkdir $current_time_samples unless (-d $current_time_samples);

###samples
my $i=1;
my $get_samples_ids_url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=biosample&term=biosample+or+sra&email=xiayh@biomarker.com.cn&tool=PubCrawler_3.0&datetype=pdat&retmax=99999999';
system "wget -q \'$get_samples_ids_url\' -O $od/data_sample/all_sample_ids.xml";
my @samples_ids_list=get_ids("$od/data_sample/all_sample_ids.xml");
open OUT,">$od/work_sh/download_sample_xml_1.sh" or die $!;
open OUTLOG,">$od/data_sample/current_xml.log" or die $!;
while( my @list = splice( @samples_ids_list,0,400) ) {
    my $idstr=join(",",@list);
    print OUT "/share/nas2/genome/bin/perl $Bin/download_xml_and_check.pl -type sample -idlist $idstr -outxml $current_time_samples/${i}.xml\n";
    print OUTLOG "${i}.xml\t$idstr\n";
    $i++;
}
close(OUT);
close(OUTLOG);
###download
system "sh $od/work_sh/download_sample_xml_1.sh > $od/work_sh/download_sample_xml_1.sh.log 2>&1";
####################



sub get_ids{
    my $xmlfile=shift;
    my @idlist; 
	open IN,"$xmlfile" or die $!;
	while(<IN>){
		chomp;
		if(/\t<Id>(\d+)<\/Id>$/){
			push @idlist,$1;
		}
	}
	close(IN);
    return @idlist;
}

sub USAGE {
    my $usage=<<"USAGE";
        Options:
        -od <directory>   update directory

USAGE
    print $usage;
    exit;
}

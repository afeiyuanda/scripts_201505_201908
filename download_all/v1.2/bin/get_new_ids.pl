#!/share/nas2/genome/bin/perl
use strict;
use warnings;
use XML::Simple;
use LWP::Simple;
use FindBin qw($Bin $Script);
use Getopt::Long;
use POSIX;
use Try::Tiny;

my ($od,$reldate);
GetOptions(
	"od:s"=>\$od,
	"help|h"=>\&USAGE,
	"reldate:s"=>\$reldate,
)or &USAGE;
&USAGE unless($od);

##
$reldate ||= 2;
####make directory
my $current_time=strftime("%Y%m%d",localtime());
my $current_time_study="$od/data_study/$current_time";
my $current_time_exper="$od/data_exper/$current_time";
my $current_time_samples="$od/data_sample/$current_time";
mkdir $current_time_study unless (-d $current_time_study);
mkdir $current_time_exper unless (-d $current_time_exper);
mkdir $current_time_samples unless (-d $current_time_samples);

####get old project ids
my %old_project_ids;
open IN,"$od/data_study/summary.txt.bak" or die $!;
<IN>;
while(<IN>){
    chomp;
    my ($id)=(split(/\t/))[3];
    $old_project_ids{$id}=1;
}
close(IN);

####read new summary.txt and generate download files
my (@project_ids_list,@experiments_ids_list);
open IN,"$od/data_study/summary.txt" or die $!;
<IN>;
while(<IN>){
    chomp;
    my ($id)=(split(/\t/))[3];
    next if (exists $old_project_ids{$id});
    push @project_ids_list,$id;
    my $get_exper_ids_url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=sra&tool=PubCrawler_3.0&email=xiayh@biomarker.com.cn&retmax=9999999&retmode=xml&term='.$id.'[bioproject:exp]';
    push @experiments_ids_list,get_ids($get_exper_ids_url);
}
close(IN);

####generate scripts for downloading project xml files based on ids
##study
open OUT,">$od/work_sh/download_study_xml_1.sh" or die $!;
open OUTLOG,">$od/data_study/current_xml.log" or die $!;
my $i=1;
while( my @list = splice( @project_ids_list,0,400) ) {
    my $idstr=join(",",@list);
    print OUT "/share/nas2/genome/bin/perl $Bin/download_xml_and_check.pl -type study -idlist $idstr -outxml $current_time_study/${i}.xml\n";
    print OUTLOG "${i}.xml\t$idstr\n";
    $i++;
}
close(OUT);
close(OUTLOG);

##experiments
open OUT,">$od/work_sh/download_exper_xml_1.sh" or die $!;
open OUTLOG,">$od/data_exper/current_xml.log" or die $!;
$i=1;
while( my @list = splice( @experiments_ids_list,0,100) ) {
    my $idstr=join(",",@list);
    print OUT "/share/nas2/genome/bin/perl $Bin/download_xml_and_check.pl -type exper -idlist $idstr -outxml $current_time_exper/${i}.xml\n";
    print OUTLOG "${i}.xml\t$idstr\n";
    $i++;
}
close(OUT);
close(OUTLOG);

###samples
$i=1;
my $try_times=3;
my @samples_ids_list;
my $get_samples_ids_url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=biosample&term=biosample+or+sra&email=xiayh@biomarker.com.cn&tool=PubCrawler_3.0&reldate='.$reldate.'&datetype=pdat&retmax=9999999';
while($try_times>0){
	@samples_ids_list=get_ids($get_samples_ids_url);
	last if(scalar(@samples_ids_list)>0);
	$try_times--;
	sleep 60;
}
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
		sleep 30;
	}
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

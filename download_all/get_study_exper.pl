#!/share/nas2/genome/bin/perl
use strict;
use warnings;
use XML::Simple;
use LWP::Simple;
use FindBin qw($Bin $Script);
use Getopt::Long;
use POSIX;
use Try::Tiny;

my $od;
GetOptions(
	"od:s"=>\$od,
	"help|h"=>\&USAGE,
)or &USAGE;
&USAGE unless($od);

####make directory
mkdir $od  unless (-d $od);
mkdir "$od/data_exper" unless (-d "$od/data_exper");
mkdir "$od/data_study" unless (-d "$od/data_study");
mkdir "$od/work_sh" unless (-d "$od/work_sh");
my $current_time=strftime("%Y%m%d",localtime());
my $current_time_study="$od/data_study/$current_time";
my $current_time_exper="$od/data_exper/$current_time";
mkdir $current_time_study unless (-d $current_time_study);
mkdir $current_time_exper unless (-d $current_time_exper);


####get  project ids
if(! -s "$od/data_study/summary.txt"){
system "wget -q \'ftp://ftp.ncbi.nlm.nih.gov/bioproject/summary.txt\' -O $od/data_study/summary.txt ";
}
my (%old_study_ids,%filter_ids);
if( (-s "$od/data_study/study.id.list" )&& (-s "$od/data_exper/exper.id.list" )){
	open IN_S ,"$od/data_study/study.id.list"  or die $!;
	while(<IN_S>){
		chomp;
		$old_study_ids{$_}=1;
	}
	close(IN_S);
	open IN_E, "$od/data_exper/exper.id.list" or die $!;
	while(<IN_E>){
		chomp;
		my ($s_id)=(split(/\t/))[0];
		$filter_ids{$s_id}=1;
	}
	close(IN_E);
}
my @experiments_ids_list;
open IN,"$od/data_study/summary.txt" or die $!;
open OUT1,">>$od/data_study/study.id.list" or die $!;
open OUT2,">>$od/data_exper/exper.id.list" or die $!;
<IN>;
while(<IN>){
    chomp;
    my ($id)=(split(/\t/))[3];
	next if (exists $filter_ids{$id});
	if(! exists $old_study_ids{$id}){
		print OUT1 $id."\n";
	}
    my $get_exper_ids_url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=sra&tool=PubCrawler_3.0&email=xiayh@biomarker.com.cn&retmax=9999999&retmode=xml&term='.$id.'[bioproject:exp]';
    #push @experiments_ids_list,get_ids($get_exper_ids_url);
	@experiments_ids_list=get_ids($get_exper_ids_url);
	foreach my $i(@experiments_ids_list){
		print OUT2 $id."\t".$i."\n";
	}
}
close(IN);
close(OUT1);
close(OUT2);

=c
####generate scripts for downloading project xml files based on ids
##study
open IN,"$od/data_study/study.id.list" or die $!;
my @project_ids_list=<IN>;
chomp(@project_ids_list);
close(IN);
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
open IN,"$od/data_exper/exper.id.list" or die $!;
my @exper_ids_list=<IN>;
chomp(@exper_ids_list);
close(IN);

open OUT,">$od/work_sh/download_exper_xml_1.sh" or die $!;
open OUTLOG,">$od/data_exper/current_xml.log" or die $!;
$i=1;
while( my @list = splice( @exper_ids_list,0,100) ) {
    my $idstr=join(",",@list);
    print OUT "/share/nas2/genome/bin/perl $Bin/download_xml_and_check.pl -type exper -idlist $idstr -outxml $current_time_exper/${i}.xml\n";
    print OUTLOG "${i}.xml\t$idstr\n";
    $i++;
}
close(OUT);
close(OUTLOG);
###download
system "sh $od/work_sh/download_study_xml_1.sh > $od/work_sh/download_study_xml_1.sh.log 2>&1 ";
system "sh $od/work_sh/download_exper_xml_1.sh > $od/work_sh/download_exper_xml_1.sh.log 2>&1 ";
=cut
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

sub USAGE {
    my $usage=<<"USAGE";
        Options:
        -od <directory>   update directory

USAGE
    print $usage;
    exit;
}

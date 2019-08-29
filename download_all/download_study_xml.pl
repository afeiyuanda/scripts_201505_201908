use strict;
use warnings;
use FindBin qw($Bin $Script);
use Getopt::Long;
use POSIX;

my $od;
GetOptions(
	"od:s"=>\$od,
	"help|h"=>\&USAGE,
)or &USAGE;
&USAGE unless($od);

my $current_time=strftime("%Y%m%d",localtime());
my $current_time_study="$od/data_study/$current_time";
mkdir $current_time_study unless (-d $current_time_study);

system "wget -q \'ftp://ftp.ncbi.nlm.nih.gov/bioproject/summary.txt\' -O $od/data_study/all.txt ";

my @project_ids_list;
open IN,"$od/data_study/all.txt" or die $!;
<IN>;
while(<IN>){
	chomp;
	push @project_ids_list,(split(/\t/,$_))[3];
}
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
system "sh $od/work_sh/download_study_xml_1.sh > $od/work_sh/download_study_xml_1.sh.log 2>&1 ";

sub USAGE {
    my $usage=<<"USAGE";
        Options:
        -od <directory>   update directory

USAGE
    print $usage;
    exit;
}

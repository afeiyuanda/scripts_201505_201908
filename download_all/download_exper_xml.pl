#!/share/nas2/genome/bin/perl
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
my $current_time_exper="$od/data_exper/$current_time";
mkdir $current_time_exper unless (-d $current_time_exper);

my @exper_ids_list;
open IN,"$od/data_exper/exper.id.list" or die $!;
while(<IN>){
	chomp;
	push @exper_ids_list,(split(/\t/,$_))[1];
}
close(IN);

open OUT,">$od/work_sh/download_exper_xml_1.sh" or die $!;
open OUTLOG,">$od/data_exper/current_xml.log" or die $!;
my $i=1;
while( my @list = splice( @exper_ids_list,0,100) ) {
    my $idstr=join(",",@list);
    print OUT "/share/nas2/genome/bin/perl $Bin/download_xml_and_check.pl -type exper -idlist $idstr -outxml $current_time_exper/${i}.xml\n";
    print OUTLOG "${i}.xml\t$idstr\n";
    $i++;
}
close(OUT);
close(OUTLOG);

system "sh $od/work_sh/download_exper_xml_1.sh > $od/work_sh/download_exper_xml_1.sh.log 2>&1 ";
sub USAGE {
    my $usage=<<"USAGE";
        Options:
        -od <directory>   update directory

USAGE
    print $usage;
    exit;
}


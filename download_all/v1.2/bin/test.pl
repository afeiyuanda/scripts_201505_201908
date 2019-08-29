#!/share/nas2/genome/bin/perl
use strict;
use warnings;
use XML::Simple;
use LWP::Simple;
use FindBin qw($Bin $Script);
use Getopt::Long;
use POSIX;
my $od=$ARGV[0];
my $i=1;
my $current_time=strftime("%Y%m%d",localtime());
my $current_time_samples="$od/data_sample/$current_time";
my $get_samples_ids_url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=biosample&term=biosample+or+sra&email=xiayh@biomarker.com.cn&tool=PubCrawler_3.0&reldate=2&datetype=pdat&retmax=9999999';
my @samples_ids_list=get_ids($get_samples_ids_url);
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
sub get_ids{
    my $web_url=shift;
    my @idlist; 
    my $xml_text=get $web_url;
    my $xs = XML::Simple->new;
    my $xml_in = $xs->XMLin($xml_text,ForceArray =>qr/^Id$/);
    foreach my $a ($xml_in->{'IdList'}->{'Id'}){
        if($a){
            push @idlist,@$a;
        }
	}
    return @idlist;
}

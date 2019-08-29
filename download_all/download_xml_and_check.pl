#!/share/nas2/genome/bin/perl
#use utf8;
use FindBin qw($Bin $Script);
#use Text::Iconv;
use lib "$Bin/Text-Unidecode-1.30/lib";
use Text::Unidecode;
use strict;
use warnings;
use Getopt::Long;
use LWP::Simple;
use XML::LibXML;
#use HTML::Entities;
use open     qw(:std :utf8);
use POSIX;
my ($idlist,$outxml,$try_num,$type);

GetOptions(
			"help|h"=>\&USAGE,
			"idlist:s"=>\$idlist,
			"outxml:s"=>\$outxml,
			"try_num:s"=>\$try_num,
            "type:s"=>\$type,
			) or &USAGE;
&USAGE unless($idlist and $outxml and $type);

print strftime('%Y-%m-%d  %H:%M:%S',localtime())." start download $outxml \n";

my $xml_url;
if($type eq "study"){
    $xml_url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=bioproject&retmode=xml&id='.$idlist;
}
elsif($type eq "exper"){
    $xml_url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=sra&retmode=xml&id='.$idlist;
}
elsif($type eq "sample"){
    $xml_url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=biosample&retmode=xml&id='.$idlist;
}
else{
    die "No such type!";
}

my $xml_content;
if($type eq "exper"){
    $try_num||=5;
    while($try_num>=1){
        #print "$xml_url\n";
        $xml_content=get $xml_url;
		#decode_entities($xml_content);
        $xml_content=~s/<!--.*?-->?//smg;
        my @lines=split(/\n/,$xml_content);
        my $lines_num=scalar(@lines);
        if($lines_num==4){
            open XML,">$outxml" or die ;
            print XML"$xml_content";
            close XML;
            last;
        }
        else{
            $try_num--;
        }
    }
}
else{
    $try_num ||=3;
    while($try_num>=1){
        $xml_content=get $xml_url;
        
        ###check xml 
        my $parser = XML::LibXML->new();
        if (eval { $parser->parse_string($xml_content) }) {
            open XML,">$outxml" or die $!;
            print XML "$xml_content";
            close XML;
            last;
        }
        else{
            $try_num--;
        }
    }
}

##############

sub USAGE {
    my $usage=<<"USAGE";
Options:
	-idlist     xml ids 
	-outxml     output file
        -type      study,exper,sample
USAGE
		print $usage;
		exit;
}

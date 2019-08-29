#!/share/nas2/genome/bin/perl
use strict;
use warnings;
use FindBin qw($Bin $Script);
use Getopt::Long;
use POSIX qw/strftime/;
use LWP::UserAgent;
use File::Basename qw(basename dirname);
my ($od,$reldate);
GetOptions(
	"od:s"=>\$od,
	"help|h"=>\&USAGE,
	"reldate:s"=>\$reldate,
)or &USAGE;
&USAGE unless($od);

##
$reldate ||= 2;
####check dir 
my $experiments_dir="$od/data_exper";
my $project_dir="$od/data_study";
my $samples_dir="$od/data_sample";
my $work_sh="$od/work_sh";
my $log_dir="$od/logs";

mkdir $log_dir unless(-d $log_dir);
mkdir $work_sh unless(-d $work_sh);
mkdir $experiments_dir unless(-d $experiments_dir);
mkdir $samples_dir unless (-d $samples_dir);
#die "No $od/data_study/summary.txt.bak file,please check" unless(-e "$od/data_study/summary.txt.bak");
unless(-e "$od/data_study/summary.txt.bak"){
	system "ln $Bin/bin/summary.txt.bak $od/data_study/" ;
}
###check logs and remove old logs 
check_remove_old_logs("$log_dir");

####generate log
my $current_time_log="$log_dir/".strftime("%Y%m%d",localtime()).".log";
open LOG,">$current_time_log" or die ;

####get project ids 
print LOG strftime('%Y-%m-%d  %H:%M:%S',localtime())." download summary.txt from ftp://ftp.ncbi.nlm.nih.gov/bioproject/summary.txt \n";
####download summary.txt and check
my $check_flag=0;
my $try_times=3;
while($try_times>0){
	system "wget -q \'ftp://ftp.ncbi.nlm.nih.gov/bioproject/summary.txt\' -O $project_dir/summary.txt ";
	$check_flag=check_sumary("$project_dir/summary.txt","$project_dir/summary.txt.bak");
	last if($check_flag ==1 );
	$try_times--;
	sleep 60;
}
if($check_flag != 1){
	print LOG strftime('%Y-%m-%d  %H:%M:%S',localtime())." download summary.txt failed because of newtork\n";
	send_email(1,"download summary.txt failed from ftp://ftp.ncbi.nlm.nih.gov/bioproject/summary.txt",$od);
	die "download summary.txt failed";
}
print LOG strftime('%Y-%m-%d  %H:%M:%S',localtime())." download summary.txt done \n";

print LOG strftime('%Y-%m-%d  %H:%M:%S',localtime())." get new ids and generate scripts start \n";
print LOG strftime('%Y-%m-%d  %H:%M:%S',localtime())." /share/nas2/genome/bin/perl $Bin/bin/get_new_ids.pl -od $od -reldate $reldate\n";
system "/share/nas2/genome/bin/perl $Bin/bin/get_new_ids.pl -od $od -reldate $reldate";
print LOG strftime('%Y-%m-%d  %H:%M:%S',localtime())." get new ids and generate scripts done \n"; 

####run download_study_xml_*.sh to download xml files of study;
if(! -e "$od/data_study/download.finish"){
	my @get_study_xml_sh=glob("$od/work_sh/download_study_xml_*.sh");
	if(scalar(@get_study_xml_sh)==0){
		print LOG "ERROR : download xml files of study done or something wrong !\n";
		exit;
	}
	run_sh_check(\@get_study_xml_sh,25);
	check_link("$od/data_study","study");
}

####run download_sample_xml_*.sh to download xml files of sample
if(! -e "$od/data_sample/download.finish"){
	my @get_sample_xml_sh=glob("$od/work_sh/download_sample_xml_*.sh");
	if(scalar(@get_sample_xml_sh)==0){
		print LOG "ERROR : download xml files of sample done or something wrong !\n";
		exit;
	}
	run_sh_check(\@get_sample_xml_sh,25);
	check_link("$od/data_sample","sample");
}
####run download_exper_xml_*.sh to download xml files of experiments
if(! -e "$od/data_exper/download.finish"){
	my @get_exper_xml_sh=glob("$od/work_sh/download_exper_xml_*.sh");
	if(scalar(@get_exper_xml_sh)==0){
		print LOG "ERROR : download xml files of experiments done or something wrong !\n";
		exit;
	}
	run_sh_check(\@get_exper_xml_sh,25);
	check_link("$od/data_exper","exper");
}
####check and remove work_sh
if(-e "$od/data_study/download.finish" && -e "$od/data_sample/download.finish" && -e "$od/data_exper/download.finish"){
	system "rm $od/data_study/download.finish && rm $od/data_sample/download.finish && rm $od/data_exper/download.finish";
	##check download failed
	my $current_date=strftime('%Y-%m-%d',localtime());
	check_download("$od/data_study","$od/${current_date}_study_failed");
	check_download("$od/data_sample","$od/${current_date}_sample_failed");
	check_download("$od/data_exper","$od/${current_date}_exper_failed");
	##parse xml files
	parse_xml_files("$od/data_sample/current_xml","sample");
	parse_xml_files("$od/data_exper/current_xml","expr");
	my $ret=parse_xml_files("$od/data_study/current_xml","pro");
#### get number of ids
	my $study_number=get_number("$od/data_exper/current_xml.log");
	my $exper_number=get_number("$od/data_exper/current_xml.log");
	my $sample_number=get_number("$od/data_sample/current_xml.log");
	if($ret ne "ok"){
		send_email(2,$ret,$od);
	}
	else{
		send_email(3,"Project: $study_number ; Experiment: $exper_number ; Sample: $sample_number ",$od);
	}
	print LOG strftime('%Y-%m-%d  %H:%M:%S',localtime())." update done !\n";
	system "rm -r $od/work_sh";
    
}

###################################
sub check_sumary{
	my $new_file=shift;
	my $old_file=shift;
	my $new_summary=`cat $new_file |wc -l`;
	chomp($new_summary);
	my $old_summary=`cat $old_file |wc -l`;
	chomp($old_summary);
	if($new_summary>=$old_summary){
		return 1;
	}
	else{
		return 0;
	}
}

sub check_link{
	my ($dir,$key)=@_;
	if(! -e "$dir/download.finish"){
		my $current_xml_dir="$dir/current_xml";
		my $current_xml_dirname=get_current_update_dir("$dir");
		system "rm -r $current_xml_dir"if (-e $current_xml_dir);
		system "ln -fs $dir/$current_xml_dirname $current_xml_dir";
        if($key eq "study"){
            system "cp $dir/summary.txt $dir/summary.txt.bak";
        }
		system "touch $dir/download.finish";
		print LOG strftime('%Y-%m-%d  %H:%M:%S',localtime())." download xml files of $key done\n";
	}
}

sub run_sh_check{
	my($commands,$time_check)=@_;
	my @all_sh=@{$commands};
	foreach my $i(@all_sh){
		next if(-e "${i}.finish");
		my $current_hour=strftime("%H",localtime());
		if($current_hour>=9 &&$current_hour<=$time_check){
			print LOG strftime('%Y-%m-%d  %H:%M:%S',localtime())." run $i \n";
			process_cmd($i);
			print LOG strftime('%Y-%m-%d  %H:%M:%S',localtime())." run $i done! \n";
		}
		else{
			exit;
		}
	}
}

sub process_cmd {
    my ($cmd) = @_;
	unless(-e "$cmd.finish"){
		 my $ret = system"sh $cmd >$cmd.log 2>&1";
		if ($ret) {
				 die "Error, cmd: $cmd died with ret $ret";
		}
		system"touch $cmd.finish";
	}
}

sub check_download{
	my ($logfile_dir,$failed_file)=@_;
	my $current_logfile=$logfile_dir."/current_xml.log";
	my $current_xml_dirname=get_current_update_dir($logfile_dir);
	my @error_xml;
	open INLOG,"$current_logfile" or die ;
	while(<INLOG>){
		chomp;
		next if(/^\s*$/);
		my $xmlfile_name=(split(/\t/))[0];
		if(-s "$logfile_dir/$current_xml_dirname/$xmlfile_name"){
			next;
		}
		else{
			 push @error_xml,$_;
		}
	}
	close(INLOG);
	if( scalar(@error_xml)!=0 ){
		open OUT1,">$failed_file" or die ;
		foreach my $i (@error_xml){
			print OUT1 $i."\n";
		}
		close(OUT1);
	}
}

sub get_current_update_dir{
	my ($path)=@_;
	my $current_dirname=0;
	opendir( my $DIR, $path );
	while ( my $entry = readdir $DIR ) {
		next unless -d $path . '/' . $entry;
		next if $entry eq '.' or $entry eq '..';
		next unless($entry=~/^\d+$/);
		if($entry>$current_dirname){
			$current_dirname=$entry;
		}
	}
	closedir $DIR;
	return $current_dirname;
}

sub parse_xml_files{
	my $xml_dir=shift;
	my $type=shift;
	my $return_value;
	my $ua = LWP::UserAgent->new;
	$ua->timeout(3600);
	my $url='http://10.3.129.219:8080/highFlux/analysis?type='.$type.'&path='.$xml_dir;
	my $req = HTTP::Request->new(GET => $url);
	my $res = $ua->request($req);
	if($res->is_success){
		print LOG strftime('%Y-%m-%d  %H:%M:%S',localtime())." parse $type successful \n";
		$return_value='ok';
	}
	else{
		my $status=$res->status_line;
		print LOG strftime('%Y-%m-%d  %H:%M:%S',localtime())." parse $type faile. Error: \'$status\' \n";
		$return_value="parse xml files failed. Error: \'$status\'";
	}
	return $return_value;
}

sub check_remove_old_logs{
	my $logdir=shift;
	my @logs=glob("$logdir/*log");
	if(scalar(@logs)>3){
		my %logs;
		foreach my $i (@logs){
			my $time=basename($i);
			$time=~s/.log//;
			$logs{$time}=$i;
		}
		my @remove_time_keys=sort {$b <=> $a} keys %logs;
		splice @remove_time_keys,0,3;
		foreach my $j (@remove_time_keys){
			system "rm $logs{$j}";
		}
	}
}
sub send_email{
	my $type=shift;
	my $content=shift;
	my $update_dir=shift;
	my $current_time=strftime("%Y%m%d",localtime());
	my ($title,$body);
	if($type == 1){
		$title=$current_time.": SRA Update Failed";
		$body=<<"BODY";
Dear Administrator,
    Cause of failure: $content
    Update directory: $update_dir
BODY
	}
	elsif($type ==2 ){
		$title=$current_time.": SRA Parse Failed";
		$body=<<"BODY";
Dear Administrator,
    Cause of failure: $content
    Update directory: $update_dir
BODY
	}
	else{
		$title=$current_time.": SRA Update Successful";
		$body=<<"BODY";
Dear Administrator,
    Number of ids : $content
    Update directory: $update_dir
BODY
	}
#print "bash $Bin/bin/mail.sh \'$title\' \'$body\'\n";exit;
system "bash $Bin/bin/mail.sh \'$title\' \'$body\' ";
}

sub get_number{
	my $logfile=shift;
	my $num=`cut -f 2 $logfile |sed 's#\,#\\n#g' |wc -l `;
	chomp($num);
	return $num;
}

sub USAGE {
    my $usage=<<"USAGE";
        Options:
        -od <directory>   update directory
	crontab eg:	1 9 */2 * * /share/nas2/genome/bin/perl /share/nas1/qing/toolkits/SRA_update/v1.2/download_in_time_span.pl -od /share/nas1/qing/database/SRA_update_every_two

USAGE
    print $usage;
    exit;
}

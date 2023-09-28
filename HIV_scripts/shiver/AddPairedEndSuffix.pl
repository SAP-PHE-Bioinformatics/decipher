#!/usr/bin/perl
use strict;
use warnings;

my $argLen = 3;


        if(scalar(@ARGV) != $argLen){
        die "\nargument list is not proper.\n\nusage: AddPairedEndTag.pl <fq_in_file> <fq_out_file> <paired-end tag (1 or 2)>\n\n";
        }

        if( ($ARGV[2] != 1) && ($ARGV[2] != 2) ){
        die "\ninvalid paired-end tag (must be 1 or 2)\n";
        }

open FH1,$ARGV[0] or die "\n can not open file $ARGV[0]\n";
open FH2,">$ARGV[1]";  ## output file
my($header,$str,$tempStr,@temp);

        while(<FH1>){
        s/\n//;
        s/\r//;
        @temp = split(/\s+/,$_);

                if($temp[0] =~ m/(\/\d)$/){
                die "\npaired-end tag is already present in the sequence name at line $.\nTerminating\n\n";
                }

        $header = $temp[0]."/$ARGV[2]";
        $str .= $header."\n";
        $str .= <FH1>;
        $str .= <FH1>;
        $str .= <FH1>;
        print FH2 $str;
        splice(@temp);
        $str = "";
        }  ## while(<FH11>) ends
close FH1;
close FH2;

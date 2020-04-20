#!/usr/bin/perl

use strict;
use File::Basename;
use Getopt::Long;

my $notsorted;
my $langOpt = '';

GetOptions ("notsorted" => \$notsorted,
            "language=s" => \$langOpt,
            )
  or Usage();

my $basedir = dirname($0);
$basedir = "." if ($basedir eq "");

my $filename = shift;
my $output = shift;


Usage() if $filename eq "";

#print STDERR "Tokenizing $filename\n";
if ($output ne "") {
    open(OUT, ">$output") or die "Unable to create output file\n";
    select OUT;
}

Declarations($filename, $notsorted);

if ($output ne "") {
    close(OUT);
}

exit;

sub Declarations
{
    my ($filename, $notsorted) = @_;

    #    my $CTAGS = "ctags-exuberant --language-force=c -x";

    my $CTAGS = 'ctags -x ';
    if ($langOpt ne "") {
        $CTAGS .= "--language-force='$langOpt' ";
    }

    if ($notsorted) {
        $CTAGS = $CTAGS . " -u";
    }

    my @declarations;

    open(ctags, "$CTAGS '$filename'|") or die "Unable to execute ctags on file [$filename]";

    while (<ctags>) {
        my %decl;
        my $rest;
        my $line;
        chomp;
        $decl{original} = $_;
        die "unable to parse output ctags [$_]" unless /^(.+?)\s+([^ ]+?)\s+([0-9]+)\s+(.+)$/;
        ($decl{name}, $decl{type}, $decl{line}, $rest) = ($1, $2, $3, $4);
        die "illegal type [$decl{type}] [$_] $decl{name}" unless $decl{type} eq "function" or
                $decl{type} eq "class" or
                $decl{type} eq "macro" or
                $decl{type} eq "member" or
                $decl{type} eq "method" or
                $decl{type} eq "field" or
                $decl{type} eq "constant" or
                $decl{type} eq "package" or
                $decl{type} eq "label" or
                $decl{type} eq "namespace" or
                $decl{type} eq "define" or
                $decl{type} eq "type" or
                $decl{type} eq "enumerator" or
                $decl{type} eq "subroutine" or
                $decl{type} eq "struct" or
                $decl{type} eq "typedef" or
                $decl{type} eq "enum" or
                $decl{type} eq "union" or
                $decl{type} eq "variable" ;

        push @declarations, "DECL|$decl{type}|$decl{name}\n";
    }
    if ($notsorted) {
        print @declarations;
    } else {
        print sort @declarations;
    }
    close ctags;

}

sub Usage {
    print STDERR @_ if @_;
    die "$0 [options]<filename> <outputfile*>\n\n\toptions: --sorted";
}

#include <stdio.h>
#include <stdlib.h>
#include <math.h>   // for exp()
#include <unistd.h> // for sleep()

// make sure that NaN is defined
#ifndef NAN
#error("NaN is not defined")
#endif

/**
 * This program computes a Gaussian for parameters given in an input file.
 * It is designed to serve as an example for large-scale stand-alone codes
 * that need to be supervised by external (e.g. Python) scripts.
 *
 * Build this with
 * gcc main_objective.c -lm -o main_objective
 *
 * Jonathan Schilling (jonathan.schilling@mail.de)
 */

// print some (maybe) helpful text
void print_help(char* argv) {
    printf("%s: a demo code\n", argv);
    printf("run as follows:\n"
           "$ %s <input.txt>\n"
           "  where <input.txt> is the name of the input file\n", argv);
}

// read a line from a given file and parse the line as a floating-point value
double read_line(FILE *fp) {
     // buffer for line to read from input file
    char line[100];

    // read until '\n' newline character and return NaN if no line available
    char *ret = fgets(line, sizeof(line), fp);
    if (ret == NULL) {
        return NAN;
    }

    // parse double from string
    double value = atof(line);

    return value;
}

// compute the value of the Gaussian bell-shaped curve at x for given parameters
double gaussian(double mean, double sigma, double amplitude, double x) {
    return amplitude*exp(-(mean-x)*(mean-x)/(2*sigma*sigma));
}

// main executable
int main(int argc, char** argv) {

    // file pointer for input and output file
    FILE *fp;

    // parameters of Gaussian
    double mean, sigma, amplitude;

    // make sure that exactly one argument is given for input filename (+program name)
    if (argc != 1+1) {
        print_help(argv[0]);
        return -1;
    }

    // open the input file
    fp = fopen(argv[1], "r");
    if (!fp) {
        printf("error: could not open input file '%s'\n", argv[1]);
        return -1;
    }

    // read first line: mean
    mean = read_line(fp);

    // read second line: sigma
    sigma = read_line(fp);

    // read third line: amplitude
    amplitude = read_line(fp);

    // close input file
    fclose(fp);

    // debug output
    printf("got      mean = %g\n", mean);
    printf("got     sigma = %g\n", sigma);
    printf("got amplitude = %g\n", amplitude);

    // checks for consistency of input values
    if (sigma <= 0.0) {
        printf("error: sigma cannot be <= 0\n");
        return -1;
    }
    if (amplitude < 0.0) {
        printf("error: amplitude cannot be < 0\n");
        return -1;
    }

    // output is from -10 to +10
    double min_x = -10.0;
    double max_x =  10.0;

    printf("=> x span from %g to %g\n", min_x, max_x);

    // result of evaluation: 100 points
    int N = 100;
    double x[N];
    double result[N];

    // the main computation of this "code"
    double delta_x = (max_x-min_x)/N;
    for (int i=0; i<N; i++) {
        x[i]      = min_x+i*delta_x;
        result[i] = gaussian(mean, sigma, amplitude, x[i]);
    }

    // this is heavy workload, so it takes some time....
    //sleep(1);

    // write the result to an output file
    fp = fopen("output.txt", "w");
    for (int i=0; i<N; i++) {
        fprintf(fp, "%g %.25f\n", x[i], result[i]);
    }
    fclose(fp);

    return 0;
}

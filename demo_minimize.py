#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 21:47:59 2021

@author: Jonathan Schilling (jonathan.schilling@mail.de)
"""

###### wrapper to execute some stand-alone code
###### and organize results in unique folders per input file

import os
import subprocess

# absolute path to executable
# in this demo, this needs to be compiled from main_objective.c
path_to_code = os.path.join(os.getcwd(), 'main_objective')

# absolute path to directory where runs of the code are to be stored
working_dir = os.path.join(os.getcwd(), 'runs')

# default name of input file
default_input_filename = "input.txt"

# default name of output file
default_output_filename = "output.txt"

# create working directory (if not exists already)
if not os.path.isdir(working_dir):
    os.makedirs(working_dir)
print("working directory: "+working_dir)


# write the input file with given parameters
def write_input(input_filename, parameters):
    # check that correct number of parameters is given
    if len(parameters) != 3:
        raise RuntimeError("number of parameters has to be 3: "
                           +"(mean, sigma, amplitude)")
    
    # split into individual input parameters
    mean      = parameters[0]
    sigma     = parameters[1]
    amplitude = parameters[2]
        
    # actually write input file
    with open(input_filename, "w") as input_file:
        input_file.write("%.25e\n"%(mean,))
        input_file.write("%.25e\n"%(sigma,))
        input_file.write("%.25e\n"%(amplitude,))

# read output file and return results found in it
def read_output(output_filename):
    # check if output file exists (== code was successful)
    if not os.path.isfile(output_filename):
        return None
    
    # read all lines of the output file
    lines = []
    with open(output_filename, "r") as output_file:
        lines = output_file.readlines()
    
    # parse the outputs line by line
    x = []
    results = []
    for line in lines:
        parts = line.split(" ")
        
        x.append(float(parts[0]))
        results.append(float(parts[1]))
        
    return x, results

# call code to compute something and return results from output file
def call_code(parameters):

    # write temporary input file 
    temp_input_filename = os.path.join(working_dir, default_input_filename)
    write_input(temp_input_filename, parameters)
    
    # generate md5sum of input file
    md5sum_output = subprocess.run(["md5sum", temp_input_filename],
                                   capture_output=True)
    input_md5sum = md5sum_output.stdout.decode().split(" ")[0]
    runId = "run_"+input_md5sum
    
    print("run id: "+runId)
    
    # path to a folder dedicated to this run
    run_folder = os.path.join(working_dir, runId)
    
    # check if run folder already exists and read output if available
    if not os.path.isdir(run_folder):
        
        # create a folder dedicated to this run
        os.makedirs(run_folder)
        
        # move temporary input file into run folder (=rename it)
        os.rename(temp_input_filename, os.path.join(run_folder, default_input_filename))
        
        # remember current working directory so we can return to it later
        old_cwd = os.getcwd()
        
        # actually call the code and check if it executed correctly
        output = subprocess.run([path_to_code, default_input_filename],
                                capture_output=True, cwd=run_folder)
        print(output.stdout.decode())
        print(output.stderr.decode())
        if output.returncode != 0:
            # run was not successful, print an error message
            print("Error: run %s failed"%(runId,))
            return None

        # change back to previous working directory
        os.chdir(old_cwd)
    else:
        print("  run already exists, skipping execution :-)")
        
    # run was already performed or successful now, so can read output file
    return read_output(os.path.join(run_folder, default_output_filename))
        


######### SciPy optimizer operating on runs of above wrapped code #########

import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import minimize

if __name__=='__main__':
    
    # target parameters
    target_mean = 5.0
    target_sigma = 1.0
    target_ampl = 0.1
    target_parameters = [target_mean, target_sigma, target_ampl]
    
    # evaluation points; has to match code in main_objective.c here
    N = 100
    min_x = -10.0
    max_x =  10.0
    x = np.arange(min_x, max_x, (max_x-min_x)/N)
    
    # evaluate objective function at target parameters
    _, target_result = call_code(target_parameters)
    
    # define boundaries for input parameters
    bounds = [(-np.Inf, np.Inf), (0.0, np.Inf), (0.0, np.Inf)]
    
    # chi-squared error objective
    # - evaluate your code with parameters given in x
    # - compare results of the code with target_result
    def objective(x):
        print("eval at "+str(x))
        eval_result = call_code(x)
        if eval_result is not None:
            return np.sum((np.subtract(target_result, eval_result))**2)
        else:
            return np.Infinity

    # debug plot of target result
    plt.figure()
    plt.plot(x, target_result, label='target')
    
    ### in a real-world example you probably will have the target
    ### from somewhere else that the code to produce them itself...
    
    # number of free parameters
    n = 3
    
    # initial guess for parameters; only has to give a valid result
    x0 = [2.5, 1.0, 0.2]

    # plot initial guess 
    _, initial_result = call_code(x0)
    plt.plot(x, initial_result, 'k--', label='initial')
    
    print("objective function at initial parameters: %g"%(objective(x0)))
    
    # call optimizer
    solution = minimize(objective, x0, method='SLSQP', bounds = bounds)
    #solution = minimize(objective, x0, method='L-BFGS-B', bounds = bounds)
    final_parameters = solution.x
    
    # plot final result 
    _, final_result = call_code(final_parameters)
    plt.plot(x, final_result, 'r.', label='final')
    
    print("objective function at final parameters: %g"%(objective(final_parameters)))
    
    plt.legend()
    plt.grid(True)
    
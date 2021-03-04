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
path_to_code = "/data/jonathan/work/code/demo_minimize/main_objective"

# absolute path to directory where runs of the code are to be stored
working_dir = "/data/jonathan/work/code/demo_minimize/runs/"

# default name of input file
default_input_filename = "input.txt"

# default name of output file
default_output_filename = "output.txt"

# make sure that working directory can be used as a path
if not working_dir.endswith("/"):
    working_dir += "/"

# create working directory (if not exists already)
if not os.path.exists(working_dir):
    os.mkdir(working_dir)
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
        input_file.write("%g\n"%(mean,))
        input_file.write("%g\n"%(sigma,))
        input_file.write("%g\n"%(amplitude,))

# read output file and return results found in it
def read_output(output_filename):
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
    temp_input_filename = working_dir+default_input_filename
    write_input(temp_input_filename, parameters)
    
    # generate md5sum of input file
    md5sum_output = subprocess.run(["md5sum", temp_input_filename],
                                   capture_output=True)
    input_md5sum = md5sum_output.stdout.decode().split(" ")[0]
    runId = "run_"+input_md5sum
    
    print("run id: "+runId)
    
    # path to a folder dedicated to this run
    run_folder = working_dir+runId+"/"
    
    # check if run folder already exists and read output if available
    if not os.path.exists(run_folder):
        
        # create a folder dedicated to this run
        os.mkdir(run_folder)
        
        # move temporary input file into run folder (=rename it)
        os.rename(temp_input_filename, run_folder+default_input_filename)
        
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
    return read_output(run_folder+default_output_filename)
        





######### SciPy optimizer operating on runs of above wrapped code #########


import numpy as np
from scipy.optimize import minimize


    
    




def objective(x):
    return x[0]*x[3]*(x[0]+x[1]+x[2])+x[2]

def constraint1(x):
    return x[0]*x[1]*x[2]*x[3]-25.0

def constraint2(x):
    sum_eq = 40.0
    for i in range(4):
        sum_eq = sum_eq - x[i]**2
    return sum_eq


if __name__=='__main__':
        
    # initial guesses
    n = 4
    x0 = np.zeros(n)
    x0[0] = 1.0
    x0[1] = 5.0
    x0[2] = 5.0
    x0[3] = 1.0
    
    # show initial objective
    print('Initial SSE Objective: ' + str(objective(x0)))
    
    # optimize
    b = (1.0,5.0)
    bnds = (b, b, b, b)
    con1 = {'type': 'ineq', 'fun': constraint1} 
    con2 = {'type': 'eq', 'fun': constraint2}
    cons = ([con1,con2])
    solution = minimize(objective,x0,method='SLSQP',\
                        bounds=bnds,constraints=cons)
    x = solution.x
    
    # show final objective
    print('Final SSE Objective: ' + str(objective(x)))
    
    # print solution
    print('Solution')
    print('x1 = ' + str(x[0]))
    print('x2 = ' + str(x[1]))
    print('x3 = ' + str(x[2]))
    print('x4 = ' + str(x[3]))
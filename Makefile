
# compiler
CC=gcc

.PHONY: all

all: main_objective

main_objective: main_objective.c
	${CC} main_objective.c -lm -o main_objective


## How to run my code?

- Clone the repo in your system
- add the desired .s or .asm file in folder
- Open InputFile.py
- Change name of input file in `file = open('Test.s', 'r')` to your file name
- Run Main.py

## What to use as -

- ### Constants
  ##### Only integer values
- ### AddressLocation
  ##### Address of other code
- ### MemoryAddress
  ##### Address of information in data segment

## Errors to expect

- ### TOO LESS ARGUMENTS
- ### INSTRUCTION DO NOT EXISTS
- ### SYNTAX ERROR

## Termination

- ### `jr $ra` instruction occurs
- ### Some error occurs

## Other rules

- ### Memory segment address starts with `0`
- #### Word has 4 bytes
- #### Values are stored in hexadecimal
- #### Constants given to code as numbers need to be in decimal

* #### if value is negative it is shown in x-value type
* #### One step and step by step execution is available

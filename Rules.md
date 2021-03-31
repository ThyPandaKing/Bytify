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


## How to delete,add and replace instructions -

- You will be able to see options below the text.
  - In the change type you will be able to select one of the option
    - If you select delete,then give the PC value of the instruction to be deleted which can be seen in the text segment
    - If you select add, then the instruction will be added at the PC value that is entered.
    - If you select replace,then the instruction will be replaced with  the instruction given by you at the given PC value.
  - Then enter the submit button and you will be able to see the changes.  

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

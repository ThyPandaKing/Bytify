## PIPELINING
#### ABOUT 
1. It is a way to implement an instruction in a feasible way by parallalizing it.
2. It has 5 stages namely:
   - Instruction fetch(IF)
   - Instruction decode/register fetch(ID/RF)
   - Execution(EXE)
   - Memory(MEM)
   - Write back(WB)
3. If somehow parallelization is not possible, then the instruction stream stops for some clock cycles and that stop is known as **stalls**.
4. To reduce number of stalls, a mechanism known as **data forwarding** is implemented.
   Where we forward data from one pipeline stage to another pipeline stage.
5. Even though data forwarding is a wonderful mechanism, in some cases we encounter with stalls.   


 #### OUR IMPLEMENTATION

- We have implemented a  2-D array system which is a **simulated version** of data Forwarding registers which stores the information which is to be passed from one instruction to another.
- After instruction decode stage we check for stalls.
- In case of arithmetic/bitwise instruction, we check the data dependency in the **previous two instructions**.(stalls can come only due to dependency in previous two instructions).
   - If data forwarding is **allowed** and previous instruction was not a load word, then we simply **forward the data**.
   - In case data forwarding is  **not allowed**, we add **three stalls** as we will be able to get the information only after the write-back stage.
   - In case of **load word**, the result is not available after the execution stage, so we need to wait till the memory stage which results in **one stall**.
- In case of branch instruction, we have tried to implement a **Branch not taken predictor** which only results in a stall if branch is taken.
- At the end **average IPC** will be evaluated.
- Information about data forwarding and stalls will be displayed during runtime.

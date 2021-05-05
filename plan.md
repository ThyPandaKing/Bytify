# 2d list with classes

if this is the case

10001011010011001010111100101 0 10 ->

| set1            | set2            |
| --------------- | --------------- |
| clock1 : clock2 | clock1 : clock2 |
| tag1 : tag2     | tag3 : tag4     |
| value1 : value2 | value3 : value4 |
| value1 : value2 | value3 : value4 |
| value1 : value2 | value3 : value4 |
| value1 : value2 | value3 : value4 |

offset = log(blocks)
index = log(set_number)
set_number = total_blocks/associativity
total_blocks = total_bytes/block_size

## Functions

- index bits/offset bits/tag bits -> normal fun
- set_finder -> take address and return which set to go -> normal fun
- find_tag -> search all the tags in set and return true/false and if true then also fetch value -> find_tag(set)
- find_offset -> return offset value (if find_tag return true)
- fetch_from_next -> if find tag return false, then we go to next memory level and fetch this new value, put it in block , by LRU policy , also we add stalls accordingly.

- LRU -> find minimum clock value's index in tag array to be replaced.
- update_results -> update the value of number in all array (strick through)
- fill_tag -> fill values in tag array
- non-inclusive/exclusive -> which ever is easy to implement

block size = 4 -> 1 integer
n size ka block -> n/4

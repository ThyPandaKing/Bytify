# Cache

## About

- Cache is used to reduce time of memory access done due to it's high clock cycle time.
- It keeps frequently used data in a location which is faster to access
- It divides the address into 3 part
  - Tag
  - Index
  - Offset
- Offset is calculated using block size as when a memory segment is accessed it brings an entire block with it.

  - `Offset_bits = log2(block size)`

- Index is calculated using cache size , block size , associativity

  - `number of blocks = cache size / block size`
  - `number of sets = number of blocks / associativity`
  - `index_bits = log2(number of sets)`

- Tag bits are the remaining bits of address
  - `Tag_bits = total_bits - index_bits - offset_bits`
- Search happens in order
  - `Index->Tag->offset`
- Replacement Policies are some rule how our blocks will gonna replace each-other.
- Memory updating method are used to update data in main memory.

## Our Implementation

- Used two level of cache
- Information of all the needed variables is taken in form of a file.
- If not given then our own cache data will be used.
- Used LRU replacement Policy
- Used Strick through for data updating as we needed data to be updated simultaneously because we needed it to be shown to user for user to get a better experience of software.

# Billion Record Challenge

More details of the challenge at [blog post](https://www.morling.dev/blog/one-billion-row-challenge/)

The main limitation is allowing the use of only built-in functionality.

Note: I allowed myself to use external libs for work with command line arguments.

---


## Testing (Development) Environment
- **System type:** Windows 11 Pro, 64-bit, x64-based processor
- **Processor:** AMD Ryzen 5 3600 6-Core Processor 3.59 GHz
- **RAM:** 128 GB
- **Disk:** Samsung SSD 970 EVO Plus 1TB

---


## Goal
I've just decided to do it by myself with my primary languages (C++ and Python) and Rust (I've been learning it at the moment)

I will try to add grids with progress improvements for each language.

---


### Python (3.12, Cython)
#### Windows
| Time            | Delta            | Notes                                                                                            |
|-----------------|------------------|--------------------------------------------------------------------------------------------------|
| 17:23:284       |                  | Naive + Buffed I/O                                                                               |
| 11:06:184       | +06:17:100       | Read file in binary mode<br/>Remove debug prints<br/>Remove unnecessary allocations, assignments |
| 10:52:539       | +00:13:644       | Memory file mapping                                                                              |
| **_02:10:640_** | **_+08:41:899_** | **_Multicore execution (12 CPU)_**                                                               |
| 02:47:864       | -00:37:223       | Change temperatures representation, parsing and processing                                       |
| 03:28:583       | -00:40:719       | [Bonus] Replace two fragments of `if x lesser/greater b then x = b` with `x = min/max(x, b)`     |


#### WSL (Ubuntu 24)
| Time            | Delta            | Notes                                                                                            |
|-----------------|------------------|--------------------------------------------------------------------------------------------------|
| 18:24:421       |                  | Naive + Buffed I/O                                                                               |
| 07:46:911       | +10:37:509       | Read file in binary mode<br/>Remove debug prints<br/>Remove unnecessary allocations, assignments |
| 07:37:350       | +00:09:561       | Memory file mapping                                                                              |
| **_01:19:774_** | **_+06:17:576_** | **_Multicore execution (12 CPU)_**                                                               |
| 02:00:558       | -00:40:783       | Change temperatures representation, parsing and processing                                       |
| 02:46:462       | -00:45:904       | [Bonus] Replace two fragments of `if x lesser/greater b then x = b` with `x = min/max(x, b)`     |

---


### Python (3.10, Pypy)
#### Windows 11
| Time            | Delta            | Notes                                                                                            |
|-----------------|------------------|--------------------------------------------------------------------------------------------------|
| 05:54.979       |                  | Naive + Buffed I/O                                                                               |
| 04:38:311       | +01:16:668       | Read file in binary mode<br/>Remove debug prints<br/>Remove unnecessary allocations, assignments |
| 04:16:455       | +00:21:856       | Memory file mapping                                                                              |
| 00:41:926       | +03:34:528       | Multicore execution (12 CPU)                                                                     |
| **_00:16:316_** | **_+00:25:609_** | **_Change temperatures representation, parsing and processing_**                                 |
| 00:16:316       | +00:00:000       | [Bonus] Replace two fragments of `if x lesser/greater b then x = b` with `x = min/max(x, b)`     |


#### WSL (Ubuntu 24)
| Time            | Delta            | Notes                                                                                            |
|-----------------|------------------|--------------------------------------------------------------------------------------------------|
| 04:05.491       |                  | Naive + Buffed I/O                                                                               |
| 03:00:459       | +01:05:031       | Read file in binary mode<br/>Remove debug prints<br/>Remove unnecessary allocations, assignments |
| 02:51:380       | +00:09:079       | Memory file mapping                                                                              |
| 00:24:733       | +02:26:646       | Multicore execution (12 CPU)                                                                     |
| **_00:13:887_** | **_+00:10:846_** | **_Change temperatures representation, parsing and processing_**                                 |
| 00:13:887       | +00:00:000       | [Bonus] Replace two fragments of `if x lesser/greater b then x = b` with `x = min/max(x, b)`     |

---


### Rust
#### Windows 11
| Time            | Delta            | Notes                                                            |
|-----------------|------------------|------------------------------------------------------------------|
| 05:44:451       | 0                | Naive + Buffed I/O                                               |
| 03:21:331       | +02:23:120       | Remove debug prints<br/>Remove unnecessary allocations           |
| 02:54:161       | +00:27:170       | Change temperatures representation, parsing and processing       |
| 02:40:729       | +00:13:432       | Replace default hash algorithm with FNV                          |
| 01:37:834       | +01:02:895       | Speed up file reading using `BufReader::read_line`               |
| 01:04:801       | +00:33:033       | Read file in binary mode<br/>Turn off utf-8 sequences validation |
| **_00:08:992_** | **_+00:55:808_** | **_Multicore execution (12 CPU)_**                               |


#### WSL (Ubuntu 24)
| Time            | Delta            | Notes                                                            |
|-----------------|------------------|------------------------------------------------------------------|
| 02:39:606       | 0                | Naive + Buffed I/O                                               |
| 02:03:929       | +00:35:676       | Remove debug prints<br/>Remove unnecessary allocations           |
| 01:38:455       | +00:25:474       | Change temperatures representation, parsing and processing       |
| 01:26:030       | +00:12:425       | Replace default hash algorithm with FNV                          |
| 01:11:196       | +00:14:833       | Speed up file reading using `BufReader::read_line`               |
| 00:49:090       | +00:22:106       | Read file in binary mode<br/>Turn off utf-8 sequences validation |
| **_00:06:114_** | **_+00:42:975_** | **_Multicore execution (12 CPU)_**                               |

---


### C++
#### Windows 11, msvc
| Time      | Delta      | Notes                                                                               |
|-----------|------------|-------------------------------------------------------------------------------------|
| 05:25:736 | 0          | Naive + Buffed I/O                                                                  |
| 04:40:763 | +00:44:972 | Remove debug prints<br/>Read file in binary mode<br/>Remove unnecessary allocations |
| 03:01:995 | +01:38:768 | Change temperatures representation, parsing and processing                          |


#### WSL (Ubuntu 24), gcc
| Time      | Delta      | Notes                                                                               |
|-----------|------------|-------------------------------------------------------------------------------------|
| 01:19:791 | 0          | Naive + Buffed I/O                                                                  |
| 01:08:614 | +00:11:176 | Remove debug prints<br/>Read file in binary mode<br/>Remove unnecessary allocations |
| 00:58:587 | +00:10:026 | Change temperatures representation, parsing and processing                          |

---

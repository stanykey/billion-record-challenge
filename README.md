# Billion Record Challenge

More details of the challenge at [blog post](https://www.morling.dev/blog/one-billion-row-challenge/)

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
| Time      | Delta      | Notes                                                                                            |
|-----------|------------|--------------------------------------------------------------------------------------------------|
| 17:23:284 |            | Naive + Buffed I/O                                                                               |
| 11:06:184 | +06:17:100 | Read file in binary mode<br/>Remove debug prints<br/>Remove unnecessary allocations, assignments |
| 10:52:539 | +00:13:644 | Memory file mapping                                                                              |
| 02:10:640 | +08:41:899 | Multicore execution (12 CPU)                                                                     |
| 02:47:864 | -00:37:223 | Change temperatures representation, parsing and processing                                       |


#### WSL (Ubuntu 24)
| Time      | Delta      | Notes                                                                                            |
|-----------|------------|--------------------------------------------------------------------------------------------------|
| 18:24:421 |            | Naive + Buffed I/O                                                                               |
| 07:46:911 | +10:37:509 | Read file in binary mode<br/>Remove debug prints<br/>Remove unnecessary allocations, assignments |
| 07:37:350 | +00:09:561 | Memory file mapping                                                                              |
| 01:19:774 | +06:17:576 | Multicore execution (12 CPU)                                                                     |
| 02:00:558 | -00:40:783 | Change temperatures representation, parsing and processing                                       |

---


### Python (3.10, Pypy)
#### Windows 11
| Time      | Delta      | Notes                                                                                            |
|-----------|------------|--------------------------------------------------------------------------------------------------|
| 05:54.979 |            | Naive + Buffed I/O                                                                               |
| 04:38:311 | +01:16:668 | Read file in binary mode<br/>Remove debug prints<br/>Remove unnecessary allocations, assignments |
| 04:16:455 | +00:21:856 | Memory file mapping                                                                              |
| 00:41:926 | +03:34:528 | Multicore execution (12 CPU)                                                                     |
| 00:16:316 | +00:25:609 | Change temperatures representation, parsing and processing                                       |


#### WSL (Ubuntu 24)
| Time      | Delta      | Notes                                                                                            |
|-----------|------------|--------------------------------------------------------------------------------------------------|
| 04:05.491 |            | Naive + Buffed I/O                                                                               |
| 03:00:459 | +01:05:031 | Read file in binary mode<br/>Remove debug prints<br/>Remove unnecessary allocations, assignments |
| 02:51:380 | +00:09:079 | Memory file mapping                                                                              |
| 00:24:733 | +02:26:646 | Multicore execution (12 CPU)                                                                     |
| 00:13:887 | +00:10:846 | Change temperatures representation, parsing and processing                                       |

---


### Rust
| Time      | Delta      | Notes                                                   |
|-----------|------------|---------------------------------------------------------|
| 05:44:451 | 0          | Naive + Buffed I/O                                      |
| 04:04:033 | +01:40:418 | Remove unnecessary allocations, assignments, and prints |
| 03:58:401 | +00:05:631 | Build result with String::push_str and then print       |

---


### C++
| Time      | Delta      | Notes                                                   |
|-----------|------------|---------------------------------------------------------|
| 05:25:736 | 0          | Naive + Buffed I/O                                      |
| 05:16:365 | +00:09:371 | Remove unnecessary allocations, assignments, and prints |

---

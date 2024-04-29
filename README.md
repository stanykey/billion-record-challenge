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
| Approach | Time      | Delta      | Notes                                                                                            |
|----------|-----------|------------|--------------------------------------------------------------------------------------------------|
| Naive    | 17:23:284 |            | Buffed I/O                                                                                       |
| Naive+   | 11:06:184 | +06:17:100 | Read file in binary mode<br/>Remove debug prints<br/>Remove unnecessary allocations, assignments |
| Naive+   | 10:52:539 | +00:13:644 | Memory file mapping                                                                              |

#### WSL (Ubuntu 24)
| Approach | Time      | Delta      | Notes                                                                                            |
|----------|-----------|------------|--------------------------------------------------------------------------------------------------|
| Naive    | 18:24:421 |            | Buffed I/O                                                                                       |
| Naive+   | 07:46:911 | +10:37:509 | Read file in binary mode<br/>Remove debug prints<br/>Remove unnecessary allocations, assignments |
| Naive+   | 07:37:350 | +00:09:561 | Memory file mapping                                                                              |

---


### Rust
| Approach | Time      | Delta      | Notes                                                   |
|----------|-----------|------------|---------------------------------------------------------|
| Naive    | 05:44:451 | 0          | Buffed I/O                                              |
| Naive+   | 04:04:033 | +01:40:418 | Remove unnecessary allocations, assignments, and prints |
| Naive++  | 03:58:401 | +00:05:631 | Build result with String::push_str and then print       |

---


### C++
| Approach | Time      | Delta      | Notes                                                   |
|----------|-----------|------------|---------------------------------------------------------|
| Naive    | 05:25:736 | 0          | std::iostreams suck                                     |
| Naive+   | 05:16:365 | +00:09:371 | Remove unnecessary allocations, assignments, and prints |

---

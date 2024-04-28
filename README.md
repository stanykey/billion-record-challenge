# Billion Record Challenge

More details of the challenge at [blog post](https://www.morling.dev/blog/one-billion-row-challenge/)

---


## Testing Environment
- **Processor:** AMD Ryzen 5 3600 6-Core Processor                 3.59 GHz
- **RAM:** 128 GB
- **System type:** Windows 11 Pro, 64-bit, x64-based processor
- **Disk:** Samsung SSD 970 EVO Plus 1TB
---


## Goal
I've just decided to do it by myself with my primary languages (C++ and Python) and Rust (I've been learning it at the moment)

I will try to add grids with progress improvements for each language.

---


### Python (3.11, Cython)
| Approach | Time      | Delta      | Notes                                                   |
|----------|-----------|------------|---------------------------------------------------------|
| Naive    | 17:23:284 | 0          | Buffed I/O                                              |
| Naive+   | 09:47:801 | +07:35:483 | Remove unnecessary allocations, assignments, and prints |
| Naive++  | 09:32:318 | +00:15:483 | StringIO to speed up the generating of results          |
| Naive++  | 10:09:501 | -00:37:182 | Add more functions for readability purposes             |
| Naive++  | 09:53:063 | +00:16:437 | Switch onto reading in binary mode                      |

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

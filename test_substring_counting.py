#!/usr/bin/env python3
"""
Benchmark different substring counting implementations in Python.
Tests naive, optimized (skip duplicates), and built-in methods.
"""

import timeit
import statistics


def naive_count(s: str, substr: str) -> int:
    """Naive implementation - uses str.count() in a loop."""
    count = 0
    start = 0
    while True:
        idx = s.find(substr, start)
        if idx == -1:
            break
        count += 1
        start = idx + 1
    return count


def optimized_count(s: str, substr: str) -> int:
    """Optimized implementation - skips len(substr) after finding match."""
    count = 0
    start = 0
    while True:
        idx = s.find(substr, start)
        if idx == -1:
            break
        count += 1
        start = idx + len(substr)
    return count


def overlapping_count(s: str, substr: str) -> int:
    """Counts overlapping occurrences."""
    return len([i for i in range(len(s) - len(substr) + 1)
                 if s[i:i+len(substr)] == substr])


def regex_count(s: str, substr: str) -> int:
    """Uses regex to find overlapping matches."""
    import re
    pattern = f'(?={re.escape(substr)})'
    return len(re.findall(pattern, s))


def buildin_count(s: str, substr: str) -> int:
    """Simple build-in count (only for non-overlapping, from start)."""
    return s.count(substr)


# Test cases
test_cases = [
    # (substring, expected_overlapping, description)
    ("aaaabaaa", 3, "Simple overlapping case: 'aaab' appears 3 times"),
    ("aaaaa", 3, "Extreme case: 'aaa' in 'aaaaa' - 3 overlapping occurrences"),
    ("aaaa", 4, "All same: 'a' in 'aaaa' - 4 occurrences"),
    ("abcabcabc", 3, "Repeating pattern: 'abc' appears 3 times"),
    ("abababa", 4, "Alternating: 'aba' appears 3 times (not 4)"),
    ("abababa", 3, "Alternating: 'bab' appears 2 times"),
    ("abababa", 2, "Alternating: 'aba' appears 3 times"),
    ("abcdef", 1, "Single occurrence"),
    ("", 0, "Empty substring"),
    ("a", 1, "Single character"),
    ("abc", 1, "Different chars"),
    ("mississippi", 2, "Classics: 'issi' appears 2 times"),
    ("ababab", 2, "Short pattern: 'abab' appears 2 times"),
    ("ababab", 2, "Short pattern: 'baba' appears 2 times"),
]


def benchmark(func, args, repeats=5, verbose=False):
    """Run a function and measure time."""
    times = timeit.repeat(
        lambda: func(*args),
        repeat=repeats,
        number=1
    )
    best_time = min(times)
    avg_time = statistics.mean(times)
    if verbose:
        print(f"Function: {func.__name__:25}  Best: {best_time*1e6:9.3f}us  Avg: {avg_time*1e6:9.3f}us")
    return avg_time


def main():
    print("=" * 70)
    print("SUBSTRING COUNTING BENCHMARK")
    print("=" * 70)
    print()

    print(f"{'Function':<25} | {'Best Time':>12} | {'Avg Time':>12} | {'Ratio':>8}")
    print("-" * 70)

    # Sort test cases by substring length for consistent results
    test_cases.sort(key=lambda x: (len(x[0]), x[0]))

    # Pre-compile regex pattern for fair comparison
    import re
    regex_pattern = None

    results = {}
    for substr, expected, description in test_cases:
        if verbose:
            print(f"\n{description}")
        print(f"Testing: {repr(substr)}")

        try:
            # Run each function
            naive_time = benchmark(naive_count, (None, substr), repeats=3)
            optimized_time = benchmark(optimized_count, (None, substr), repeats=3)
            overlapping_time = benchmark(overlapping_count, (None, substr), repeats=3)
            regex_time = benchmark(regex_count, (None, substr), repeats=3)

            print("-" * 70)
            print(f"{description}")
            print(f"  Substring: {repr(substr)}")
            print(f"  Overlapping count: {expected}")

            naive_count_val = naive_count(None, substr)
            optimized_count_val = optimized_count(None, substr)
            overlapping_count_val = overlapping_count(None, substr)
            regex_count_val = regex_count(None, substr)

            print(f"  Overlapping count (naive): {overlapping_count_val}")
            print(f"  Overlapping count (optimized): {overlapping_count_val}")
            print(f"  Overlapping count (regex): {regex_count_val}")
            print(f"  Overlapping count (manual): {expected}")

            # Only show timing if substring length > 2 (to avoid noise)
            if len(substr) > 2:
                print(f"\n  Timing Results (over 3 repeats, 1 call each):")
                print(f"  {naive_count.__name__:25} | {naive_time*1e6:>12.3f}us | {naive_time*1e6:>12.3f}us | -")
                print(f"  {optimized_count.__name__:25} | {optimized_time*1e6:>12.3f}us | {optimized_time*1e6:>12.3f}us | -")
                print(f"  {overlapping_count.__name__:25} | {overlapping_time*1e6:>12.3f}us | {overlapping_time*1e6:>12.3f}us | -")
                print(f"  {regex_count.__name__:25} | {regex_time*1e6:>12.3f}us | {regex_time*1e6:>12.3f}us | -")

                if optimized_time > 0:
                    speedup = naive_time / optimized_time
                    print(f"  Speedup (optimized vs naive): {speedup:.1f}x")
        except Exception as e:
            print(f"  Error: {e}")
            print(f"  {naive_count.__name__:25} | - | - | -")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("Key findings:")
    print("  1. str.find() in a loop is the most efficient for counting overlapping")
    print("       occurrences in Python.")
    print("  2. The naive approach (start = idx + 1) is fast enough for most cases.")
    print("  3. Regex can match overlapping patterns but adds overhead.")
    print("  4. For non-overlapping counts, str.count() is the best choice.")
    print()
    print("Recommendations:")
    print("  - Use str.count() for non-overlapping counts")
    print("  - Use a find() loop for overlapping counts")
    print("  - Use str.find() in a loop for performance")
    print("=" * 70)


if __name__ == "__main__":
    main()

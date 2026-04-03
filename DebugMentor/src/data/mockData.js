// =============================================
// DEBUGMENTOR — MOCK DATA (Multi-Scenario + Multi-Mode)
// =============================================

// ─── Scenario 1: Empty array / index-out-of-range ───────────────────────────
export const scenario_emptyArray = {
  id: 'empty_array',
  status: "bugs_found",
  executionOutput: "IndexError: list index out of range",
  errorLine: 2,
  bugSummary: "Edge case failure on empty array input",
  hints: [
    {
      level: 1, title: "Directional nudge", icon: "💡",
      text: "Think carefully about what happens when the input array has **no elements at all**. Does your function handle that gracefully?"
    },
    {
      level: 2, title: "More specific", icon: "💡",
      text: "Your code accesses `arr[0]` before checking if `arr` has any elements. If the list is empty, this line throws an **IndexError: list index out of range**."
    },
    {
      level: 3, title: "Full solution", icon: "🔓",
      text: "Add a guard clause at the top: `if not arr: return None`. This safely handles the empty input case before any array access."
    }
  ],
  testCases: [
    { id: 1, input: "[3,1,4,1,5]", expected: "5",    actual: "5",    passed: true  },
    { id: 2, input: "[]",          expected: "None",  actual: "ERROR", passed: false },
    { id: 3, input: "[-1,-5,-2]",  expected: "-1",   actual: "-1",   passed: true  },
    { id: 4, input: "[1]",         expected: "1",     actual: "1",    passed: true  }
  ]
}

// ─── Scenario 2: Off-by-one loop error ──────────────────────────────────────
export const scenario_offByOne = {
  id: 'off_by_one',
  status: "bugs_found",
  executionOutput: "Wrong answer on boundary inputs",
  errorLine: 3,
  bugSummary: "Off-by-one error — loop skips the last element",
  hints: [
    {
      level: 1, title: "Directional nudge", icon: "💡",
      text: "Your loop is producing incorrect results on some inputs. Think carefully about where your loop **starts and stops** — are you visiting every element?"
    },
    {
      level: 2, title: "More specific", icon: "💡",
      text: "The loop condition `i < len(arr) - 1` stops **one element early**, so the last element is never compared. Change it to `i < len(arr)` or use `range(len(arr))`."
    },
    {
      level: 3, title: "Full solution", icon: "🔓",
      text: "Fix the loop bound: `for i in range(len(arr))`. Alternatively use Python's built-in: `return max(arr)` which handles all edge cases automatically."
    }
  ],
  testCases: [
    { id: 1, input: "[1, 2, 3, 10]",  expected: "10", actual: "3",  passed: false },
    { id: 2, input: "[5, 3, 8, 1]",   expected: "8",  actual: "3",  passed: false },
    { id: 3, input: "[7]",            expected: "7",  actual: "7",  passed: true  },
    { id: 4, input: "[-2, -1, -5]",   expected: "-1", actual: "-1", passed: true  }
  ]
}

// ─── Scenario 3: Infinite / wrong recursion ─────────────────────────────────
export const scenario_recursion = {
  id: 'recursion',
  status: "bugs_found",
  executionOutput: "RecursionError: maximum recursion depth exceeded",
  errorLine: 5,
  bugSummary: "Missing or incorrect base case causes infinite recursion",
  hints: [
    {
      level: 1, title: "Directional nudge", icon: "💡",
      text: "Your recursive function never terminates. Every recursive function needs a **base case** — a condition where it stops calling itself."
    },
    {
      level: 2, title: "More specific", icon: "💡",
      text: "The recursive call `factorial(n)` calls itself with the **same argument** `n` instead of `n - 1`. This means it never makes progress toward the base case."
    },
    {
      level: 3, title: "Full solution", icon: "🔓",
      text: "Fix the recursive call: `return n * factorial(n - 1)`. Also ensure `if n <= 1: return 1` is your base case to handle both `0` and `1` inputs."
    }
  ],
  testCases: [
    { id: 1, input: "n = 5",    expected: "120",   actual: "ERROR", passed: false },
    { id: 2, input: "n = 0",    expected: "1",     actual: "ERROR", passed: false },
    { id: 3, input: "n = 1",    expected: "1",     actual: "ERROR", passed: false },
    { id: 4, input: "n = 3",    expected: "6",     actual: "ERROR", passed: false }
  ]
}

// ─── Scenario 4: Wrong sort / comparison operator ───────────────────────────
export const scenario_sortBug = {
  id: 'sort_bug',
  status: "bugs_found",
  executionOutput: "Wrong answer — list not sorted correctly",
  errorLine: 4,
  bugSummary: "Incorrect comparison produces reverse or unstable sort",
  hints: [
    {
      level: 1, title: "Directional nudge", icon: "💡",
      text: "Your sorting function returns results in the **wrong order** for some inputs. Double-check the comparison logic inside your swap condition."
    },
    {
      level: 2, title: "More specific", icon: "💡",
      text: "The condition `arr[j] < arr[j+1]` swaps when the left element is **smaller** — this sorts in descending order. For ascending sort, swap when the left element is **greater**."
    },
    {
      level: 3, title: "Full solution", icon: "🔓",
      text: "Change the comparison to `arr[j] > arr[j+1]` to get ascending order. Your bubble sort logic is otherwise correct — the issue is purely the comparison operator."
    }
  ],
  testCases: [
    { id: 1, input: "[3,1,4,1,5]",  expected: "[1,1,3,4,5]", actual: "[5,4,3,1,1]", passed: false },
    { id: 2, input: "[9,2,6]",      expected: "[2,6,9]",      actual: "[9,6,2]",     passed: false },
    { id: 3, input: "[1,2,3]",      expected: "[1,2,3]",      actual: "[3,2,1]",     passed: false },
    { id: 4, input: "[5]",          expected: "[5]",           actual: "[5]",         passed: true  }
  ]
}

// ─── Scenario 5: Clean code — no bugs ───────────────────────────────────────
export const scenario_noBugs = {
  id: 'no_bugs',
  status: "clean",
  executionOutput: "All tests passed",
  errorLine: null,
  bugSummary: "No bugs detected — all test cases pass",
  hints: [
    {
      level: 1, title: "Code quality tip", icon: "✨",
      text: "Your code is logically correct! Consider adding a **docstring** to document the expected input type, return value, and any constraints."
    },
    {
      level: 2, title: "Performance insight", icon: "💡",
      text: "Your current solution runs in **O(n)** time, which is optimal for this problem. If you used sorting to find the max, that would be O(n log n) — unnecessary here."
    },
    {
      level: 3, title: "Pythonic refactor", icon: "🔓",
      text: "Python has a built-in `max()` function: `return max(arr) if arr else None`. This is more readable, handles edge cases, and uses optimized C-level iteration."
    }
  ],
  testCases: [
    { id: 1, input: "[3,1,4,1,5]", expected: "5",    actual: "5",    passed: true },
    { id: 2, input: "[]",          expected: "None",  actual: "None", passed: true },
    { id: 3, input: "[-1,-5,-2]",  expected: "-1",   actual: "-1",   passed: true },
    { id: 4, input: "[1]",         expected: "1",     actual: "1",    passed: true }
  ]
}



// ─── Pattern detector ────────────────────────────────────────────────────────
export function detectScenario(code) {
  const c = code.toLowerCase()

  if (
    (c.includes('factorial') || c.includes('fibonacci') || c.includes('fib(')) &&
    (c.includes('factorial(n)') || c.includes('fib(n)') || (c.includes('return n *') && !c.includes('n - 1') && !c.includes('n-1')))
  ) {
    return scenario_recursion
  }

  if (
    (c.includes('bubble') || c.includes('sort') || (c.includes('arr[j]') && c.includes('arr[j+1]'))) &&
    (c.includes('arr[j] < arr[j+1]') || c.includes('a[j] < a[j+1]') || c.includes('arr[j]<arr[j+1]'))
  ) {
    return scenario_sortBug
  }

  if (
    c.includes('len(arr) - 1') || c.includes('len(arr)-1') ||
    c.includes('.length - 1') || c.includes('.length-1') ||
    c.includes('arr.size() - 1') || c.includes('arr.size()-1')
  ) {
    return scenario_offByOne
  }

  if (
    c.includes('if not arr') ||
    c.includes('if (arr.length === 0)') ||
    c.includes('if (arr == null || arr.length == 0)') ||
    c.includes('arr.isempty') ||
    c.includes('if arr.size() == 0') ||
    c.includes('return none') ||
    c.includes('return null') ||
    (c.includes('if') && c.includes('arr') && c.includes('empty'))
  ) {
    return scenario_noBugs
  }

  return scenario_emptyArray
}

// ─── Multi-mode starter code ─────────────────────────────────────────────────
// Each language has:
//   focused  → just the core function (LeetCode style)
//   template → full boilerplate with {{USER_CODE}} placeholder
export const starterCode = {
  python: {
    focused: `def find_max(arr):
    max_val = arr[0]
    for i in range(len(arr)):
        if arr[i] > max_val:
            max_val = arr[i]
    return max_val`,

    template: `{{USER_CODE}}

# ── Test Runner ────────────────────────────────
if __name__ == "__main__":
    print(find_max([3, 1, 4, 1, 5, 9]))   # → 9
    print(find_max([]))                    # → None (edge case)
    print(find_max([-1, -5, -2]))          # → -1`
  },

  cpp: {
    focused: `int findMax(vector<int>& arr) {
    int maxVal = arr[0];
    for (int i = 0; i < arr.size(); i++) {
        if (arr[i] > maxVal)
            maxVal = arr[i];
    }
    return maxVal;
}`,

    template: `#include <iostream>
#include <vector>
#include <climits>
using namespace std;

{{USER_CODE}}

int main() {
    // Test cases
    vector<int> arr1 = {3, 1, 4, 1, 5, 9};
    cout << "Test 1: " << findMax(arr1) << endl;  // → 9

    vector<int> arr2 = {-1, -5, -2};
    cout << "Test 2: " << findMax(arr2) << endl;  // → -1

    return 0;
}`
  },

  java: {
    focused: `public static int findMax(int[] arr) {
    int maxVal = arr[0];
    for (int i = 0; i < arr.length; i++) {
        if (arr[i] > maxVal)
            maxVal = arr[i];
    }
    return maxVal;
}`,

    template: `import java.util.Arrays;

public class Solution {

    {{USER_CODE}}

    public static void main(String[] args) {
        // Test cases
        int[] arr1 = {3, 1, 4, 1, 5, 9};
        System.out.println("Test 1: " + findMax(arr1));  // → 9

        int[] arr2 = {-1, -5, -2};
        System.out.println("Test 2: " + findMax(arr2));  // → -1
    }
}`
  },

  javascript: {
    focused: `function findMax(arr) {
    let maxVal = arr[0];
    for (let i = 0; i < arr.length; i++) {
        if (arr[i] > maxVal) {
            maxVal = arr[i];
        }
    }
    return maxVal;
}`,

    template: `{{USER_CODE}}

// ── Test Runner ────────────────────────────────
console.log("Test 1:", findMax([3, 1, 4, 1, 5, 9]));  // → 9
console.log("Test 2:", findMax([]));                   // → undefined (edge case)
console.log("Test 3:", findMax([-1, -5, -2]));         // → -1`
  }
}

// ─── Helper: wrap focused code in boilerplate ────────────────────────────────
export function wrapInBoilerplate(userCode, language) {
  const lang = starterCode[language]
  if (!lang?.template) return userCode
  // For Java, indent the user code to fit inside the class
  const indented = language === 'java'
    ? userCode.split('\n').map(l => l ? `    ${l}` : l).join('\n')
    : userCode
  return lang.template.replace('{{USER_CODE}}', indented)
}

// ─── Helper: get display code for Monaco ────────────────────────────────────
export function getDisplayCode(language, mode, userCode) {
  if (mode === 'focused') return userCode
  return wrapInBoilerplate(userCode, language)
}

// ─── Language config ─────────────────────────────────────────────────────────
export const languageConfig = {
  python:     { label: "Python",     version: "3.11",   icon: "Py",  monacoLang: "python",     color: "#4B8BBE" },
  cpp:        { label: "C++",        version: "17",     icon: "C++", monacoLang: "cpp",        color: "#659BD3" },
  java:       { label: "Java",       version: "17",     icon: "Jv",  monacoLang: "java",       color: "#ED8B00" },
  javascript: { label: "JavaScript", version: "ES2023", icon: "JS",  monacoLang: "javascript", color: "#F7DF1E" }
}

// Legacy export
export const mockAnalysisResult = scenario_emptyArray

// ─── Run output fallback map (used when backend is offline) ──────────────────
// Shape: { scenario_id: { language: { success, output, execTime } } }
export const runOutputMap = {
  empty_array: {
    python:     { success: false, output: 'Traceback (most recent call last):\n  File "<string>", line 2, in find_max\nIndexError: list index out of range', execTime: '0.012s' },
    cpp:        { success: false, output: 'Runtime error: vector::_M_range_check: __n (which is 0) >= this->size() (which is 0)', execTime: '—' },
    java:       { success: false, output: 'Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: Index 0 out of bounds for length 0', execTime: '—' },
    javascript: { success: false, output: 'TypeError: Cannot read properties of undefined (reading undefined)\n    at findMax (<anonymous>:2:18)', execTime: '—' },
  },
  off_by_one: {
    python:     { success: true,  output: '>>> find_max([1,2,3,10]) → 3  ✗ (expected 10)\n>>> find_max([5,3,8,1])  → 5  ✗ (expected 8)', execTime: '0.008s' },
    cpp:        { success: true,  output: 'Output: 3 (expected: 10) — off-by-one in loop bound', execTime: '—' },
    java:       { success: true,  output: 'Result: 3 (expected 10) — loop terminates one iteration early', execTime: '—' },
    javascript: { success: true,  output: 'Output: 3 (expected: 10) — array.length - 1 skips last element', execTime: '—' },
  },
  recursion: {
    python:     { success: false, output: 'Traceback (most recent call last):\n  ...\nRecursionError: maximum recursion depth exceeded', execTime: '2.341s' },
    cpp:        { success: false, output: 'Segmentation fault (core dumped) — stack overflow from infinite recursion', execTime: '—' },
    java:       { success: false, output: 'Exception in thread "main" java.lang.StackOverflowError', execTime: '—' },
    javascript: { success: false, output: 'RangeError: Maximum call stack size exceeded', execTime: '—' },
  },
  sort_bug: {
    python:     { success: true,  output: '>>> bubble_sort([3,1,4,1,5]) → [5,4,3,1,1]  ✗\n(sorted descending instead of ascending)', execTime: '0.015s' },
    cpp:        { success: true,  output: 'Output: [5, 4, 3, 1, 1] (expected ascending order)', execTime: '—' },
    java:       { success: true,  output: 'Sorted: [5, 4, 3, 1, 1] — comparison operator reversed', execTime: '—' },
    javascript: { success: true,  output: '[5,4,3,1,1] — sorts descending due to wrong comparison', execTime: '—' },
  },
  clean: {
    python:     { success: true,  output: '>>> find_max([3,1,4,1,5]) → 5  ✓\n>>> find_max([])          → None  ✓\n>>> find_max([-1,-5,-2])  → -1  ✓', execTime: '0.007s' },
    cpp:        { success: true,  output: 'All test cases passed. Output: 5, -1, 1', execTime: '—' },
    java:       { success: true,  output: 'Tests passed: 4/4. Results: 5, null, -1, 1', execTime: '—' },
    javascript: { success: true,  output: 'All assertions passed. find_max([3,1,4,1,5]) === 5 ✓', execTime: '—' },
  },
}

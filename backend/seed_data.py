"""
Seed curated DSA patterns, problems, and official test cases.

Run:
    cd backend
    python seed_data.py

This script is idempotent for patterns/problems and replaces each problem's
test-case set with the curated visible/hidden cases defined below.
"""
from __future__ import annotations

import sys
from typing import Dict, List

sys.path.insert(0, ".")


LANGUAGES = ("python", "javascript", "java", "cpp")


PROBLEM_SIGNATURES = {
    "two-sum": {"params": [("nums", "int_array"), ("target", "int")], "return_type": "int_array"},
    "best-time-to-buy-and-sell-stock": {"params": [("prices", "int_array")], "return_type": "int"},
    "move-zeroes": {"params": [("nums", "int_array")], "return_type": "int_array"},
    "product-of-array-except-self": {"params": [("nums", "int_array")], "return_type": "int_array"},
    "valid-palindrome": {"params": [("s", "string")], "return_type": "bool"},
    "two-sum-ii-sorted": {"params": [("numbers", "int_array"), ("target", "int")], "return_type": "int_array"},
    "longest-substring-without-repeating": {"params": [("s", "string")], "return_type": "int"},
    "maximum-average-subarray": {"params": [("nums", "int_array"), ("k", "int")], "return_type": "float"},
    "binary-search": {"params": [("nums", "int_array"), ("target", "int")], "return_type": "int"},
    "search-insert-position": {"params": [("nums", "int_array"), ("target", "int")], "return_type": "int"},
    "reverse-string": {"params": [("s", "string")], "return_type": "string"},
    "valid-anagram": {"params": [("s", "string"), ("t", "string")], "return_type": "bool"},
    "climbing-stairs": {"params": [("n", "int")], "return_type": "int"},
    "maximum-subarray": {"params": [("nums", "int_array")], "return_type": "int"},
    "container-with-most-water": {"params": [("height", "int_array")], "return_type": "int"},
}

JAVA_TYPE_MAP = {
    "int": "int",
    "float": "double",
    "bool": "boolean",
    "string": "String",
    "int_array": "int[]",
}

CPP_TYPE_MAP = {
    "int": "int",
    "float": "double",
    "bool": "bool",
    "string": "string",
    "int_array": "vector<int>",
}


def _python_input_expr(index: int, param_type: str) -> str:
    value = f"values[{index}] if len(values) > {index} else {_python_default(param_type)}"
    if param_type == "int":
        return f"int({value})"
    if param_type == "float":
        return f"float({value})"
    if param_type == "bool":
        return f"bool({value})"
    return value


def _python_default(value_type: str) -> str:
    return {
        "int": "0",
        "float": "0.0",
        "bool": "False",
        "string": '""',
        "int_array": "[]",
    }[value_type]


def _javascript_default(value_type: str) -> str:
    return {
        "int": "0",
        "float": "0",
        "bool": "false",
        "string": "''",
        "int_array": "[]",
    }[value_type]


def _javascript_format(value_type: str) -> str:
    return "JSON.stringify(answer)" if value_type in {"int_array", "bool"} else "answer"


def _java_default_value(value_type: str) -> str:
    return {
        "int": "0",
        "float": "0.0",
        "bool": "false",
        "string": '""',
        "int_array": "new int[0]",
    }[value_type]


def _cpp_default_value(value_type: str) -> str:
    return {
        "int": "0",
        "float": "0.0",
        "bool": "false",
        "string": '""',
        "int_array": "{}",
    }[value_type]


def program_starter(problem_slug: str, language: str) -> str:
    signature = PROBLEM_SIGNATURES[problem_slug]
    params = signature["params"]
    return_type = signature["return_type"]

    if language == "python":
        assignments = "\n".join(
            f"    {name} = {_python_input_expr(index, param_type)}"
            for index, (name, param_type) in enumerate(params)
        )
        return f"""import ast
import sys


def parse_value(raw):
    try:
        return ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        return raw


def main():
    values = [parse_value(line) for line in sys.stdin.read().splitlines()]
{assignments}

    # Write your solution here.
    answer = {_python_default(return_type)}
    print(answer)


if __name__ == "__main__":
    main()
"""

    if language == "javascript":
        assignments = "\n".join(
            f"  const {name} = input.length > {index} ? parseValue(input[{index}]) : {_javascript_default(param_type)};"
            for index, (name, param_type) in enumerate(params)
        )
        return f"""const fs = require('fs');
const input = fs.readFileSync(0, 'utf8').replace(/\\r/g, '').split('\\n');

function parseValue(value) {{
  try {{
    return JSON.parse(value);
  }} catch {{
    const numeric = Number(value);
    return Number.isNaN(numeric) ? value : numeric;
  }}
}}

function main() {{
{assignments}

  // Write your solution here.
  const answer = {_javascript_default(return_type)};
  console.log({_javascript_format(return_type)});
}}

main();
"""

    if language == "java":
        java_assignments = "\n".join(
            f"        {JAVA_TYPE_MAP[param_type]} {param_name} = {_java_parse_expr(index, param_type)};"
            for index, (param_name, param_type) in enumerate(params)
        )
        java_return_type = JAVA_TYPE_MAP[return_type]
        return f"""import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

public class Main {{
    private static int[] parseIntArray(String raw) {{
        String cleaned = raw.trim();
        if (cleaned.length() <= 2) return new int[0];
        cleaned = cleaned.substring(1, cleaned.length() - 1);
        String[] parts = cleaned.split(",");
        int[] nums = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {{
            nums[i] = Integer.parseInt(parts[i].trim());
        }}
        return nums;
    }}

    private static String parseString(String raw) {{
        String cleaned = raw.trim();
        if (cleaned.length() >= 2 && cleaned.startsWith("\"") && cleaned.endsWith("\"")) {{
            return cleaned.substring(1, cleaned.length() - 1);
        }}
        return cleaned;
    }}

    private static boolean parseBool(String raw) {{
        return raw.trim().equalsIgnoreCase("true");
    }}

    private static String formatIntArray(int[] nums) {{
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < nums.length; i++) {{
            if (i > 0) sb.append(", ");
            sb.append(nums[i]);
        }}
        sb.append("]");
        return sb.toString();
    }}

    private static String formatResult({java_return_type} result) {{
{_java_format_result(return_type)}
    }}

    public static void main(String[] args) throws Exception {{
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        List<String> input = new ArrayList<>();
        String line;
        while ((line = br.readLine()) != null) {{
            input.add(line);
        }}
{java_assignments}

        // Write your solution here.
        {java_return_type} answer = {_java_default_value(return_type)};
        System.out.println(formatResult(answer));
    }}
}}
"""

    cpp_assignments = "\n".join(
        f"    {CPP_TYPE_MAP[param_type]} {param_name} = {_cpp_parse_expr(index, param_type)};"
        for index, (param_name, param_type) in enumerate(params)
    )
    cpp_return_type = CPP_TYPE_MAP[return_type]
    return f"""#include <bits/stdc++.h>
using namespace std;

vector<int> parseIntVector(string raw) {{
    vector<int> result;
    raw.erase(remove_if(raw.begin(), raw.end(), ::isspace), raw.end());
    if (raw.size() <= 2) return result;
    raw = raw.substr(1, raw.size() - 2);
    string token;
    stringstream ss(raw);
    while (getline(ss, token, ',')) {{
        if (!token.empty()) result.push_back(stoi(token));
    }}
    return result;
}}

string parseString(string raw) {{
    if (raw.size() >= 2 && raw.front() == '"' && raw.back() == '"') {{
        return raw.substr(1, raw.size() - 2);
    }}
    return raw;
}}

bool parseBool(string raw) {{
    transform(raw.begin(), raw.end(), raw.begin(), ::tolower);
    return raw == "true";
}}

string formatIntVector(const vector<int>& nums) {{
    stringstream out;
    out << "[";
    for (size_t i = 0; i < nums.size(); i++) {{
        if (i > 0) out << ", ";
        out << nums[i];
    }}
    out << "]";
    return out.str();
}}

string formatResult({cpp_return_type} result) {{
{_cpp_format_result(return_type)}
}}

int main() {{
    vector<string> input;
    string line;
    while (getline(cin, line)) {{
        input.push_back(line);
    }}

{cpp_assignments}

    // Write your solution here.
    {cpp_return_type} answer = {_cpp_default_value(return_type)};
    cout << formatResult(answer) << endl;
    return 0;
}}
"""


def _java_parse_expr(index: int, param_type: str) -> str:
    raw = f'input.size() > {index} ? input.get({index}) : ""'
    if param_type == "int":
        return f"Integer.parseInt({raw}.trim())"
    if param_type == "float":
        return f"Double.parseDouble({raw}.trim())"
    if param_type == "bool":
        return f"parseBool({raw})"
    if param_type == "int_array":
        return f"parseIntArray({raw})"
    return f"parseString({raw})"


def _java_format_result(return_type: str) -> str:
    formatters = {
        "int": "        return String.valueOf(result);",
        "float": "        return String.valueOf(result);",
        "bool": '        return result ? "true" : "false";',
        "string": "        return result;",
        "int_array": "        return formatIntArray(result);",
    }
    return formatters[return_type]


def _cpp_parse_expr(index: int, param_type: str) -> str:
    raw = f'(input.size() > {index} ? input[{index}] : string())'
    if param_type == "int":
        return f"stoi({raw})"
    if param_type == "float":
        return f"stod({raw})"
    if param_type == "bool":
        return f"parseBool({raw})"
    if param_type == "int_array":
        return f"parseIntVector({raw})"
    return f"parseString({raw})"


def _cpp_format_result(return_type: str) -> str:
    formatters = {
        "int": "    return to_string(result);",
        "float": '    ostringstream out; out << result; return out.str();',
        "bool": '    return result ? "true" : "false";',
        "string": "    return result;",
        "int_array": "    return formatIntVector(result);",
    }
    return formatters[return_type]


def program_starters(problem_slug: str) -> Dict[str, str]:
    return {language: program_starter(problem_slug, language) for language in LANGUAGES}


INPUT_TYPE_LABELS = {
    "int": "an integer",
    "float": "a number",
    "bool": "true or false",
    "string": "a string without surrounding quotes",
    "int_array": "a JSON-style integer array, for example [1, 2, 3]",
}

OUTPUT_TYPE_LABELS = {
    "int": "Print one integer.",
    "float": "Print one number. Answers within 1e-6 are accepted.",
    "bool": "Print true or false.",
    "string": "Print the resulting string.",
    "int_array": "Print the resulting indices or values as an array, for example [0, 1].",
}


def problem_input_format(problem_slug: str) -> str:
    params = PROBLEM_SIGNATURES[problem_slug]["params"]
    return "\n".join(
        f"Line {index}: {name} - {INPUT_TYPE_LABELS[param_type]}."
        for index, (name, param_type) in enumerate(params, start=1)
    )


def problem_output_format(problem_slug: str) -> str:
    return OUTPUT_TYPE_LABELS[PROBLEM_SIGNATURES[problem_slug]["return_type"]]


PATTERNS = [
    {
        "name": "Arrays",
        "slug": "arrays",
        "description": "Array traversal, prefix products, and index-based reasoning.",
        "icon_name": "AR",
        "order_index": 1,
    },
    {
        "name": "Two Pointers",
        "slug": "two-pointers",
        "description": "Use left/right pointers to scan or shrink the search space.",
        "icon_name": "TP",
        "order_index": 2,
    },
    {
        "name": "Sliding Window",
        "slug": "sliding-window",
        "description": "Maintain a moving window for substring and subarray problems.",
        "icon_name": "SW",
        "order_index": 3,
    },
    {
        "name": "Binary Search",
        "slug": "binary-search",
        "description": "Exploit sorted order to cut the search space in half.",
        "icon_name": "BS",
        "order_index": 4,
    },
    {
        "name": "Strings",
        "slug": "strings",
        "description": "String validation, transformations, and frequency checks.",
        "icon_name": "ST",
        "order_index": 5,
    },
    {
        "name": "Recursion & DP",
        "slug": "recursion-dp",
        "description": "Recursive thinking, transitions, and dynamic programming.",
        "icon_name": "DP",
        "order_index": 6,
    },
]


PROBLEMS = [
    {
        "pattern_slug": "arrays",
        "title": "Two Sum",
        "slug": "two-sum",
        "difficulty": "easy",
        "short_description": "Return the indices of the two numbers that add up to the target.",
        "statement": "Given an array of integers nums and an integer target, return the indices of the two numbers such that they add up to target. Assume exactly one valid answer exists, and do not use the same element twice.",
        "constraints_text": "2 <= nums.length <= 10^4, -10^9 <= nums[i] <= 10^9, exactly one valid answer exists.",
        "examples_json": [
            {"input": "nums = [2, 7, 11, 15], target = 9", "output": "[0, 1]", "explanation": "nums[0] + nums[1] equals 9."},
            {"input": "nums = [3, 2, 4], target = 6", "output": "[1, 2]", "explanation": "2 + 4 equals 6."},
        ],
        "starter_code_json": program_starters("two-sum"),
        "test_cases": [
            {"label": "Example 1", "input": "[2, 7, 11, 15]\n9", "expected_output": "[0, 1]", "is_hidden": False},
            {"label": "Example 2", "input": "[3, 2, 4]\n6", "expected_output": "[1, 2]", "is_hidden": False},
            {"label": "Duplicate values", "input": "[3, 3]\n6", "expected_output": "[0, 1]", "is_hidden": True},
            {"label": "Negative values", "input": "[-3, 4, 3, 90]\n0", "expected_output": "[0, 2]", "is_hidden": True},
        ],
    },
    {
        "pattern_slug": "arrays",
        "title": "Best Time to Buy and Sell Stock",
        "slug": "best-time-to-buy-and-sell-stock",
        "difficulty": "easy",
        "short_description": "Track the best profit from one buy and one sell.",
        "statement": "You are given an array where prices[i] is the price of a stock on day i. Choose one day to buy and a later day to sell. Return the maximum profit you can achieve. If no profit is possible, return 0.",
        "constraints_text": "1 <= prices.length <= 10^5, 0 <= prices[i] <= 10^4.",
        "examples_json": [
            {"input": "prices = [7, 1, 5, 3, 6, 4]", "output": "5", "explanation": "Buy at 1 and sell at 6."},
            {"input": "prices = [7, 6, 4, 3, 1]", "output": "0", "explanation": "No profitable transaction exists."},
        ],
        "starter_code_json": program_starters("best-time-to-buy-and-sell-stock"),
        "test_cases": [
            {"label": "Rising after dip", "input": "[7, 1, 5, 3, 6, 4]", "expected_output": "5", "is_hidden": False},
            {"label": "Always falling", "input": "[7, 6, 4, 3, 1]", "expected_output": "0", "is_hidden": False},
            {"label": "Single day", "input": "[5]", "expected_output": "0", "is_hidden": True},
            {"label": "Late profit", "input": "[2, 4, 1]", "expected_output": "2", "is_hidden": True},
        ],
    },
    {
        "pattern_slug": "arrays",
        "title": "Move Zeroes",
        "slug": "move-zeroes",
        "difficulty": "easy",
        "short_description": "Move all zeroes to the end while keeping non-zero order.",
        "statement": "Given an integer array nums, move all zeroes to the end of it while keeping the relative order of the non-zero elements.",
        "constraints_text": "1 <= nums.length <= 10^4, -2^31 <= nums[i] <= 2^31 - 1.",
        "examples_json": [
            {"input": "nums = [0, 1, 0, 3, 12]", "output": "[1, 3, 12, 0, 0]", "explanation": "Non-zero values stay in order and zeroes shift right."},
            {"input": "nums = [0]", "output": "[0]", "explanation": "A single zero stays where it is."},
        ],
        "starter_code_json": program_starters("move-zeroes"),
        "test_cases": [
            {"label": "Classic example", "input": "[0, 1, 0, 3, 12]", "expected_output": "[1, 3, 12, 0, 0]", "is_hidden": False},
            {"label": "Already packed", "input": "[4, 1, 2]", "expected_output": "[4, 1, 2]", "is_hidden": False},
            {"label": "Only zeroes", "input": "[0, 0, 0]", "expected_output": "[0, 0, 0]", "is_hidden": True},
            {"label": "Zero in middle", "input": "[1, 0, 2, 0, 3]", "expected_output": "[1, 2, 3, 0, 0]", "is_hidden": True},
        ],
    },
    {
        "pattern_slug": "arrays",
        "title": "Product of Array Except Self",
        "slug": "product-of-array-except-self",
        "difficulty": "medium",
        "short_description": "Build the product of all numbers except the current index.",
        "statement": "Given an integer array nums, return an array answer such that answer[i] is the product of all the elements of nums except nums[i]. Do not use division.",
        "constraints_text": "2 <= nums.length <= 10^5, -30 <= nums[i] <= 30. The product of any prefix or suffix fits in a 32-bit integer.",
        "examples_json": [
            {"input": "nums = [1, 2, 3, 4]", "output": "[24, 12, 8, 6]", "explanation": "Each slot is the product of the other three values."},
            {"input": "nums = [-1, 1, 0, -3, 3]", "output": "[0, 0, 9, 0, 0]", "explanation": "The zero forces all other positions to zero except the zero index itself."},
        ],
        "starter_code_json": program_starters("product-of-array-except-self"),
        "test_cases": [
            {"label": "Simple positives", "input": "[1, 2, 3, 4]", "expected_output": "[24, 12, 8, 6]", "is_hidden": False},
            {"label": "Contains zero", "input": "[-1, 1, 0, -3, 3]", "expected_output": "[0, 0, 9, 0, 0]", "is_hidden": False},
            {"label": "Two elements", "input": "[5, 2]", "expected_output": "[2, 5]", "is_hidden": True},
            {"label": "Two zeroes", "input": "[0, 4, 0]", "expected_output": "[0, 0, 0]", "is_hidden": True},
        ],
    },
    {
        "pattern_slug": "two-pointers",
        "title": "Valid Palindrome",
        "slug": "valid-palindrome",
        "difficulty": "easy",
        "short_description": "Ignore punctuation and case, then check whether the string reads the same both ways.",
        "statement": "Given a string s, return true if it is a palindrome after converting uppercase letters to lowercase and removing all non-alphanumeric characters.",
        "constraints_text": "1 <= s.length <= 2 * 10^5, s contains printable ASCII characters.",
        "examples_json": [
            {"input": "s = \"A man, a plan, a canal: Panama\"", "output": "True", "explanation": "Ignoring punctuation gives 'amanaplanacanalpanama'."},
            {"input": "s = \"race a car\"", "output": "False", "explanation": "The cleaned string is not symmetric."},
        ],
        "starter_code_json": program_starters("valid-palindrome"),
        "test_cases": [
            {"label": "Classic palindrome", "input": "A man, a plan, a canal: Panama", "expected_output": "True", "is_hidden": False},
            {"label": "Not a palindrome", "input": "race a car", "expected_output": "False", "is_hidden": False},
            {"label": "Numbers and letters", "input": "0P", "expected_output": "False", "is_hidden": True},
            {"label": "Only punctuation", "input": ".,", "expected_output": "True", "is_hidden": True},
        ],
    },
    {
        "pattern_slug": "two-pointers",
        "title": "Two Sum II (Sorted)",
        "slug": "two-sum-ii-sorted",
        "difficulty": "medium",
        "short_description": "Find the two 1-indexed positions in a sorted array that add up to target.",
        "statement": "Given a 1-indexed array of integers numbers that is already sorted in non-decreasing order, return the indices of the two numbers such that they add up to target.",
        "constraints_text": "2 <= numbers.length <= 3 * 10^4, -1000 <= numbers[i] <= 1000, exactly one solution exists.",
        "examples_json": [
            {"input": "numbers = [2, 7, 11, 15], target = 9", "output": "[1, 2]", "explanation": "The first two numbers sum to 9."},
            {"input": "numbers = [2, 3, 4], target = 6", "output": "[1, 3]", "explanation": "2 + 4 equals 6."},
        ],
        "starter_code_json": program_starters("two-sum-ii-sorted"),
        "test_cases": [
            {"label": "Example 1", "input": "[2, 7, 11, 15]\n9", "expected_output": "[1, 2]", "is_hidden": False},
            {"label": "Example 2", "input": "[2, 3, 4]\n6", "expected_output": "[1, 3]", "is_hidden": False},
            {"label": "Negative pair", "input": "[-1, 0]\n-1", "expected_output": "[1, 2]", "is_hidden": True},
            {"label": "Wide spacing", "input": "[1, 2, 3, 4, 4, 9, 56, 90]\n8", "expected_output": "[4, 5]", "is_hidden": True},
        ],
    },
    {
        "pattern_slug": "sliding-window",
        "title": "Longest Substring Without Repeating",
        "slug": "longest-substring-without-repeating",
        "difficulty": "medium",
        "short_description": "Track the longest window with all unique characters.",
        "statement": "Given a string s, find the length of the longest substring without repeating characters.",
        "constraints_text": "0 <= s.length <= 5 * 10^4, s consists of English letters, digits, symbols, and spaces.",
        "examples_json": [
            {"input": "s = \"abcabcbb\"", "output": "3", "explanation": "The answer is 'abc'."},
            {"input": "s = \"bbbbb\"", "output": "1", "explanation": "Only one unique character can stay in the window."},
        ],
        "starter_code_json": program_starters("longest-substring-without-repeating"),
        "test_cases": [
            {"label": "Repeating pattern", "input": "abcabcbb", "expected_output": "3", "is_hidden": False},
            {"label": "Single repeat", "input": "bbbbb", "expected_output": "1", "is_hidden": False},
            {"label": "Mixed overlap", "input": "pwwkew", "expected_output": "3", "is_hidden": True},
            {"label": "Empty string", "input": "", "expected_output": "0", "is_hidden": True},
        ],
    },
    {
        "pattern_slug": "sliding-window",
        "title": "Maximum Average Subarray",
        "slug": "maximum-average-subarray",
        "difficulty": "easy",
        "short_description": "Find the maximum average of any contiguous subarray of length k.",
        "statement": "Given an integer array nums and an integer k, return the maximum average value of a contiguous subarray of length k.",
        "constraints_text": "1 <= k <= nums.length <= 10^5, -10^4 <= nums[i] <= 10^4.",
        "examples_json": [
            {"input": "nums = [1, 12, -5, -6, 50, 3], k = 4", "output": "12.75", "explanation": "The subarray [12, -5, -6, 50] has the best average."},
            {"input": "nums = [5], k = 1", "output": "5.0", "explanation": "Only one window exists."},
        ],
        "starter_code_json": program_starters("maximum-average-subarray"),
        "test_cases": [
            {"label": "Classic example", "input": "[1, 12, -5, -6, 50, 3]\n4", "expected_output": "12.75", "is_hidden": False},
            {"label": "Single value", "input": "[5]\n1", "expected_output": "5.0", "is_hidden": False},
            {"label": "All negatives", "input": "[-1, -12, -5, -6, -50, -3]\n2", "expected_output": "-5.5", "is_hidden": True},
            {"label": "Window at end", "input": "[0, 4, 0, 3, 2]\n1", "expected_output": "4.0", "is_hidden": True},
        ],
    },
    {
        "pattern_slug": "binary-search",
        "title": "Binary Search",
        "slug": "binary-search",
        "difficulty": "easy",
        "short_description": "Return the index of target in a sorted array, or -1 if absent.",
        "statement": "Given a sorted array of integers nums and an integer target, return the index of target if it exists. Otherwise return -1.",
        "constraints_text": "1 <= nums.length <= 10^4, nums is sorted in ascending order.",
        "examples_json": [
            {"input": "nums = [-1, 0, 3, 5, 9, 12], target = 9", "output": "4", "explanation": "9 is at index 4."},
            {"input": "nums = [-1, 0, 3, 5, 9, 12], target = 2", "output": "-1", "explanation": "2 is not present."},
        ],
        "starter_code_json": program_starters("binary-search"),
        "test_cases": [
            {"label": "Target present", "input": "[-1, 0, 3, 5, 9, 12]\n9", "expected_output": "4", "is_hidden": False},
            {"label": "Target absent", "input": "[-1, 0, 3, 5, 9, 12]\n2", "expected_output": "-1", "is_hidden": False},
            {"label": "Single element hit", "input": "[5]\n5", "expected_output": "0", "is_hidden": True},
            {"label": "Single element miss", "input": "[5]\n-5", "expected_output": "-1", "is_hidden": True},
        ],
    },
    {
        "pattern_slug": "binary-search",
        "title": "Search Insert Position",
        "slug": "search-insert-position",
        "difficulty": "easy",
        "short_description": "Find the index where target should be inserted in sorted order.",
        "statement": "Given a sorted array of distinct integers and a target value, return the index if the target is found. If not, return the index where it would be inserted to keep the array sorted.",
        "constraints_text": "1 <= nums.length <= 10^4, nums contains distinct values sorted in ascending order.",
        "examples_json": [
            {"input": "nums = [1, 3, 5, 6], target = 5", "output": "2", "explanation": "5 already exists at index 2."},
            {"input": "nums = [1, 3, 5, 6], target = 2", "output": "1", "explanation": "2 should be inserted between 1 and 3."},
        ],
        "starter_code_json": program_starters("search-insert-position"),
        "test_cases": [
            {"label": "Already present", "input": "[1, 3, 5, 6]\n5", "expected_output": "2", "is_hidden": False},
            {"label": "Insert in middle", "input": "[1, 3, 5, 6]\n2", "expected_output": "1", "is_hidden": False},
            {"label": "Insert at end", "input": "[1, 3, 5, 6]\n7", "expected_output": "4", "is_hidden": True},
            {"label": "Insert at start", "input": "[1, 3, 5, 6]\n0", "expected_output": "0", "is_hidden": True},
        ],
    },
    {
        "pattern_slug": "strings",
        "title": "Reverse String",
        "slug": "reverse-string",
        "difficulty": "easy",
        "short_description": "Reverse the characters in the input string.",
        "statement": "Given a string, return the reversed string.",
        "constraints_text": "1 <= s.length <= 10^5.",
        "examples_json": [
            {"input": "s = \"hello\"", "output": "olleh", "explanation": "The characters are reversed."},
            {"input": "s = \"DebugMentor\"", "output": "rotneMgubeD", "explanation": "Case is preserved while order reverses."},
        ],
        "starter_code_json": program_starters("reverse-string"),
        "test_cases": [
            {"label": "Simple word", "input": "hello", "expected_output": "olleh", "is_hidden": False},
            {"label": "With spaces", "input": "data structures", "expected_output": "serutcurts atad", "is_hidden": False},
            {"label": "Single char", "input": "a", "expected_output": "a", "is_hidden": True},
            {"label": "Mixed case", "input": "AbCd", "expected_output": "dCbA", "is_hidden": True},
        ],
    },
    {
        "pattern_slug": "strings",
        "title": "Valid Anagram",
        "slug": "valid-anagram",
        "difficulty": "easy",
        "short_description": "Check whether two strings are anagrams of each other.",
        "statement": "Given two strings s and t, return true if t is an anagram of s, and false otherwise.",
        "constraints_text": "1 <= s.length, t.length <= 5 * 10^4, s and t consist of lowercase English letters.",
        "examples_json": [
            {"input": "s = \"anagram\", t = \"nagaram\"", "output": "True", "explanation": "They contain the same letters with the same counts."},
            {"input": "s = \"rat\", t = \"car\"", "output": "False", "explanation": "The letter counts differ."},
        ],
        "starter_code_json": program_starters("valid-anagram"),
        "test_cases": [
            {"label": "Positive case", "input": "anagram\nnagaram", "expected_output": "True", "is_hidden": False},
            {"label": "Negative case", "input": "rat\ncar", "expected_output": "False", "is_hidden": False},
            {"label": "Different lengths", "input": "a\nab", "expected_output": "False", "is_hidden": True},
            {"label": "Repeated chars", "input": "listen\nsilent", "expected_output": "True", "is_hidden": True},
        ],
    },
    {
        "pattern_slug": "recursion-dp",
        "title": "Climbing Stairs",
        "slug": "climbing-stairs",
        "difficulty": "easy",
        "short_description": "Count the distinct ways to reach the top with 1-step or 2-step moves.",
        "statement": "You are climbing a staircase. It takes n steps to reach the top. Each time you can climb either 1 or 2 steps. Return the number of distinct ways to reach the top.",
        "constraints_text": "1 <= n <= 45.",
        "examples_json": [
            {"input": "n = 2", "output": "2", "explanation": "Either 1+1 or 2."},
            {"input": "n = 3", "output": "3", "explanation": "1+1+1, 1+2, or 2+1."},
        ],
        "starter_code_json": program_starters("climbing-stairs"),
        "test_cases": [
            {"label": "Two steps", "input": "2", "expected_output": "2", "is_hidden": False},
            {"label": "Three steps", "input": "3", "expected_output": "3", "is_hidden": False},
            {"label": "Five steps", "input": "5", "expected_output": "8", "is_hidden": True},
            {"label": "One step", "input": "1", "expected_output": "1", "is_hidden": True},
        ],
    },
    {
        "pattern_slug": "recursion-dp",
        "title": "Maximum Subarray",
        "slug": "maximum-subarray",
        "difficulty": "medium",
        "short_description": "Find the contiguous subarray with the largest sum.",
        "statement": "Given an integer array nums, find the contiguous subarray with the largest sum and return that sum.",
        "constraints_text": "1 <= nums.length <= 10^5, -10^4 <= nums[i] <= 10^4.",
        "examples_json": [
            {"input": "nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]", "output": "6", "explanation": "The best subarray is [4, -1, 2, 1]."},
            {"input": "nums = [1]", "output": "1", "explanation": "A single value is the best subarray."},
        ],
        "starter_code_json": program_starters("maximum-subarray"),
        "test_cases": [
            {"label": "Kadane classic", "input": "[-2, 1, -3, 4, -1, 2, 1, -5, 4]", "expected_output": "6", "is_hidden": False},
            {"label": "Single element", "input": "[1]", "expected_output": "1", "is_hidden": False},
            {"label": "All positive", "input": "[5, 4, -1, 7, 8]", "expected_output": "23", "is_hidden": True},
            {"label": "All negative", "input": "[-3, -2, -5]", "expected_output": "-2", "is_hidden": True},
        ],
    },
    {
        "pattern_slug": "arrays",
        "title": "Container With Most Water",
        "slug": "container-with-most-water",
        "difficulty": "medium",
        "short_description": "Use two pointers to maximize water area between vertical lines.",
        "statement": "You are given an integer array height where each value represents the height of a vertical line. Find two lines that together with the x-axis form a container that holds the most water. Return that maximum area.",
        "constraints_text": "2 <= height.length <= 10^5, 0 <= height[i] <= 10^4.",
        "examples_json": [
            {"input": "height = [1, 8, 6, 2, 5, 4, 8, 3, 7]", "output": "49", "explanation": "The best container uses heights 8 and 7."},
            {"input": "height = [1, 1]", "output": "1", "explanation": "Only one container is possible."},
        ],
        "starter_code_json": program_starters("container-with-most-water"),
        "test_cases": [
            {"label": "Classic example", "input": "[1, 8, 6, 2, 5, 4, 8, 3, 7]", "expected_output": "49", "is_hidden": False},
            {"label": "Two bars", "input": "[1, 1]", "expected_output": "1", "is_hidden": False},
            {"label": "Wide best", "input": "[4, 3, 2, 1, 4]", "expected_output": "16", "is_hidden": True},
            {"label": "Inner best", "input": "[1, 2, 1]", "expected_output": "2", "is_hidden": True},
        ],
    },
]


def ensure_patterns(db):
    from app.models.pattern import Pattern

    created = 0
    for payload in PATTERNS:
        existing = db.query(Pattern).filter(Pattern.slug == payload["slug"]).first()
        if existing:
            existing.name = payload["name"]
            existing.description = payload["description"]
            existing.icon_name = payload["icon_name"]
            existing.order_index = payload["order_index"]
            continue

        db.add(Pattern(**payload))
        created += 1

    db.commit()
    return created


def prune_non_curated_content(db):
    from app.models.pattern import Pattern
    from app.models.problem import Problem
    from app.models.testcase import TestCase

    curated_pattern_slugs = {payload["slug"] for payload in PATTERNS}
    curated_problem_slugs = {payload["slug"] for payload in PROBLEMS}

    non_curated_problem_ids = [
        row[0]
        for row in db.query(Problem.id).filter(~Problem.slug.in_(curated_problem_slugs)).all()
    ]
    if non_curated_problem_ids:
        db.query(TestCase).filter(TestCase.problem_id.in_(non_curated_problem_ids)).delete(synchronize_session=False)
        db.query(Problem).filter(Problem.id.in_(non_curated_problem_ids)).delete(synchronize_session=False)

    db.query(Pattern).filter(~Pattern.slug.in_(curated_pattern_slugs)).delete(synchronize_session=False)
    db.commit()


def upsert_problem(db, payload: Dict, pattern_map: Dict[str, int], order_index: int) -> Problem:
    from app.models.problem import Problem

    problem = db.query(Problem).filter(Problem.slug == payload["slug"]).first()
    if not problem:
        problem = Problem()
        db.add(problem)

    problem.slug = payload["slug"]
    problem.pattern_id = pattern_map[payload["pattern_slug"]]
    problem.title = payload["title"]
    problem.difficulty = payload["difficulty"]
    problem.short_description = payload["short_description"]
    problem.statement = payload["statement"]
    problem.input_format = problem_input_format(payload["slug"])
    problem.output_format = problem_output_format(payload["slug"])
    problem.constraints_text = payload["constraints_text"]
    problem.examples_json = payload["examples_json"]
    problem.starter_code_json = payload["starter_code_json"]
    problem.reference_solution_json = payload.get("reference_solution_json")
    problem.order_index = order_index
    problem.is_active = True
    return problem


def replace_test_cases(db, problem: Problem, test_cases: List[Dict]) -> int:
    from app.models.testcase import TestCase

    db.query(TestCase).filter(TestCase.problem_id == problem.id).delete()
    created = 0
    for index, test_case in enumerate(test_cases, start=1):
        db.add(
            TestCase(
                problem_id=problem.id,
                label=test_case["label"],
                input=test_case["input"],
                expected_output=test_case["expected_output"],
                is_hidden=test_case["is_hidden"],
                order_index=index,
            )
        )
        created += 1
    return created


def ensure_problems_and_tests(db):
    from app.models.pattern import Pattern
    from app.models.problem import Problem

    created_problems = 0
    created_tests = 0
    pattern_map = {p.slug: p.id for p in db.query(Pattern).all()}

    for index, payload in enumerate(PROBLEMS, start=1):
        existing = db.query(Problem).filter(Problem.slug == payload["slug"]).first()
        if not existing:
            created_problems += 1

        problem = upsert_problem(db, payload, pattern_map, index)
        db.flush()
        created_tests += replace_test_cases(db, problem, payload["test_cases"])

    db.commit()
    return created_problems, created_tests


def seed():
    from app.database import SessionLocal
    from app.models.pattern import Pattern
    from app.models.problem import Problem
    from app.models.testcase import TestCase

    db = SessionLocal()
    try:
        prune_non_curated_content(db)
        created_patterns = ensure_patterns(db)
        created_problems, created_tests = ensure_problems_and_tests(db)

        total_patterns = db.query(Pattern).count()
        total_problems = db.query(Problem).count()
        total_tests = db.query(TestCase).count()

        print(f"Patterns created: {created_patterns}")
        print(f"Problems created: {created_problems}")
        print(f"Test cases replaced/created: {created_tests}")
        print(
            f"Totals -> patterns: {total_patterns}, problems: {total_problems}, "
            f"test_cases: {total_tests}"
        )
    except Exception as exc:
        db.rollback()
        print(f"Seed failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()

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


def starter_two_sum(language: str) -> str:
    if language == "python":
        return """nums = eval(input().strip())
target = int(input().strip())

seen = {}
answer = []
for i, num in enumerate(nums):
    needed = target - num
    if needed in seen:
        answer = [seen[needed], i]
        break
    seen[num] = i

print(answer)
"""
    if language == "javascript":
        return """const fs = require('fs');
const lines = fs.readFileSync(0, 'utf8').trim().split(/\\r?\\n/);
const nums = JSON.parse(lines[0]);
const target = Number(lines[1]);

const seen = new Map();
let answer = [];
for (let i = 0; i < nums.length; i += 1) {
  const needed = target - nums[i];
  if (seen.has(needed)) {
    answer = [seen.get(needed), i];
    break;
  }
  seen.set(nums[i], i);
}

console.log(JSON.stringify(answer));
"""
    if language == "java":
        return """import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.Map;

public class Solution {
    private static int[] parseIntArray(String raw) {
        String cleaned = raw.trim();
        if (cleaned.length() <= 2) return new int[0];
        cleaned = cleaned.substring(1, cleaned.length() - 1);
        String[] parts = cleaned.split(",");
        int[] nums = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            nums[i] = Integer.parseInt(parts[i].trim());
        }
        return nums;
    }

    private static String formatArray(int[] nums) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < nums.length; i++) {
            if (i > 0) sb.append(", ");
            sb.append(nums[i]);
        }
        sb.append("]");
        return sb.toString();
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int[] nums = parseIntArray(br.readLine());
        int target = Integer.parseInt(br.readLine().trim());

        Map<Integer, Integer> seen = new HashMap<>();
        int[] answer = new int[0];
        for (int i = 0; i < nums.length; i++) {
            int needed = target - nums[i];
            if (seen.containsKey(needed)) {
                answer = new int[]{seen.get(needed), i};
                break;
            }
            seen.put(nums[i], i);
        }

        System.out.println(formatArray(answer));
    }
}
"""
    return """#include <iostream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;

vector<int> parseIntArray(string raw) {
    vector<int> result;
    if (raw.size() <= 2) return result;
    raw = raw.substr(1, raw.size() - 2);
    stringstream ss(raw);
    string part;
    while (getline(ss, part, ',')) {
        result.push_back(stoi(part));
    }
    return result;
}

string formatArray(const vector<int>& nums) {
    stringstream out;
    out << "[";
    for (size_t i = 0; i < nums.size(); ++i) {
        if (i > 0) out << ", ";
        out << nums[i];
    }
    out << "]";
    return out.str();
}

int main() {
    string numsLine;
    string targetLine;
    getline(cin, numsLine);
    getline(cin, targetLine);

    vector<int> nums = parseIntArray(numsLine);
    int target = stoi(targetLine);
    unordered_map<int, int> seen;
    vector<int> answer;

    for (int i = 0; i < static_cast<int>(nums.size()); ++i) {
        int needed = target - nums[i];
        if (seen.count(needed)) {
            answer = {seen[needed], i};
            break;
        }
        seen[nums[i]] = i;
    }

    cout << formatArray(answer) << endl;
    return 0;
}
"""


def starter_stock(language: str) -> str:
    body = {
        "python": """prices = eval(input().strip())

best = 0
min_price = float("inf")
for price in prices:
    min_price = min(min_price, price)
    best = max(best, price - min_price)

print(best)
""",
        "javascript": """const fs = require('fs');
const prices = JSON.parse(fs.readFileSync(0, 'utf8').trim());

let best = 0;
let minPrice = Infinity;
for (const price of prices) {
  minPrice = Math.min(minPrice, price);
  best = Math.max(best, price - minPrice);
}

console.log(best);
""",
        "java": """import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Solution {
    private static int[] parseIntArray(String raw) {
        String cleaned = raw.trim();
        if (cleaned.length() <= 2) return new int[0];
        cleaned = cleaned.substring(1, cleaned.length() - 1);
        String[] parts = cleaned.split(",");
        int[] nums = new int[parts.length];
        for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i].trim());
        return nums;
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int[] prices = parseIntArray(br.readLine());

        int best = 0;
        int minPrice = Integer.MAX_VALUE;
        for (int price : prices) {
            minPrice = Math.min(minPrice, price);
            best = Math.max(best, price - minPrice);
        }

        System.out.println(best);
    }
}
""",
        "cpp": """#include <climits>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
using namespace std;

vector<int> parseIntArray(string raw) {
    vector<int> result;
    if (raw.size() <= 2) return result;
    raw = raw.substr(1, raw.size() - 2);
    stringstream ss(raw);
    string part;
    while (getline(ss, part, ',')) result.push_back(stoi(part));
    return result;
}

int main() {
    string line;
    getline(cin, line);
    vector<int> prices = parseIntArray(line);

    int best = 0;
    int minPrice = INT_MAX;
    for (int price : prices) {
        minPrice = min(minPrice, price);
        best = max(best, price - minPrice);
    }

    cout << best << endl;
    return 0;
}
""",
    }
    return body[language]


def starter_move_zeroes(language: str) -> str:
    if language == "python":
        return """nums = eval(input().strip())

insert = 0
for num in nums:
    if num != 0:
        nums[insert] = num
        insert += 1
while insert < len(nums):
    nums[insert] = 0
    insert += 1

print(nums)
"""
    if language == "javascript":
        return """const fs = require('fs');
const nums = JSON.parse(fs.readFileSync(0, 'utf8').trim());

let insert = 0;
for (const num of nums) {
  if (num !== 0) {
    nums[insert] = num;
    insert += 1;
  }
}
while (insert < nums.length) {
  nums[insert] = 0;
  insert += 1;
}

console.log(JSON.stringify(nums));
"""
    if language == "java":
        return """import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Solution {
    private static int[] parseIntArray(String raw) {
        String cleaned = raw.trim();
        if (cleaned.length() <= 2) return new int[0];
        cleaned = cleaned.substring(1, cleaned.length() - 1);
        String[] parts = cleaned.split(",");
        int[] nums = new int[parts.length];
        for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i].trim());
        return nums;
    }

    private static String formatArray(int[] nums) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < nums.length; i++) {
            if (i > 0) sb.append(", ");
            sb.append(nums[i]);
        }
        sb.append("]");
        return sb.toString();
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int[] nums = parseIntArray(br.readLine());

        int insert = 0;
        for (int num : nums) {
            if (num != 0) nums[insert++] = num;
        }
        while (insert < nums.length) nums[insert++] = 0;

        System.out.println(formatArray(nums));
    }
}
"""
    return """#include <iostream>
#include <sstream>
#include <string>
#include <vector>
using namespace std;

vector<int> parseIntArray(string raw) {
    vector<int> result;
    if (raw.size() <= 2) return result;
    raw = raw.substr(1, raw.size() - 2);
    stringstream ss(raw);
    string part;
    while (getline(ss, part, ',')) result.push_back(stoi(part));
    return result;
}

string formatArray(const vector<int>& nums) {
    stringstream out;
    out << "[";
    for (size_t i = 0; i < nums.size(); ++i) {
        if (i > 0) out << ", ";
        out << nums[i];
    }
    out << "]";
    return out.str();
}

int main() {
    string line;
    getline(cin, line);
    vector<int> nums = parseIntArray(line);

    int insert = 0;
    for (int num : nums) {
        if (num != 0) nums[insert++] = num;
    }
    while (insert < static_cast<int>(nums.size())) nums[insert++] = 0;

    cout << formatArray(nums) << endl;
    return 0;
}
"""


def starter_product_except_self(language: str) -> str:
    if language == "python":
        return """nums = eval(input().strip())
n = len(nums)
answer = [1] * n

prefix = 1
for i in range(n):
    answer[i] = prefix
    prefix *= nums[i]

suffix = 1
for i in range(n - 1, -1, -1):
    answer[i] *= suffix
    suffix *= nums[i]

print(answer)
"""
    if language == "javascript":
        return """const fs = require('fs');
const nums = JSON.parse(fs.readFileSync(0, 'utf8').trim());
const answer = new Array(nums.length).fill(1);

let prefix = 1;
for (let i = 0; i < nums.length; i += 1) {
  answer[i] = prefix;
  prefix *= nums[i];
}

let suffix = 1;
for (let i = nums.length - 1; i >= 0; i -= 1) {
  answer[i] *= suffix;
  suffix *= nums[i];
}

console.log(JSON.stringify(answer));
"""
    if language == "java":
        return """import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Solution {
    private static int[] parseIntArray(String raw) {
        String cleaned = raw.trim();
        if (cleaned.length() <= 2) return new int[0];
        cleaned = cleaned.substring(1, cleaned.length() - 1);
        String[] parts = cleaned.split(",");
        int[] nums = new int[parts.length];
        for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i].trim());
        return nums;
    }

    private static String formatArray(int[] nums) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < nums.length; i++) {
            if (i > 0) sb.append(", ");
            sb.append(nums[i]);
        }
        sb.append("]");
        return sb.toString();
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int[] nums = parseIntArray(br.readLine());
        int[] answer = new int[nums.length];

        int prefix = 1;
        for (int i = 0; i < nums.length; i++) {
            answer[i] = prefix;
            prefix *= nums[i];
        }

        int suffix = 1;
        for (int i = nums.length - 1; i >= 0; i--) {
            answer[i] *= suffix;
            suffix *= nums[i];
        }

        System.out.println(formatArray(answer));
    }
}
"""
    return """#include <iostream>
#include <sstream>
#include <string>
#include <vector>
using namespace std;

vector<int> parseIntArray(string raw) {
    vector<int> result;
    if (raw.size() <= 2) return result;
    raw = raw.substr(1, raw.size() - 2);
    stringstream ss(raw);
    string part;
    while (getline(ss, part, ',')) result.push_back(stoi(part));
    return result;
}

string formatArray(const vector<int>& nums) {
    stringstream out;
    out << "[";
    for (size_t i = 0; i < nums.size(); ++i) {
        if (i > 0) out << ", ";
        out << nums[i];
    }
    out << "]";
    return out.str();
}

int main() {
    string line;
    getline(cin, line);
    vector<int> nums = parseIntArray(line);
    vector<int> answer(nums.size(), 1);

    int prefix = 1;
    for (int i = 0; i < static_cast<int>(nums.size()); ++i) {
        answer[i] = prefix;
        prefix *= nums[i];
    }

    int suffix = 1;
    for (int i = static_cast<int>(nums.size()) - 1; i >= 0; --i) {
        answer[i] *= suffix;
        suffix *= nums[i];
    }

    cout << formatArray(answer) << endl;
    return 0;
}
"""


def starter_valid_palindrome(language: str) -> str:
    if language == "python":
        return """s = input().rstrip("\\n")
filtered = [ch.lower() for ch in s if ch.isalnum()]
print(str(filtered == filtered[::-1]))
"""
    if language == "javascript":
        return """const fs = require('fs');
const s = fs.readFileSync(0, 'utf8').trimEnd();
const filtered = [...s.toLowerCase()].filter(ch => /[a-z0-9]/.test(ch)).join('');
console.log(filtered === [...filtered].reverse().join('') ? 'True' : 'False');
"""
    if language == "java":
        return """import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Solution {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        if (s == null) s = "";
        StringBuilder filtered = new StringBuilder();
        for (char ch : s.toLowerCase().toCharArray()) {
            if (Character.isLetterOrDigit(ch)) filtered.append(ch);
        }
        String cleaned = filtered.toString();
        String reversed = filtered.reverse().toString();
        System.out.println(cleaned.equals(reversed) ? "True" : "False");
    }
}
"""
    return """#include <algorithm>
#include <cctype>
#include <iostream>
#include <string>
using namespace std;

int main() {
    string s;
    getline(cin, s);
    string filtered;
    for (char ch : s) {
        if (isalnum(static_cast<unsigned char>(ch))) {
            filtered.push_back(static_cast<char>(tolower(static_cast<unsigned char>(ch))));
        }
    }
    string reversed = filtered;
    reverse(reversed.begin(), reversed.end());
    cout << (filtered == reversed ? "True" : "False") << endl;
    return 0;
}
"""


def starter_two_sum_sorted(language: str) -> str:
    if language == "python":
        return """numbers = eval(input().strip())
target = int(input().strip())

left, right = 0, len(numbers) - 1
answer = []
while left < right:
    total = numbers[left] + numbers[right]
    if total == target:
        answer = [left + 1, right + 1]
        break
    if total < target:
        left += 1
    else:
        right -= 1

print(answer)
"""
    if language == "javascript":
        return """const fs = require('fs');
const lines = fs.readFileSync(0, 'utf8').trim().split(/\\r?\\n/);
const numbers = JSON.parse(lines[0]);
const target = Number(lines[1]);

let left = 0;
let right = numbers.length - 1;
let answer = [];
while (left < right) {
  const total = numbers[left] + numbers[right];
  if (total === target) {
    answer = [left + 1, right + 1];
    break;
  }
  if (total < target) left += 1;
  else right -= 1;
}

console.log(JSON.stringify(answer));
"""
    if language == "java":
        return """import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Solution {
    private static int[] parseIntArray(String raw) {
        String cleaned = raw.trim();
        if (cleaned.length() <= 2) return new int[0];
        cleaned = cleaned.substring(1, cleaned.length() - 1);
        String[] parts = cleaned.split(",");
        int[] nums = new int[parts.length];
        for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i].trim());
        return nums;
    }

    private static String formatArray(int[] nums) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < nums.length; i++) {
            if (i > 0) sb.append(", ");
            sb.append(nums[i]);
        }
        sb.append("]");
        return sb.toString();
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int[] numbers = parseIntArray(br.readLine());
        int target = Integer.parseInt(br.readLine().trim());

        int left = 0;
        int right = numbers.length - 1;
        int[] answer = new int[0];
        while (left < right) {
            int total = numbers[left] + numbers[right];
            if (total == target) {
                answer = new int[]{left + 1, right + 1};
                break;
            }
            if (total < target) left++;
            else right--;
        }

        System.out.println(formatArray(answer));
    }
}
"""
    return """#include <iostream>
#include <sstream>
#include <string>
#include <vector>
using namespace std;

vector<int> parseIntArray(string raw) {
    vector<int> result;
    if (raw.size() <= 2) return result;
    raw = raw.substr(1, raw.size() - 2);
    stringstream ss(raw);
    string part;
    while (getline(ss, part, ',')) result.push_back(stoi(part));
    return result;
}

string formatArray(const vector<int>& nums) {
    stringstream out;
    out << "[";
    for (size_t i = 0; i < nums.size(); ++i) {
        if (i > 0) out << ", ";
        out << nums[i];
    }
    out << "]";
    return out.str();
}

int main() {
    string numbersLine;
    string targetLine;
    getline(cin, numbersLine);
    getline(cin, targetLine);
    vector<int> numbers = parseIntArray(numbersLine);
    int target = stoi(targetLine);

    int left = 0;
    int right = static_cast<int>(numbers.size()) - 1;
    vector<int> answer;
    while (left < right) {
        int total = numbers[left] + numbers[right];
        if (total == target) {
            answer = {left + 1, right + 1};
            break;
        }
        if (total < target) left++;
        else right--;
    }

    cout << formatArray(answer) << endl;
    return 0;
}
"""


def starter_longest_substring(language: str) -> str:
    if language == "python":
        return """s = input().rstrip("\\n")
seen = {}
left = 0
best = 0

for right, ch in enumerate(s):
    if ch in seen and seen[ch] >= left:
        left = seen[ch] + 1
    seen[ch] = right
    best = max(best, right - left + 1)

print(best)
"""
    if language == "javascript":
        return """const fs = require('fs');
const s = fs.readFileSync(0, 'utf8').trimEnd();
const seen = new Map();
let left = 0;
let best = 0;

for (let right = 0; right < s.length; right += 1) {
  const ch = s[right];
  if (seen.has(ch) && seen.get(ch) >= left) {
    left = seen.get(ch) + 1;
  }
  seen.set(ch, right);
  best = Math.max(best, right - left + 1);
}

console.log(best);
"""
    if language == "java":
        return """import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.Map;

public class Solution {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        if (s == null) s = "";

        Map<Character, Integer> seen = new HashMap<>();
        int left = 0;
        int best = 0;
        for (int right = 0; right < s.length(); right++) {
            char ch = s.charAt(right);
            if (seen.containsKey(ch) && seen.get(ch) >= left) {
                left = seen.get(ch) + 1;
            }
            seen.put(ch, right);
            best = Math.max(best, right - left + 1);
        }

        System.out.println(best);
    }
}
"""
    return """#include <iostream>
#include <string>
#include <unordered_map>
using namespace std;

int main() {
    string s;
    getline(cin, s);

    unordered_map<char, int> seen;
    int left = 0;
    int best = 0;
    for (int right = 0; right < static_cast<int>(s.size()); ++right) {
        char ch = s[right];
        if (seen.count(ch) && seen[ch] >= left) {
            left = seen[ch] + 1;
        }
        seen[ch] = right;
        best = max(best, right - left + 1);
    }

    cout << best << endl;
    return 0;
}
"""


def starter_max_average(language: str) -> str:
    if language == "python":
        return """nums = eval(input().strip())
k = int(input().strip())

window_sum = sum(nums[:k])
best = window_sum
for i in range(k, len(nums)):
    window_sum += nums[i] - nums[i - k]
    best = max(best, window_sum)

print(best / k)
"""
    if language == "javascript":
        return """const fs = require('fs');
const lines = fs.readFileSync(0, 'utf8').trim().split(/\\r?\\n/);
const nums = JSON.parse(lines[0]);
const k = Number(lines[1]);

let windowSum = nums.slice(0, k).reduce((acc, val) => acc + val, 0);
let best = windowSum;
for (let i = k; i < nums.length; i += 1) {
  windowSum += nums[i] - nums[i - k];
  best = Math.max(best, windowSum);
}

console.log(best / k);
"""
    if language == "java":
        return """import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Solution {
    private static int[] parseIntArray(String raw) {
        String cleaned = raw.trim();
        if (cleaned.length() <= 2) return new int[0];
        cleaned = cleaned.substring(1, cleaned.length() - 1);
        String[] parts = cleaned.split(",");
        int[] nums = new int[parts.length];
        for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i].trim());
        return nums;
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int[] nums = parseIntArray(br.readLine());
        int k = Integer.parseInt(br.readLine().trim());

        int windowSum = 0;
        for (int i = 0; i < k; i++) windowSum += nums[i];
        int best = windowSum;
        for (int i = k; i < nums.length; i++) {
            windowSum += nums[i] - nums[i - k];
            best = Math.max(best, windowSum);
        }

        System.out.println(best / (double) k);
    }
}
"""
    return """#include <iostream>
#include <sstream>
#include <string>
#include <vector>
using namespace std;

vector<int> parseIntArray(string raw) {
    vector<int> result;
    if (raw.size() <= 2) return result;
    raw = raw.substr(1, raw.size() - 2);
    stringstream ss(raw);
    string part;
    while (getline(ss, part, ',')) result.push_back(stoi(part));
    return result;
}

int main() {
    string numsLine;
    string kLine;
    getline(cin, numsLine);
    getline(cin, kLine);
    vector<int> nums = parseIntArray(numsLine);
    int k = stoi(kLine);

    int windowSum = 0;
    for (int i = 0; i < k; ++i) windowSum += nums[i];
    int best = windowSum;
    for (int i = k; i < static_cast<int>(nums.size()); ++i) {
        windowSum += nums[i] - nums[i - k];
        best = max(best, windowSum);
    }

    cout << (best / static_cast<double>(k)) << endl;
    return 0;
}
"""


def starter_binary_search(language: str) -> str:
    if language == "python":
        return """nums = eval(input().strip())
target = int(input().strip())

left, right = 0, len(nums) - 1
answer = -1
while left <= right:
    mid = (left + right) // 2
    if nums[mid] == target:
        answer = mid
        break
    if nums[mid] < target:
        left = mid + 1
    else:
        right = mid - 1

print(answer)
"""
    if language == "javascript":
        return """const fs = require('fs');
const lines = fs.readFileSync(0, 'utf8').trim().split(/\\r?\\n/);
const nums = JSON.parse(lines[0]);
const target = Number(lines[1]);

let left = 0;
let right = nums.length - 1;
let answer = -1;
while (left <= right) {
  const mid = Math.floor((left + right) / 2);
  if (nums[mid] === target) {
    answer = mid;
    break;
  }
  if (nums[mid] < target) left = mid + 1;
  else right = mid - 1;
}

console.log(answer);
"""
    if language == "java":
        return """import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Solution {
    private static int[] parseIntArray(String raw) {
        String cleaned = raw.trim();
        if (cleaned.length() <= 2) return new int[0];
        cleaned = cleaned.substring(1, cleaned.length() - 1);
        String[] parts = cleaned.split(",");
        int[] nums = new int[parts.length];
        for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i].trim());
        return nums;
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int[] nums = parseIntArray(br.readLine());
        int target = Integer.parseInt(br.readLine().trim());

        int left = 0;
        int right = nums.length - 1;
        int answer = -1;
        while (left <= right) {
            int mid = (left + right) / 2;
            if (nums[mid] == target) {
                answer = mid;
                break;
            }
            if (nums[mid] < target) left = mid + 1;
            else right = mid - 1;
        }

        System.out.println(answer);
    }
}
"""
    return """#include <iostream>
#include <sstream>
#include <string>
#include <vector>
using namespace std;

vector<int> parseIntArray(string raw) {
    vector<int> result;
    if (raw.size() <= 2) return result;
    raw = raw.substr(1, raw.size() - 2);
    stringstream ss(raw);
    string part;
    while (getline(ss, part, ',')) result.push_back(stoi(part));
    return result;
}

int main() {
    string numsLine;
    string targetLine;
    getline(cin, numsLine);
    getline(cin, targetLine);
    vector<int> nums = parseIntArray(numsLine);
    int target = stoi(targetLine);

    int left = 0;
    int right = static_cast<int>(nums.size()) - 1;
    int answer = -1;
    while (left <= right) {
        int mid = (left + right) / 2;
        if (nums[mid] == target) {
            answer = mid;
            break;
        }
        if (nums[mid] < target) left = mid + 1;
        else right = mid - 1;
    }

    cout << answer << endl;
    return 0;
}
"""


def starter_search_insert(language: str) -> str:
    if language == "python":
        return """nums = eval(input().strip())
target = int(input().strip())

left, right = 0, len(nums)
while left < right:
    mid = (left + right) // 2
    if nums[mid] < target:
        left = mid + 1
    else:
        right = mid

print(left)
"""
    if language == "javascript":
        return """const fs = require('fs');
const lines = fs.readFileSync(0, 'utf8').trim().split(/\\r?\\n/);
const nums = JSON.parse(lines[0]);
const target = Number(lines[1]);

let left = 0;
let right = nums.length;
while (left < right) {
  const mid = Math.floor((left + right) / 2);
  if (nums[mid] < target) left = mid + 1;
  else right = mid;
}

console.log(left);
"""
    if language == "java":
        return """import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Solution {
    private static int[] parseIntArray(String raw) {
        String cleaned = raw.trim();
        if (cleaned.length() <= 2) return new int[0];
        cleaned = cleaned.substring(1, cleaned.length() - 1);
        String[] parts = cleaned.split(",");
        int[] nums = new int[parts.length];
        for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i].trim());
        return nums;
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int[] nums = parseIntArray(br.readLine());
        int target = Integer.parseInt(br.readLine().trim());

        int left = 0;
        int right = nums.length;
        while (left < right) {
            int mid = (left + right) / 2;
            if (nums[mid] < target) left = mid + 1;
            else right = mid;
        }

        System.out.println(left);
    }
}
"""
    return """#include <iostream>
#include <sstream>
#include <string>
#include <vector>
using namespace std;

vector<int> parseIntArray(string raw) {
    vector<int> result;
    if (raw.size() <= 2) return result;
    raw = raw.substr(1, raw.size() - 2);
    stringstream ss(raw);
    string part;
    while (getline(ss, part, ',')) result.push_back(stoi(part));
    return result;
}

int main() {
    string numsLine;
    string targetLine;
    getline(cin, numsLine);
    getline(cin, targetLine);
    vector<int> nums = parseIntArray(numsLine);
    int target = stoi(targetLine);

    int left = 0;
    int right = static_cast<int>(nums.size());
    while (left < right) {
        int mid = (left + right) / 2;
        if (nums[mid] < target) left = mid + 1;
        else right = mid;
    }

    cout << left << endl;
    return 0;
}
"""


def starter_reverse_string(language: str) -> str:
    if language == "python":
        return """s = input().rstrip("\\n")
print(s[::-1])
"""
    if language == "javascript":
        return """const fs = require('fs');
const s = fs.readFileSync(0, 'utf8').trimEnd();
console.log([...s].reverse().join(''));
"""
    if language == "java":
        return """import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Solution {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        if (s == null) s = "";
        System.out.println(new StringBuilder(s).reverse().toString());
    }
}
"""
    return """#include <algorithm>
#include <iostream>
#include <string>
using namespace std;

int main() {
    string s;
    getline(cin, s);
    reverse(s.begin(), s.end());
    cout << s << endl;
    return 0;
}
"""


def starter_valid_anagram(language: str) -> str:
    if language == "python":
        return """s = input().rstrip("\\n")
t = input().rstrip("\\n")
print(str(sorted(s) == sorted(t)))
"""
    if language == "javascript":
        return """const fs = require('fs');
const lines = fs.readFileSync(0, 'utf8').trimEnd().split(/\\r?\\n/);
const s = lines[0] || '';
const t = lines[1] || '';
const normalize = value => [...value].sort().join('');
console.log(normalize(s) === normalize(t) ? 'True' : 'False');
"""
    if language == "java":
        return """import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.Arrays;

public class Solution {
    private static String sorted(String value) {
        char[] chars = value.toCharArray();
        Arrays.sort(chars);
        return new String(chars);
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        String t = br.readLine();
        if (s == null) s = "";
        if (t == null) t = "";
        System.out.println(sorted(s).equals(sorted(t)) ? "True" : "False");
    }
}
"""
    return """#include <algorithm>
#include <iostream>
#include <string>
using namespace std;

int main() {
    string s;
    string t;
    getline(cin, s);
    getline(cin, t);
    string a = s;
    string b = t;
    sort(a.begin(), a.end());
    sort(b.begin(), b.end());
    cout << (a == b ? "True" : "False") << endl;
    return 0;
}
"""


def starter_climbing_stairs(language: str) -> str:
    if language == "python":
        return """n = int(input().strip())

if n <= 2:
    print(n)
else:
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    print(b)
"""
    if language == "javascript":
        return """const fs = require('fs');
const n = Number(fs.readFileSync(0, 'utf8').trim());

if (n <= 2) {
  console.log(n);
} else {
  let a = 1;
  let b = 2;
  for (let step = 3; step <= n; step += 1) {
    [a, b] = [b, a + b];
  }
  console.log(b);
}
"""
    if language == "java":
        return """import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Solution {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        if (n <= 2) {
            System.out.println(n);
            return;
        }

        int a = 1;
        int b = 2;
        for (int step = 3; step <= n; step++) {
            int next = a + b;
            a = b;
            b = next;
        }

        System.out.println(b);
    }
}
"""
    return """#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    if (n <= 2) {
        cout << n << endl;
        return 0;
    }
    int a = 1;
    int b = 2;
    for (int step = 3; step <= n; ++step) {
        int next = a + b;
        a = b;
        b = next;
    }
    cout << b << endl;
    return 0;
}
"""


def starter_max_subarray(language: str) -> str:
    if language == "python":
        return """nums = eval(input().strip())
current = best = nums[0]
for num in nums[1:]:
    current = max(num, current + num)
    best = max(best, current)
print(best)
"""
    if language == "javascript":
        return """const fs = require('fs');
const nums = JSON.parse(fs.readFileSync(0, 'utf8').trim());
let current = nums[0];
let best = nums[0];
for (let i = 1; i < nums.length; i += 1) {
  current = Math.max(nums[i], current + nums[i]);
  best = Math.max(best, current);
}
console.log(best);
"""
    if language == "java":
        return """import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Solution {
    private static int[] parseIntArray(String raw) {
        String cleaned = raw.trim();
        if (cleaned.length() <= 2) return new int[0];
        cleaned = cleaned.substring(1, cleaned.length() - 1);
        String[] parts = cleaned.split(",");
        int[] nums = new int[parts.length];
        for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i].trim());
        return nums;
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int[] nums = parseIntArray(br.readLine());
        int current = nums[0];
        int best = nums[0];
        for (int i = 1; i < nums.length; i++) {
            current = Math.max(nums[i], current + nums[i]);
            best = Math.max(best, current);
        }
        System.out.println(best);
    }
}
"""
    return """#include <iostream>
#include <sstream>
#include <string>
#include <vector>
using namespace std;

vector<int> parseIntArray(string raw) {
    vector<int> result;
    if (raw.size() <= 2) return result;
    raw = raw.substr(1, raw.size() - 2);
    stringstream ss(raw);
    string part;
    while (getline(ss, part, ',')) result.push_back(stoi(part));
    return result;
}

int main() {
    string line;
    getline(cin, line);
    vector<int> nums = parseIntArray(line);
    int current = nums[0];
    int best = nums[0];
    for (int i = 1; i < static_cast<int>(nums.size()); ++i) {
        current = max(nums[i], current + nums[i]);
        best = max(best, current);
    }
    cout << best << endl;
    return 0;
}
"""


def starter_container(language: str) -> str:
    if language == "python":
        return """height = eval(input().strip())
left, right = 0, len(height) - 1
best = 0

while left < right:
    best = max(best, min(height[left], height[right]) * (right - left))
    if height[left] < height[right]:
        left += 1
    else:
        right -= 1

print(best)
"""
    if language == "javascript":
        return """const fs = require('fs');
const height = JSON.parse(fs.readFileSync(0, 'utf8').trim());

let left = 0;
let right = height.length - 1;
let best = 0;
while (left < right) {
  best = Math.max(best, Math.min(height[left], height[right]) * (right - left));
  if (height[left] < height[right]) left += 1;
  else right -= 1;
}

console.log(best);
"""
    if language == "java":
        return """import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Solution {
    private static int[] parseIntArray(String raw) {
        String cleaned = raw.trim();
        if (cleaned.length() <= 2) return new int[0];
        cleaned = cleaned.substring(1, cleaned.length() - 1);
        String[] parts = cleaned.split(",");
        int[] nums = new int[parts.length];
        for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i].trim());
        return nums;
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int[] height = parseIntArray(br.readLine());
        int left = 0;
        int right = height.length - 1;
        int best = 0;

        while (left < right) {
            best = Math.max(best, Math.min(height[left], height[right]) * (right - left));
            if (height[left] < height[right]) left++;
            else right--;
        }

        System.out.println(best);
    }
}
"""
    return """#include <iostream>
#include <sstream>
#include <string>
#include <vector>
using namespace std;

vector<int> parseIntArray(string raw) {
    vector<int> result;
    if (raw.size() <= 2) return result;
    raw = raw.substr(1, raw.size() - 2);
    stringstream ss(raw);
    string part;
    while (getline(ss, part, ',')) result.push_back(stoi(part));
    return result;
}

int main() {
    string line;
    getline(cin, line);
    vector<int> height = parseIntArray(line);
    int left = 0;
    int right = static_cast<int>(height.size()) - 1;
    int best = 0;

    while (left < right) {
        best = max(best, min(height[left], height[right]) * (right - left));
        if (height[left] < height[right]) left++;
        else right--;
    }

    cout << best << endl;
    return 0;
}
"""


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
        "starter_code_json": {lang: starter_two_sum(lang) for lang in LANGUAGES},
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
        "starter_code_json": {lang: starter_stock(lang) for lang in LANGUAGES},
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
        "starter_code_json": {lang: starter_move_zeroes(lang) for lang in LANGUAGES},
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
        "starter_code_json": {lang: starter_product_except_self(lang) for lang in LANGUAGES},
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
        "starter_code_json": {lang: starter_valid_palindrome(lang) for lang in LANGUAGES},
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
        "starter_code_json": {lang: starter_two_sum_sorted(lang) for lang in LANGUAGES},
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
        "starter_code_json": {lang: starter_longest_substring(lang) for lang in LANGUAGES},
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
        "starter_code_json": {lang: starter_max_average(lang) for lang in LANGUAGES},
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
        "starter_code_json": {lang: starter_binary_search(lang) for lang in LANGUAGES},
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
        "starter_code_json": {lang: starter_search_insert(lang) for lang in LANGUAGES},
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
        "starter_code_json": {lang: starter_reverse_string(lang) for lang in LANGUAGES},
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
        "starter_code_json": {lang: starter_valid_anagram(lang) for lang in LANGUAGES},
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
        "starter_code_json": {lang: starter_climbing_stairs(lang) for lang in LANGUAGES},
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
        "starter_code_json": {lang: starter_max_subarray(lang) for lang in LANGUAGES},
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
        "starter_code_json": {lang: starter_container(lang) for lang in LANGUAGES},
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


def upsert_problem(db, payload: Dict, pattern_map: Dict[str, int], order_index: int) -> Problem:
    from app.models.problem import Problem

    problem = db.query(Problem).filter(Problem.slug == payload["slug"]).first()
    if not problem:
        problem = Problem(slug=payload["slug"])
        db.add(problem)
        db.flush()

    problem.pattern_id = pattern_map[payload["pattern_slug"]]
    problem.title = payload["title"]
    problem.difficulty = payload["difficulty"]
    problem.short_description = payload["short_description"]
    problem.statement = payload["statement"]
    problem.constraints_text = payload["constraints_text"]
    problem.examples_json = payload["examples_json"]
    problem.starter_code_json = payload["starter_code_json"]
    problem.reference_solution_json = None
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

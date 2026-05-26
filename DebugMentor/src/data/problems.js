// src/data/problems.js

export const predefinedProblems = [
  {
    id: "find_max",
    title: "Find Maximum Element",
    description: "Write a function `find_max(arr)` that takes an array of integers and returns the maximum integer. If the array is empty, return None or null. The array may contain negative numbers.",
    starter: {
      python: "def find_max(arr):\n    # Write your code here\n    pass",
      javascript: "function findMax(arr) {\n    // Write your code here\n}",
      cpp: "int findMax(vector<int>& arr) {\n    // Write your code here\n}",
      java: "public static int findMax(int[] arr) {\n    // Write your code here\n}"
    }
  },
  {
    id: "factorial",
    title: "Compute Factorial",
    description: "Write a function `factorial(n)` that returns the factorial of n. n will be a non-negative integer. Example: factorial(5) should return 120. Make sure to handle edge cases like n=0.",
    starter: {
      python: "def factorial(n):\n    # Write your code here\n    pass",
      javascript: "function factorial(n) {\n    // Write your code here\n}",
      cpp: "int factorial(int n) {\n    // Write your code here\n}",
      java: "public static int factorial(int n) {\n    // Write your code here\n}"
    }
  },
  {
    id: "bubble_sort",
    title: "Sort Array",
    description: "Write a function `bubble_sort(arr)` that sorts an array of integers in ascending order. You should return the sorted array. Do not use built-in sort functions; implement sorting manually.",
    starter: {
      python: "def bubble_sort(arr):\n    # Write your code here\n    pass",
      javascript: "function bubbleSort(arr) {\n    // Write your code here\n}",
      cpp: "vector<int> bubbleSort(vector<int> arr) {\n    // Write your code here\n}",
      java: "public static int[] bubbleSort(int[] arr) {\n    // Write your code here\n}"
    }
  }
];

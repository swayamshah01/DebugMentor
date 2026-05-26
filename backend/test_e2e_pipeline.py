"""Quick E2E test of the Phase 2 /submit pipeline."""
import requests
import json

TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3IiwidXNlcm5hbWUiOiJwaXBldGVzdCIsImV4cCI6MTc3NjQ1MjM4NX0.aAxYU4YCwBn4gosNUxr3WruichXgs2zRSJ9bKKd-Jas'

# Code with a known off-by-one bug
code = """def find_max(arr):
    max_val = arr[0]
    for i in range(len(arr) - 1):
        if arr[i] > max_val:
            max_val = arr[i]
    return max_val"""

r = requests.post(
    'http://localhost:8000/api/submit',
    json={'code': code, 'language': 'python', 'test_input': ''},
    headers={'Authorization': f'Bearer {TOKEN}'},
    timeout=30,
)
data = r.json()
print(f"STATUS: {r.status_code}")
print(f"submission_id: {data.get('id')}")
print(f"status: {data.get('status')}")
print()

print("=== AST ISSUES ===")
for issue in (data.get('ast_issues') or []):
    print(f"  [{issue['severity']}] {issue['title']} (line {issue['line']})")
    print(f"    {issue['message']}")
print()

print("=== FAILURE REPORT ===")
fr = data.get('failure_report', {})
print(f"  Total: {fr.get('total')}, Passed: {fr.get('passed')}, Failed: {fr.get('failed')}")
print(f"  Dominant: {fr.get('dominant_failure_type')}")
print(f"  Summary: {fr.get('failure_summary')}")
print()

print("=== TEST RESULTS ===")
for tr in (fr.get('test_results') or []):
    status_emoji = 'PASS' if tr['status'] == 'PASSED' else 'FAIL'
    actual = (tr.get('actual_output') or '')[:40]
    print(f"  [{status_emoji}] {tr['label']:20s}  input={tr['input']:25s}  output={actual:40s}  status={tr['status']}")
print()

print(f"hints: {data.get('hints')}")

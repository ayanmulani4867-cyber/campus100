import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:5000"

def request(path, method="GET", data=None, token=None):
    url = BASE_URL + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Session-Token"] = token
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            return resp.status, content
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        return e.code, content

def run_tests():
    print("=" * 70)
    print("TESTING ADMIN NAVIGATION, ROUTES & MODULE INTEGRATION")
    print("=" * 70)

    # 1. Admin Login
    status, body = request("/api/auth/login", "POST", {
        "email": "admin@campus.edu",
        "password": "campus@123"
    })
    assert status == 200, f"Admin login failed: {body}"
    res = json.loads(body)
    admin_token = res["sessionToken"]
    print("[PASS] Admin logged in successfully.")

    # 2. Check User Directory APIs
    status, body = request("/api/students", "GET", token=admin_token)
    assert status == 200, f"Failed to get students: {body}"
    students_res = json.loads(body)
    assert students_res["success"], "Students API not success"
    print(f"[PASS] /api/students returned {len(students_res['data'])} student records.")

    status, body = request("/api/faculty", "GET", token=admin_token)
    assert status == 200, f"Failed to get faculty: {body}"
    faculty_res = json.loads(body)
    assert faculty_res["success"], "Faculty API not success"
    print(f"[PASS] /api/faculty returned {len(faculty_res['data'])} faculty records.")

    # 3. Check Results API
    status, body = request("/api/results", "GET", token=admin_token)
    assert status == 200, f"Failed to get results: {body}"
    results_res = json.loads(body)
    assert results_res["success"], "Results API not success"
    print(f"[PASS] /api/results returned {len(results_res['data'])} result records.")

    # 4. Check Materials API
    status, body = request("/api/materials", "GET", token=admin_token)
    assert status == 200, f"Failed to get materials: {body}"
    materials_res = json.loads(body)
    assert materials_res["success"], "Materials API not success"
    print(f"[PASS] /api/materials returned {len(materials_res['data'])} study material items.")

    # 5. Check HTML Pages and Element IDs
    status, html_users = request("/users.html", "GET")
    assert status == 200, "users.html failed to load"
    assert 'id="usersDirectoryTable"' in html_users, "usersDirectoryTable missing in users.html"
    assert 'id="usersTableBody"' in html_users, "usersTableBody missing in users.html"
    assert 'id="adminResultsTableBody"' not in html_users, "adminResultsTableBody wrongly in users.html"
    assert 'id="materialsTableBody"' not in html_users, "materialsTableBody wrongly in users.html"
    print("[PASS] users.html has correct dedicated table IDs.")

    status, html_results = request("/results.html", "GET")
    assert status == 200, "results.html failed to load"
    assert 'id="adminResultView"' in html_results, "adminResultView missing in results.html"
    assert 'id="adminBatchResultsTable"' in html_results, "adminBatchResultsTable missing in results.html"
    assert 'id="adminResultsTableBody"' in html_results, "adminResultsTableBody missing in results.html"
    assert 'id="usersTableBody"' not in html_results, "usersTableBody wrongly in results.html"
    assert 'id="materialsTableBody"' not in html_results, "materialsTableBody wrongly in results.html"
    print("[PASS] results.html has correct dedicated table IDs (no user table collision).")

    status, html_materials = request("/materials.html", "GET")
    assert status == 200, "materials.html failed to load"
    assert 'id="materialsTable"' in html_materials, "materialsTable missing in materials.html"
    assert 'id="materialsTableBody"' in html_materials, "materialsTableBody missing in materials.html"
    assert 'id="usersTableBody"' not in html_materials, "usersTableBody wrongly in materials.html"
    assert 'id="adminResultsTableBody"' not in html_materials, "adminResultsTableBody wrongly in materials.html"
    print("[PASS] materials.html has correct dedicated table IDs (no user table collision).")

    # 6. Test Publish/Unpublish toggle endpoint
    if results_res["data"]:
        test_r = results_res["data"][0]
        r_id = test_r["id"]
        new_status = not test_r["isPublished"]
        status, body = request(f"/api/results/{r_id}/publish", "PUT", {"isPublished": new_status}, token=admin_token)
        assert status == 200, f"Toggle publish failed: {body}"
        pub_res = json.loads(body)
        assert pub_res["data"]["isPublished"] == new_status, "Publish state did not toggle"
        # Toggle back
        request(f"/api/results/{r_id}/publish", "PUT", {"isPublished": test_r["isPublished"]}, token=admin_token)
        print(f"[PASS] /api/results/{r_id}/publish successfully toggled publish status.")

    print("=" * 70)
    print("ALL ADMIN NAVIGATION & ROUTING TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()

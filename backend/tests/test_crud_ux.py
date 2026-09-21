import json
import urllib.request
import urllib.parse

BASE_URL = "http://127.0.0.1:5000"

def make_request(path, method="GET", data=None, headers=None, content_type="application/json"):
    url = f"{BASE_URL}{path}"
    req_headers = headers.copy() if headers else {}
    req_data = None

    if data is not None:
        if isinstance(data, (dict, list)):
            req_data = json.dumps(data).encode("utf-8")
            req_headers["Content-Type"] = content_type
        elif isinstance(data, bytes):
            req_data = data
            req_headers["Content-Type"] = content_type

    req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            return response.status, json.loads(res_body) if res_body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            parsed = json.loads(err_body)
        except Exception:
            parsed = {"raw": err_body}
        return e.code, parsed

def login(email, password="campus@123", role=None):
    payload = {"email": email, "password": password}
    if role:
        payload["role"] = role
    status, body = make_request("/api/auth/login", method="POST", data=payload)
    assert status == 200, f"Login failed ({status}): {body}"
    token = body.get("sessionToken") or body.get("session_token")
    return {"X-Session-Token": token}

def test_all_crud():
    print("=== 1. Authenticating as Admin ===")
    admin_headers = login("admin@campus.edu", "campus@123", role="admin")
    print("Admin authenticated.")

    print("\n=== 2. Add Student ===")
    add_stu_payload = {
        "name": "Test Student UX",
        "email": "test_ux_student@campus.edu",
        "phone": "9876501234",
        "department": "Computer Science & Engineering",
        "year": "3rd Year",
        "semester": "6",
        "division": "B",
        "prn": "STU_UX_9999"
    }
    status, res = make_request("/api/students", method="POST", data=add_stu_payload, headers=admin_headers)
    assert status == 201, f"Add student failed ({status}): {res}"
    stu_data = res.get("data", {})
    stu_code = stu_data.get("id") or "STU_UX_9999"
    print(f"Created student: {stu_data.get('name')} (ID: {stu_code})")

    print("\n=== 3. Edit Student ===")
    edit_stu_payload = {
        "name": "Test Student UX Updated",
        "phone": "9876509999",
        "year": "3rd Year",
        "semester": "6",
        "division": "A"
    }
    status, res = make_request(f"/api/students/{stu_code}", method="PUT", data=edit_stu_payload, headers=admin_headers)
    assert status == 200, f"Edit student failed ({status}): {res}"
    print("Student edited successfully.")

    print("\n=== 4. Delete Student ===")
    status, res = make_request(f"/api/students/{stu_code}", method="DELETE", headers=admin_headers)
    assert status == 200, f"Delete student failed ({status}): {res}"
    print("Student deleted successfully.")

    print("\n=== 5. Add Faculty Member ===")
    add_fac_payload = {
        "name": "Prof. Test Faculty UX",
        "email": "test_ux_faculty@campus.edu",
        "phone": "9876505678",
        "department": "Computer Science & Engineering",
        "designation": "Associate Professor",
        "facultyId": "FAC_UX_888",
        "assignments": [
            {"subject": "DBMS", "year": "3rd Year", "semester": "5", "divisions": ["A", "B"]}
        ]
    }
    status, res = make_request("/api/faculty", method="POST", data=add_fac_payload, headers=admin_headers)
    assert status == 201, f"Add faculty failed ({status}): {res}"
    fac_data = res.get("data", {})
    fac_code = fac_data.get("id") or "FAC_UX_888"
    print(f"Created faculty: {fac_data.get('name')} (ID: {fac_code})")

    print("\n=== 6. Edit Faculty Member ===")
    edit_fac_payload = {
        "name": "Prof. Test Faculty UX Senior",
        "phone": "9876508888",
        "designation": "Professor"
    }
    status, res = make_request(f"/api/faculty/{fac_code}", method="PUT", data=edit_fac_payload, headers=admin_headers)
    assert status == 200, f"Edit faculty failed ({status}): {res}"
    print("Faculty edited successfully.")

    print("\n=== 7. Delete Faculty Member ===")
    status, res = make_request(f"/api/faculty/{fac_code}", method="DELETE", headers=admin_headers)
    assert status == 200, f"Delete faculty failed ({status}): {res}"
    print("Faculty deleted successfully.")

    print("\n=== 8. Authenticating as Faculty ===")
    faculty_headers = login("anita.sen@campus.edu", "campus@123", role="faculty")
    print("Faculty authenticated.")

    print("\n=== 9. Record Marks / Exam Result ===")
    marks_payload = {
        "studentId": "STU2024001",
        "courseCode": "CS601",
        "marks": 82
    }
    status, res = make_request("/api/results", method="POST", data=marks_payload, headers=faculty_headers)
    assert status in (200, 201), f"Record marks failed ({status}): {res}"
    result_data = res.get("data", {})
    result_id = result_data.get("id")
    print(f"Marks saved: Total={result_data.get('total')}, Grade={result_data.get('grade')}, ResultID={result_id}")

    print("\n=== 10. Admin Publish / Unpublish Result ===")
    status, res = make_request(f"/api/results/{result_id}/publish", method="PUT", data={"isPublished": True}, headers=admin_headers)
    assert status == 200, f"Publish failed ({status}): {res}"
    print("Published scorecard successfully.")
    status, res = make_request(f"/api/results/{result_id}/publish", method="PUT", data={"isPublished": False}, headers=admin_headers)
    assert status == 200, f"Unpublish failed ({status}): {res}"
    print("Unpublished scorecard successfully.")

    print("\n=== 11. Upload Study Material (Multipart) ===")
    boundary = "----WebKitFormBoundaryUXTest7MA4YWxkTrZu0gW"
    body_parts = []
    
    def add_field(name, value):
        body_parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode("utf-8"))
    
    add_field("title", "Unit 4 Advanced Indexing Notes")
    add_field("category", "Lecture Notes")
    add_field("courseCode", "CS601")
    add_field("division", "All")

    file_content = b"%PDF-1.4 test study material content"
    body_parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"Unit4_Indexing.pdf\"\r\nContent-Type: application/pdf\r\n\r\n".encode("utf-8")
        + file_content + b"\r\n"
    )
    body_parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    multipart_body = b"".join(body_parts)

    status, res = make_request("/api/materials", method="POST", data=multipart_body, headers=faculty_headers, content_type=f"multipart/form-data; boundary={boundary}")
    assert status == 201, f"Upload material failed ({status}): {res}"
    mat_data = res.get("data", {})
    mat_id = mat_data.get("id")
    print(f"Uploaded study material: {mat_data.get('title')} (ID: {mat_id})")

    print("\n=== 12. Delete Study Material ===")
    status, res = make_request(f"/api/materials/{mat_id}", method="DELETE", headers=faculty_headers)
    assert status == 200, f"Delete material failed ({status}): {res}"
    print("Deleted study material successfully.")

    print("\n=== 13. Save Roll-Call Classroom Attendance ===")
    attend_payload = {
        "courseCode": "CS601",
        "division": "A",
        "records": [
            {"studentId": "STU2024001", "status": "present"},
            {"studentId": "STU2024002", "status": "absent"}
        ]
    }
    status, res = make_request("/api/attendance/roll-call", method="POST", data=attend_payload, headers=faculty_headers)
    assert status == 200, f"Roll call failed ({status}): {res}"
    print(f"Attendance saved: {res.get('message')}")

    print("\n=== 14. Create Notice ===")
    notice_payload = {
        "title": "UX Evaluation Notice",
        "category": "Academic",
        "body": "Campus Connect interactive UX enhancements are now active."
    }
    status, res = make_request("/api/notices", method="POST", data=notice_payload, headers=faculty_headers)
    assert status == 201, f"Create notice failed ({status}): {res}"
    notice_data = res.get("data", {})
    notice_id = notice_data.get("id")
    print(f"Created notice: {notice_data.get('title')} (ID: {notice_id})")

    print("\n=== 15. Delete Notice ===")
    status, res = make_request(f"/api/notices/{notice_id}", method="DELETE", headers=faculty_headers)
    assert status == 200, f"Delete notice failed ({status}): {res}"
    print("Deleted notice successfully.")

    print("\n=== 16. Create Event ===")
    event_payload = {
        "title": "NextGen AI & Cloud Workshop",
        "date": "2026-04-10",
        "category": "Workshop",
        "location": "Seminar Hall A • 10:00 AM",
        "description": "Comprehensive workshop on scalable web systems."
    }
    status, res = make_request("/api/events", method="POST", data=event_payload, headers=faculty_headers)
    assert status == 201, f"Create event failed ({status}): {res}"
    event_data = res.get("data", {})
    event_id = event_data.get("id")
    print(f"Created event: {event_data.get('title')} (ID: {event_id})")

    print("\n=== 17. Delete Event ===")
    status, res = make_request(f"/api/events/{event_id}", method="DELETE", headers=faculty_headers)
    assert status == 200, f"Delete event failed ({status}): {res}"
    print("Deleted event successfully.")

    print("\n[SUCCESS] ALL 17 CRUD / ACTION OPERATIONS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    test_all_crud()

from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "vit_timetable_secret_key"

# ---------------- DATABASE CONNECTION ----------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root123",
        database="timetable"
    )

# ---------------- LOGIN PAGE ----------------
@app.route('/')
def login_page():
    return render_template('login.html')

# ---------------- LOGIN HANDLER ----------------
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM users
        WHERE username=%s AND password=%s AND role=%s
    """, (username, password, role))

    user = cursor.fetchone()
    conn.close()

    if not user:
        return "Invalid credentials"

    session['role'] = role
    session['linked_id'] = user['linked_id']

    if role == 'admin':
        return redirect('/admin-dashboard')
    elif role == 'faculty':
        return redirect('/faculty-dashboard')
    else:
        return redirect('/student-dashboard')

# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin-dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM class")
    classes = cursor.fetchall()

    cursor.execute("SELECT * FROM subject")
    subjects = cursor.fetchall()

    cursor.execute("SELECT * FROM faculty")
    faculties = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        classes=classes,
        subjects=subjects,
        faculties=faculties
    )

# ---------------- ADD FACULTY ----------------
@app.route('/add-faculty', methods=['POST'])
def add_faculty():
    if session.get('role') != 'admin':
        return redirect('/')

    name = request.form['faculty_name']
    max_day = request.form['max_hours_per_day']
    max_week = request.form['max_hours_per_week']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO faculty (faculty_name, max_hours_per_day, max_hours_per_week, dept_id)
        VALUES (%s, %s, %s, 1)
    """, (name, max_day, max_week))

    conn.commit()
    conn.close()

    return redirect('/admin-dashboard')

# ---------------- ADD CLASS ----------------
@app.route('/add-class', methods=['POST'])
def add_class():
    if session.get('role') != 'admin':
        return redirect('/')

    semester = request.form['semester']
    division = request.form['division']
    shift_id = request.form['student_shift_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO class (semester, division, student_shift_id, dept_id)
        VALUES (%s, %s, %s, 1)
    """, (semester, division, shift_id))

    conn.commit()
    conn.close()

    return redirect('/admin-dashboard')

# ---------------- ADD SUBJECT ----------------
@app.route('/add-subject', methods=['POST'])
def add_subject():
    if session.get('role') != 'admin':
        return redirect('/')

    name = request.form['subject_name']
    semester = request.form['semester']
    hours = request.form['hours_per_week']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO subject (subject_name, semester, hours_per_week, dept_id)
        VALUES (%s, %s, %s, 1)
    """, (name, semester, hours))

    conn.commit()
    conn.close()

    return redirect('/admin-dashboard')

# ---------------- ASSIGN FACULTY ----------------
@app.route('/assign-faculty', methods=['POST'])
def assign_faculty():
    if session.get('role') != 'admin':
        return redirect('/')

    class_id = request.form['class_id']
    subject_id = request.form['subject_id']
    faculty_id = request.form['faculty_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO class_subject_faculty (class_id, subject_id, faculty_id)
        VALUES (%s, %s, %s)
    """, (class_id, subject_id, faculty_id))

    conn.commit()
    conn.close()

    return redirect('/admin-dashboard')

# ---------------- GENERATE TIMETABLE ----------------
@app.route('/generate-timetable')
def generate_timetable():
    if session.get('role') != 'admin':
        return redirect('/')

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Clear old timetable
    cursor.execute("DELETE FROM weekly_timetable")

    cursor.execute("SELECT * FROM class")
    classes = cursor.fetchall()

    # Track faculty clashes → (day, slot_id, faculty_id)
    faculty_busy = set()

    # Track subject per day per class → (class_id, subject_id, day)
    subject_day_used = set()

    for cls in classes:
        class_id = cls['class_id']
        shift_id = cls['student_shift_id']

        # Get slots for shift
        cursor.execute("""
            SELECT slot_id
            FROM time_slot
            WHERE student_shift_id = %s
            ORDER BY start_time
        """, (shift_id,))
        slots = [s['slot_id'] for s in cursor.fetchall()]

        # Get subject–faculty mappings
        cursor.execute("""
            SELECT csf.subject_id, csf.faculty_id, s.hours_per_week
            FROM class_subject_faculty csf
            JOIN subject s ON csf.subject_id = s.subject_id
            WHERE csf.class_id = %s
        """, (class_id,))
        mappings = cursor.fetchall()

        # Expand subjects by hours/week
        expanded = []
        for m in mappings:
            expanded.extend(
                [(m['subject_id'], m['faculty_id'])] * m['hours_per_week']
            )

        day_i = 0
        slot_i = 0

        for subject_id, faculty_id in expanded:
            placed = False

            for _ in range(len(DAYS) * len(slots)):
                day = DAYS[day_i]
                slot = slots[slot_i]

                faculty_key = (day, slot, faculty_id)
                subject_key = (class_id, subject_id, day)

                # ✅ BOTH constraints checked here
                if faculty_key not in faculty_busy and subject_key not in subject_day_used:
                    cursor.execute("""
                        INSERT INTO weekly_timetable
                        (class_id, subject_id, faculty_id, slot_id, day)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (class_id, subject_id, faculty_id, slot, day))

                    faculty_busy.add(faculty_key)
                    subject_day_used.add(subject_key)
                    placed = True
                    break

                # Move to next slot/day
                slot_i = (slot_i + 1) % len(slots)
                if slot_i == 0:
                    day_i = (day_i + 1) % len(DAYS)

            if not placed:
                conn.rollback()
                conn.close()
                return "Timetable generation failed due to constraints"

            # Move forward after successful placement
            slot_i = (slot_i + 1) % len(slots)
            if slot_i == 0:
                day_i = (day_i + 1) % len(DAYS)

    conn.commit()
    conn.close()

    return redirect('/admin-dashboard')


# ---------------- VIEW TIMETABLE ----------------
@app.route('/view-timetable/<division>')
def view_timetable(division):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT wt.day, ts.slot_name, s.subject_name, f.faculty_name
        FROM weekly_timetable wt
        JOIN subject s ON wt.subject_id = s.subject_id
        JOIN faculty f ON wt.faculty_id = f.faculty_id
        JOIN time_slot ts ON wt.slot_id = ts.slot_id
        JOIN class c ON wt.class_id = c.class_id
        WHERE c.division = %s
        ORDER BY FIELD(wt.day,'Monday','Tuesday','Wednesday','Thursday','Friday'),
                 ts.start_time
    """, (division,))

    rows = cursor.fetchall()
    conn.close()

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    slots = sorted({r['slot_name'] for r in rows})

    timetable = {d: {s: "" for s in slots} for d in days}

    for r in rows:
        timetable[r['day']][r['slot_name']] = f"{r['subject_name']}<br><small>{r['faculty_name']}</small>"

    return render_template(
        "view_timetable.html",
        division=division,
        slots=slots,
        timetable=timetable
    )

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- DELETE CLASS ----------------
@app.route('/delete-class/<int:class_id>')
def delete_class(class_id):
    if session.get('role') != 'admin':
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM class_subject_faculty WHERE class_id=%s", (class_id,))
    cursor.execute("DELETE FROM weekly_timetable WHERE class_id=%s", (class_id,))
    cursor.execute("DELETE FROM class WHERE class_id=%s", (class_id,))

    conn.commit()
    conn.close()

    return redirect('/admin-dashboard')

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)

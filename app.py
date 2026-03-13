from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
import json
import random
from collections import defaultdict

# OR-Tools CP-SAT — install with: pip install ortools
try:
    from ortools.sat.python import cp_model
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False

app = Flask(__name__)
app.secret_key = "vit_timetable_secret_key"


# ================================================================
#  DATABASE CONNECTION
# ================================================================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root123",
        database="timetable"
    )


# ================================================================
#  LOGIN PAGE
# ================================================================
@app.route('/')
def login_page():
    return render_template('login.html')


# ================================================================
#  LOGIN HANDLER
# ================================================================
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    role     = request.form['role']

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM users
        WHERE username=%s AND password=%s AND role=%s
    """, (username, password, role))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return "Invalid credentials. <a href='/'>Go back</a>"

    session['role']      = role
    session['linked_id'] = user['linked_id']

    if role == 'admin':
        return redirect('/admin-dashboard')
    elif role == 'faculty':
        return redirect('/faculty-dashboard')
    else:
        return redirect('/student-dashboard')


# ================================================================
#  ADMIN DASHBOARD
# ================================================================
@app.route('/admin-dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/')

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM class ORDER BY semester, division")
    classes = cursor.fetchall()

    cursor.execute("SELECT * FROM subject ORDER BY semester, subject_name")
    subjects = cursor.fetchall()

    cursor.execute("SELECT * FROM faculty ORDER BY faculty_name")
    faculties = cursor.fetchall()

    cursor.execute("""
        SELECT class_id, COUNT(*) as subject_count
        FROM class_subject_faculty
        GROUP BY class_id
    """)
    assignment_counts = {r['class_id']: r['subject_count'] for r in cursor.fetchall()}

    cursor.execute("""
        SELECT class_id, COUNT(*) as entry_count
        FROM weekly_timetable
        GROUP BY class_id
    """)
    tt_counts = {r['class_id']: r['entry_count'] for r in cursor.fetchall()}

    conn.close()
    return render_template('admin_dashboard.html',
                           classes=classes,
                           subjects=subjects,
                           faculties=faculties,
                           assignment_counts=assignment_counts,
                           tt_counts=tt_counts)


# ================================================================
#  ADD FACULTY
# ================================================================
@app.route('/add-faculty', methods=['POST'])
def add_faculty():
    if session.get('role') != 'admin':
        return redirect('/')

    name     = request.form['faculty_name'].strip()
    max_day  = int(request.form.get('max_hours_per_day', 3))
    max_week = int(request.form.get('max_hours_per_week', 15))
    dept_id  = int(request.form.get('dept_id', 1))

    if not name:
        flash("⚠ Faculty name cannot be empty.", "error")
        return redirect('/admin-dashboard')

    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO faculty (faculty_name, max_hours_per_day, max_hours_per_week, dept_id)
        VALUES (%s, %s, %s, %s)
    """, (name, max_day, max_week, dept_id))
    conn.commit()
    conn.close()
    flash(f"✓ Faculty '{name}' added successfully.", "success")
    return redirect('/admin-dashboard')


# ================================================================
#  EDIT FACULTY
# ================================================================
@app.route('/edit-faculty/<int:faculty_id>', methods=['POST'])
def edit_faculty(faculty_id):
    if session.get('role') != 'admin':
        return redirect('/')

    name     = request.form['faculty_name'].strip()
    max_day  = int(request.form.get('max_hours_per_day', 3))
    max_week = int(request.form.get('max_hours_per_week', 15))

    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE faculty
        SET faculty_name=%s, max_hours_per_day=%s, max_hours_per_week=%s
        WHERE faculty_id = %s
    """, (name, max_day, max_week, faculty_id))
    conn.commit()
    conn.close()
    flash("✓ Faculty updated.", "success")
    return redirect('/admin-dashboard')


# ================================================================
#  DELETE FACULTY
# ================================================================
@app.route('/delete-faculty/<int:faculty_id>')
def delete_faculty(faculty_id):
    if session.get('role') != 'admin':
        return redirect('/')

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT COUNT(*) as cnt FROM weekly_timetable WHERE faculty_id = %s",
        (faculty_id,)
    )
    if cursor.fetchone()['cnt'] > 0:
        conn.close()
        flash("⚠ Cannot delete faculty with existing timetable entries. "
              "Clear their timetable entries first.", "error")
        return redirect('/admin-dashboard')

    cursor.execute("DELETE FROM class_subject_faculty WHERE faculty_id = %s", (faculty_id,))
    cursor.execute("DELETE FROM faculty WHERE faculty_id = %s", (faculty_id,))
    conn.commit()
    conn.close()
    flash("✓ Faculty deleted.", "success")
    return redirect('/admin-dashboard')


# ================================================================
#  ADD CLASS
# ================================================================
@app.route('/add-class', methods=['POST'])
def add_class():
    if session.get('role') != 'admin':
        return redirect('/')

    semester = request.form['semester'].strip()
    division = request.form['division'].strip().upper()
    shift_id = int(request.form['student_shift_id'])
    dept_id  = int(request.form.get('dept_id', 1))

    if not semester or not division:
        flash("⚠ Semester and Division cannot be empty.", "error")
        return redirect('/admin-dashboard')

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) as cnt FROM class
        WHERE semester=%s AND division=%s AND dept_id=%s
    """, (semester, division, dept_id))
    if cursor.fetchone()['cnt'] > 0:
        conn.close()
        flash(f"⚠ Class Semester {semester} Division {division} already exists.", "error")
        return redirect('/admin-dashboard')

    cursor.execute("""
        INSERT INTO class (semester, division, student_shift_id, dept_id)
        VALUES (%s, %s, %s, %s)
    """, (semester, division, shift_id, dept_id))
    conn.commit()
    new_class_id = cursor.lastrowid
    conn.close()

    flash(f"✓ Class Sem {semester} Div {division} added (ID: {new_class_id}).", "success")
    return redirect('/admin-dashboard')


# ================================================================
#  EDIT CLASS
# ================================================================
@app.route('/edit-class/<int:class_id>', methods=['POST'])
def edit_class(class_id):
    if session.get('role') != 'admin':
        return redirect('/')

    semester = request.form['semester'].strip()
    division = request.form['division'].strip().upper()
    shift_id = int(request.form['student_shift_id'])

    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE class SET semester=%s, division=%s, student_shift_id=%s
        WHERE class_id = %s
    """, (semester, division, shift_id, class_id))
    conn.commit()
    conn.close()
    flash("✓ Class updated.", "success")
    return redirect('/admin-dashboard')


# ================================================================
#  DUPLICATE CLASS
# ================================================================
@app.route('/duplicate-class/<int:class_id>', methods=['POST'])
def duplicate_class(class_id):
    if session.get('role') != 'admin':
        return redirect('/')

    new_division = request.form['new_division'].strip().upper()
    if not new_division:
        flash("⚠ Please provide a division name for the duplicate.", "error")
        return redirect('/admin-dashboard')

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM class WHERE class_id = %s", (class_id,))
    src = cursor.fetchone()
    if not src:
        conn.close()
        flash("⚠ Source class not found.", "error")
        return redirect('/admin-dashboard')

    cursor.execute("""
        SELECT COUNT(*) as cnt FROM class
        WHERE semester=%s AND division=%s AND dept_id=%s
    """, (src['semester'], new_division, src['dept_id']))
    if cursor.fetchone()['cnt'] > 0:
        conn.close()
        flash(f"⚠ Division {new_division} already exists for Semester {src['semester']}.", "error")
        return redirect('/admin-dashboard')

    cursor.execute("""
        INSERT INTO class (semester, division, student_shift_id, dept_id)
        VALUES (%s, %s, %s, %s)
    """, (src['semester'], new_division, src['student_shift_id'], src['dept_id']))
    new_class_id = cursor.lastrowid

    cursor.execute("""
        SELECT subject_id, faculty_id FROM class_subject_faculty WHERE class_id = %s
    """, (class_id,))
    for row in cursor.fetchall():
        cursor.execute("""
            INSERT INTO class_subject_faculty (class_id, subject_id, faculty_id)
            VALUES (%s, %s, %s)
        """, (new_class_id, row['subject_id'], row['faculty_id']))

    conn.commit()
    conn.close()
    flash(f"✓ Class duplicated to Division {new_division} (ID: {new_class_id}). "
          "Assignments copied. Generate timetable separately.", "success")
    return redirect('/admin-dashboard')


# ================================================================
#  ADD SUBJECT
# ================================================================
@app.route('/add-subject', methods=['POST'])
def add_subject():
    if session.get('role') != 'admin':
        return redirect('/')

    name     = request.form['subject_name'].strip()
    semester = request.form['semester'].strip()
    hours    = int(request.form.get('hours_per_week', 3))
    dept_id  = int(request.form.get('dept_id', 1))

    if not name or not semester:
        flash("⚠ Subject name and semester are required.", "error")
        return redirect('/admin-dashboard')

    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO subject (subject_name, semester, hours_per_week, dept_id)
        VALUES (%s, %s, %s, %s)
    """, (name, semester, hours, dept_id))
    conn.commit()
    conn.close()
    flash(f"✓ Subject '{name}' added.", "success")
    return redirect('/admin-dashboard')


# ================================================================
#  DELETE SUBJECT
# ================================================================
@app.route('/delete-subject/<int:subject_id>')
def delete_subject(subject_id):
    if session.get('role') != 'admin':
        return redirect('/')

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT COUNT(*) as cnt FROM weekly_timetable WHERE subject_id = %s",
        (subject_id,)
    )
    if cursor.fetchone()['cnt'] > 0:
        conn.close()
        flash("⚠ Cannot delete subject with existing timetable entries. "
              "Clear timetables first.", "error")
        return redirect('/admin-dashboard')

    cursor.execute("DELETE FROM class_subject_faculty WHERE subject_id = %s", (subject_id,))
    cursor.execute("DELETE FROM subject WHERE subject_id = %s", (subject_id,))
    conn.commit()
    conn.close()
    flash("✓ Subject deleted.", "success")
    return redirect('/admin-dashboard')


# ================================================================
#  ASSIGN FACULTY TO SUBJECT
# ================================================================
@app.route('/assign-faculty', methods=['POST'])
def assign_faculty():
    if session.get('role') != 'admin':
        return redirect('/')

    class_id   = int(request.form['class_id'])
    subject_id = int(request.form['subject_id'])
    faculty_id = int(request.form['faculty_id'])

    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO class_subject_faculty (class_id, subject_id, faculty_id)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE faculty_id = VALUES(faculty_id)
    """, (class_id, subject_id, faculty_id))
    conn.commit()
    conn.close()
    flash("✓ Faculty assigned to subject.", "success")
    return redirect('/admin-dashboard')


# ================================================================
#  REMOVE FACULTY ASSIGNMENT
# ================================================================
@app.route('/remove-assignment', methods=['POST'])
def remove_assignment():
    if session.get('role') != 'admin':
        return redirect('/')

    class_id   = int(request.form['class_id'])
    subject_id = int(request.form['subject_id'])

    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM class_subject_faculty
        WHERE class_id=%s AND subject_id=%s
    """, (class_id, subject_id))
    conn.commit()
    conn.close()
    flash("✓ Assignment removed.", "success")
    return redirect('/admin-dashboard')


# ================================================================
#  DELETE CLASS
# ================================================================
@app.route('/delete-class/<int:class_id>')
def delete_class(class_id):
    if session.get('role') != 'admin':
        return redirect('/')

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT semester, division FROM class WHERE class_id = %s", (class_id,))
    cls   = cursor.fetchone()
    label = f"Sem {cls['semester']} Div {cls['division']}" if cls else str(class_id)

    # ON DELETE CASCADE handles weekly_timetable + class_subject_faculty automatically
    cursor.execute("DELETE FROM weekly_timetable      WHERE class_id = %s", (class_id,))
    cursor.execute("DELETE FROM class_subject_faculty WHERE class_id = %s", (class_id,))
    cursor.execute("DELETE FROM class                 WHERE class_id = %s", (class_id,))
    conn.commit()
    conn.close()
    flash(f"✓ Class {label} and all its timetable data deleted.", "success")
    return redirect('/admin-dashboard')


# ================================================================
#  GENERATE OPTIONS PAGE
# ================================================================
@app.route('/generate-options')
def generate_options():
    if session.get('role') != 'admin':
        return redirect('/')

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM class ORDER BY semester, division")
    classes = cursor.fetchall()
    conn.close()
    return render_template('generate_options.html', classes=classes)


# ================================================================
#  ILP SCHEDULER — Google OR-Tools CP-SAT
#
#  Integer Linear Programming formulation:
#
#  DECISION VARIABLE:
#    x[s, d, t] = 1  if subject s is assigned to day d, slot t
#                 0  otherwise
#    where s encodes (subject_id, faculty_id) pair
#
#  HARD CONSTRAINTS (must all be satisfied — infeasible otherwise):
#    C1. Coverage     : sum over (d,t) of x[s,d,t] == hours_per_week[s]
#                       Every subject gets exactly the required lecture count.
#    C2. No slot clash: sum over s of x[s,d,t] <= 1  for all (d,t)
#                       At most one subject per slot per day for this class.
#    C3. No double-book: x[s,d,t] == 0  if faculty of s is busy at (d,t)
#                        in another class (pre-blocked slots).
#    C4. Spread rule  : sum over t of x[s,d,t] <= 1  for all (s,d)
#                       Same subject at most once per day.
#    C5. Daily limit  : sum over (s,t) with same faculty of x[s,d,t]
#                       <= max_hours_per_day - existing_count[fac,d]
#
#  SOFT CONSTRAINTS (minimised in objective function):
#    S1. Even spread  : penalise placing lectures on the same day
#                       across different subjects (encourages distribution).
#    S2. Early slots  : penalise late slots slightly so lectures prefer
#                       morning hours when possible.
#
#  OBJECTIVE: Minimize total soft-constraint penalty.
#  The solver guarantees the global optimum — not just any feasible solution.
#
#  Returns: list of placement dicts on success, None if infeasible.
# ================================================================
def ilp_schedule(mappings, days, slots, faculty_busy, faculty_day_count):
    if not ORTOOLS_AVAILABLE:
        return None, "ortools_missing"

    model  = cp_model.CpModel()
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0   # timeout safety

    D = len(days)
    T = len(slots)

    # Index maps for clean variable naming
    day_idx  = {d: i for i, d in enumerate(days)}
    slot_idx = {s: i for i, s in enumerate(slots)}

    # ── Build subject list (one entry per unique subject-faculty pair) ──
    subjects = []   # list of dicts with subject_id, faculty_id, hours, max_day
    for m in mappings:
        subjects.append({
            'subject_id':        m['subject_id'],
            'subject_name':      m['subject_name'],
            'faculty_id':        m['faculty_id'],
            'hours':             m['hours_per_week'] or 1,
            'max_hours_per_day': m['max_hours_per_day'] or 3,
        })

    S = len(subjects)

    # ── DECISION VARIABLES: x[s_idx, d_idx, t_idx] ∈ {0, 1} ──
    x = {}
    for s in range(S):
        for d in range(D):
            for t in range(T):
                x[s, d, t] = model.NewBoolVar(f'x_s{s}_d{d}_t{t}')

    # ── C1: Coverage — each subject must be placed exactly hours_per_week times ──
    for s, subj in enumerate(subjects):
        model.Add(
            sum(x[s, d, t] for d in range(D) for t in range(T)) == subj['hours']
        )

    # ── C2: No slot clash — at most one subject per (day, slot) for this class ──
    for d in range(D):
        for t in range(T):
            model.Add(sum(x[s, d, t] for s in range(S)) <= 1)

    # ── C3: Pre-block slots where faculty is busy in another class ──
    for s, subj in enumerate(subjects):
        fid = subj['faculty_id']
        for d, day in enumerate(days):
            for t, slot in enumerate(slots):
                if (day, slot, fid) in faculty_busy:
                    model.Add(x[s, d, t] == 0)

    # ── C4: Spread rule — same subject at most once per day ──
    for s in range(S):
        for d in range(D):
            model.Add(sum(x[s, d, t] for t in range(T)) <= 1)

    # ── C5: Faculty daily limit (across all classes combined) ──
    # Group subjects by faculty_id
    fac_subjects = defaultdict(list)
    for s, subj in enumerate(subjects):
        fac_subjects[subj['faculty_id']].append(s)

    for fid, s_indices in fac_subjects.items():
        max_day = subjects[s_indices[0]]['max_hours_per_day']
        for d, day in enumerate(days):
            already = faculty_day_count[(fid, day)]   # from other classes
            remaining = max(0, max_day - already)
            model.Add(
                sum(x[s, d, t] for s in s_indices for t in range(T)) <= remaining
            )

    # ── SOFT CONSTRAINTS: build penalty terms for objective ──
    penalties = []

    # S1: Penalise having more than 2 lectures on the same day (overloading a day)
    #     For each day, count total lectures assigned; penalise if > 2
    for d in range(D):
        day_total = sum(x[s, d, t] for s in range(S) for t in range(T))
        overload  = model.NewIntVar(0, S * T, f'overload_d{d}')
        model.AddMaxEquality(overload, [day_total - 2, model.NewConstant(0)])
        penalties.append(overload)

    # S2: Penalise later slots slightly (prefer morning lectures)
    #     Weight = slot index (0 = earliest = no penalty, T-1 = heaviest penalty)
    for s in range(S):
        for d in range(D):
            for t in range(T):
                late_penalty = model.NewBoolVar(f'late_s{s}_d{d}_t{t}')
                model.Add(late_penalty == x[s, d, t])
                penalties.append(cp_model.LinearExpr.Term(late_penalty, t))

    # ── OBJECTIVE: minimise total penalty ──
    model.Minimize(sum(penalties))

    # ── SOLVE ──
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, "infeasible"

    # ── Extract solution ──
    result = []
    for s, subj in enumerate(subjects):
        for d, day in enumerate(days):
            for t, slot in enumerate(slots):
                if solver.Value(x[s, d, t]) == 1:
                    result.append({
                        'subject_id': subj['subject_id'],
                        'faculty_id': subj['faculty_id'],
                        'day':        day,
                        'slot_id':    slot,
                    })

    algo_used = "ILP (CP-SAT Optimal)" if status == cp_model.OPTIMAL else "ILP (CP-SAT Feasible)"
    return result, algo_used


# ================================================================
#  BACKTRACKING FALLBACK (used when OR-Tools not installed)
#
#  Pure Python recursive backtracking with constraint checking.
#  Finds a feasible solution (not necessarily optimal).
#  Used automatically if ortools import fails.
# ================================================================
def backtrack_schedule(lectures, days, slots, faculty_busy, faculty_day_count):
    placed         = []
    subject_day    = defaultdict(set)
    class_slot     = set()
    fac_busy_local = set()
    fac_day_local  = defaultdict(int)

    def is_valid(lecture, day, slot):
        sid = lecture['subject_id']
        fid = lecture['faculty_id']
        mxd = lecture['max_hours_per_day']
        if (day, slot, fid) in faculty_busy:                                        return False
        if (day, slot, fid) in fac_busy_local:                                      return False
        if (day, slot) in class_slot:                                               return False
        if day in subject_day[sid]:                                                 return False
        if faculty_day_count[(fid, day)] + fac_day_local[(fid, day)] >= mxd:       return False
        return True

    def place(idx):
        if idx == len(lectures):
            return True
        lecture = lectures[idx]
        sid = lecture['subject_id']
        fid = lecture['faculty_id']
        for day in days:
            for slot in slots:
                if not is_valid(lecture, day, slot):
                    continue
                placed.append({'subject_id': sid, 'faculty_id': fid, 'day': day, 'slot_id': slot})
                subject_day[sid].add(day)
                class_slot.add((day, slot))
                fac_busy_local.add((day, slot, fid))
                fac_day_local[(fid, day)] += 1
                if place(idx + 1):
                    return True
                placed.pop()
                subject_day[sid].discard(day)
                class_slot.discard((day, slot))
                fac_busy_local.discard((day, slot, fid))
                fac_day_local[(fid, day)] -= 1
        return False

    return (placed if place(0) else None), "Backtracking CSP"


# ================================================================
#  GENERATE TIMETABLE ROUTE
#
#  Algorithm selection:
#    1. Try ILP (OR-Tools CP-SAT) — optimal, minimises soft constraint
#       violations (overloaded days, late slots). Best quality.
#    2. Fall back to Backtracking CSP — if ortools not installed.
#       Finds any feasible solution, not necessarily optimal.
#
#  Both algorithms work entirely in-memory.
#  DB is only written to after a solution is confirmed.
# ================================================================
@app.route('/generate-timetable', methods=['POST'])
def generate_timetable():
    if session.get('role') != 'admin':
        return redirect('/')

    selected_class_id = int(request.form['class_id'])
    randomise         = request.form.get('randomise', 'off') == 'on'
    DAYS  = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ── Load class ──
    cursor.execute("SELECT * FROM class WHERE class_id = %s", (selected_class_id,))
    cls = cursor.fetchone()
    if not cls:
        conn.close()
        flash("⚠ Class not found.", "error")
        return redirect('/generate-options')

    division = cls['division']
    shift_id = cls['student_shift_id']

    # ── Load time slots ──
    cursor.execute("""
        SELECT slot_id, slot_name, start_time
        FROM time_slot
        WHERE student_shift_id = %s
        ORDER BY start_time
    """, (shift_id,))
    slot_rows = cursor.fetchall()

    if not slot_rows:
        conn.close()
        flash("⚠ No time slots found for this shift.", "error")
        return redirect('/generate-options')

    slots = [s['slot_id'] for s in slot_rows]

    # ── Load subject-faculty mappings ──
    cursor.execute("""
        SELECT csf.subject_id, csf.faculty_id,
               s.hours_per_week, s.subject_name,
               f.faculty_name, f.max_hours_per_day
        FROM class_subject_faculty csf
        JOIN subject s ON csf.subject_id = s.subject_id
        JOIN faculty f ON csf.faculty_id  = f.faculty_id
        WHERE csf.class_id = %s
    """, (selected_class_id,))
    mappings = cursor.fetchall()

    if not mappings:
        conn.close()
        flash("⚠ No subjects assigned. Please assign subjects and faculty first.", "error")
        return redirect('/admin-dashboard')

    # ── Sanity check ──
    total_slots_available = len(DAYS) * len(slots)
    total_hours_needed    = sum(m['hours_per_week'] or 1 for m in mappings)
    if total_hours_needed > total_slots_available:
        conn.close()
        flash(
            f"⚠ Cannot fit {total_hours_needed} lectures into "
            f"{total_slots_available} available slots. "
            "Reduce hours/week or add more time slots.",
            "error"
        )
        return redirect('/generate-options')

    # ── Load faculty conflicts from other classes ──
    cursor.execute("""
        SELECT day, slot_id, faculty_id FROM weekly_timetable
        WHERE class_id != %s
    """, (selected_class_id,))
    existing = cursor.fetchall()

    faculty_busy      = set()
    faculty_day_count = defaultdict(int)
    for e in existing:
        faculty_busy.add((e['day'], e['slot_id'], e['faculty_id']))
        faculty_day_count[(e['faculty_id'], e['day'])] += 1

    # ── Optionally shuffle day/slot order (affects backtracking variety
    #    and ILP soft constraint weighting for late slots) ──
    day_order  = DAYS[:]
    slot_order = slots[:]
    if randomise:
        random.shuffle(day_order)
        random.shuffle(slot_order)

    # ── Run ILP (preferred) or Backtracking (fallback) ──
    if ORTOOLS_AVAILABLE:
        result, algo_used = ilp_schedule(
            mappings, day_order, slot_order, faculty_busy, faculty_day_count
        )
    else:
        # Build expanded lecture list for backtracking
        mappings_sorted = sorted(mappings, key=lambda m: m['hours_per_week'] or 1, reverse=True)
        lectures = []
        for m in mappings_sorted:
            hrs = m['hours_per_week'] or 1
            lectures.extend([{
                'subject_id':        m['subject_id'],
                'subject_name':      m['subject_name'],
                'faculty_id':        m['faculty_id'],
                'faculty_name':      m['faculty_name'],
                'max_hours_per_day': m['max_hours_per_day'] or 3,
            }] * hrs)
        result, algo_used = backtrack_schedule(
            lectures, day_order, slot_order, faculty_busy, faculty_day_count
        )

    if result is None:
        conn.close()
        flash(
            f"⚠ No valid timetable exists for Division {division}. "
            "Try reducing hours/week, increasing max_hours_per_day, or adding time slots.",
            "error"
        )
        return redirect('/generate-options')

    # ── Write to DB only after confirmed success ──
    cursor.execute("DELETE FROM weekly_timetable WHERE class_id = %s", (selected_class_id,))
    for entry in result:
        cursor.execute("""
            INSERT INTO weekly_timetable
                (class_id, subject_id, faculty_id, slot_id, day)
            VALUES (%s, %s, %s, %s, %s)
        """, (selected_class_id,
              entry['subject_id'],
              entry['faculty_id'],
              entry['slot_id'],
              entry['day']))

    conn.commit()
    conn.close()
    flash(
        f"✓ Timetable generated for Division {division} — "
        f"{len(result)} lectures placed using {algo_used}.",
        "success"
    )
    return redirect(f'/view-timetable/{selected_class_id}')


# ================================================================
#  VIEW TIMETABLE
# ================================================================
@app.route('/view-timetable/<int:class_id>')
def view_timetable(class_id):
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM class WHERE class_id = %s", (class_id,))
    cls = cursor.fetchone()
    if not cls:
        conn.close()
        flash(f"⚠ No class found with ID {class_id}.", "error")
        return redirect('/admin-dashboard')

    division = cls['division']
    semester = cls['semester']

    cursor.execute("""
        SELECT wt.day, ts.slot_name, ts.start_time,
               s.subject_name, f.faculty_name
        FROM weekly_timetable wt
        JOIN subject   s  ON wt.subject_id = s.subject_id
        JOIN faculty   f  ON wt.faculty_id  = f.faculty_id
        JOIN time_slot ts ON wt.slot_id     = ts.slot_id
        WHERE wt.class_id = %s
        ORDER BY FIELD(wt.day,'Monday','Tuesday','Wednesday','Thursday','Friday'),
                 ts.start_time
    """, (class_id,))
    rows = cursor.fetchall()
    conn.close()

    DAYS  = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    seen  = {}
    for r in rows:
        if r['slot_name'] not in seen:
            seen[r['slot_name']] = r['start_time']
    slots = sorted(seen.keys(), key=lambda n: seen[n])

    timetable = {d: {s: "" for s in slots} for d in DAYS}
    for r in rows:
        timetable[r['day']][r['slot_name']] = (
            f"{r['subject_name']}<br><small>{r['faculty_name']}</small>"
        )

    return render_template('view_timetable.html',
                           class_id=class_id,
                           division=division,
                           semester=semester,
                           slots=slots,
                           timetable=timetable)


# ================================================================
#  MANUAL OPTIONS PAGE  —  Visual Grid Editor
# ================================================================
@app.route('/manual-options')
def manual_options():
    if session.get('role') != 'admin':
        return redirect('/')

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM class ORDER BY semester, division")
    classes = cursor.fetchall()

    class_id = request.args.get('class_id', classes[0]['class_id'] if classes else None)
    if not class_id:
        conn.close()
        flash("⚠ No classes found. Add a class first.", "error")
        return redirect('/admin-dashboard')

    class_id = int(class_id)

    cursor.execute("SELECT * FROM class WHERE class_id = %s", (class_id,))
    selected_class = cursor.fetchone()

    cursor.execute("""
        SELECT slot_id, slot_name, start_time
        FROM time_slot
        WHERE student_shift_id = %s
        ORDER BY start_time
    """, (selected_class['student_shift_id'],))
    slots = cursor.fetchall()

    cursor.execute("SELECT * FROM subject ORDER BY semester, subject_name")
    subjects = cursor.fetchall()

    cursor.execute("SELECT * FROM faculty ORDER BY faculty_name")
    faculties = cursor.fetchall()

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    cursor.execute("""
        SELECT wt.timetable_id, wt.day, wt.slot_id,
               wt.subject_id, wt.faculty_id,
               s.subject_name, f.faculty_name
        FROM weekly_timetable wt
        JOIN subject s ON wt.subject_id = s.subject_id
        JOIN faculty f ON wt.faculty_id  = f.faculty_id
        WHERE wt.class_id = %s
    """, (class_id,))
    entries = cursor.fetchall()

    timetable = {d: {s['slot_id']: None for s in slots} for d in DAYS}
    for e in entries:
        timetable[e['day']][e['slot_id']] = e

    cursor.execute("""
        SELECT wt.day, wt.slot_id, wt.faculty_id, wt.class_id,
               f.faculty_name, f.max_hours_per_day
        FROM weekly_timetable wt
        JOIN faculty f ON wt.faculty_id = f.faculty_id
    """)
    all_entries = cursor.fetchall()
    conn.close()

    clashes        = {d: {s['slot_id']: None for s in slots} for d in DAYS}
    fac_day_count  = defaultdict(lambda: defaultdict(int))
    fac_slot_class = defaultdict(list)

    for ae in all_entries:
        fac_day_count[ae['faculty_id']][ae['day']] += 1
        fac_slot_class[(ae['faculty_id'], ae['day'], ae['slot_id'])].append(ae['class_id'])

    for d in DAYS:
        for s in slots:
            entry = timetable[d][s['slot_id']]
            if not entry:
                continue
            fid     = entry['faculty_id']
            at_slot = fac_slot_class.get((fid, d, s['slot_id']), [])
            if len(at_slot) > 1:
                clashes[d][s['slot_id']] = f"{entry['faculty_name']} is double-booked"
                continue
            max_day = next((f['max_hours_per_day'] for f in faculties
                            if f['faculty_id'] == fid), 3) or 3
            if fac_day_count[fid][d] > max_day:
                clashes[d][s['slot_id']] = (
                    f"Over daily limit ({fac_day_count[fid][d]}/{max_day})"
                )

    busy_slots = defaultdict(list)
    for ae in all_entries:
        if ae['class_id'] != class_id:
            busy_slots[ae['faculty_id']].append(f"{ae['day']}|{ae['slot_id']}")

    fac_day_count_plain = {
        fid: dict(day_counts)
        for fid, day_counts in fac_day_count.items()
    }
    fac_max_day = {f['faculty_id']: (f['max_hours_per_day'] or 3) for f in faculties}

    return render_template('manual_options.html',
                           classes=classes,
                           selected_class=selected_class,
                           slots=slots,
                           subjects=subjects,
                           faculties=faculties,
                           timetable=timetable,
                           clashes=clashes,
                           busy_slots_json=json.dumps(dict(busy_slots)),
                           fac_day_count_json=json.dumps(fac_day_count_plain),
                           fac_max_day_json=json.dumps(fac_max_day))


# ================================================================
#  SAVE MANUAL TIMETABLE ENTRY
# ================================================================
@app.route('/save-manual-timetable', methods=['POST'])
def save_manual_timetable():
    if session.get('role') != 'admin':
        return redirect('/')

    class_id     = int(request.form['class_id'])
    day          = request.form['day']
    slot_id      = int(request.form['slot_id'])
    subject_id   = int(request.form['subject_id'])
    faculty_id   = int(request.form['faculty_id'])
    timetable_id = request.form.get('timetable_id')

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if timetable_id:
        cursor.execute(
            "DELETE FROM weekly_timetable WHERE timetable_id = %s", (timetable_id,)
        )

    cursor.execute("""
        SELECT COUNT(*) AS cnt FROM weekly_timetable
        WHERE day=%s AND slot_id=%s AND faculty_id=%s AND class_id != %s
    """, (day, slot_id, faculty_id, class_id))
    if cursor.fetchone()['cnt'] > 0:
        if timetable_id:
            conn.rollback()
        conn.close()
        flash(f"⚠ Clash: Faculty already teaching another class at this slot on {day}.", "error")
        return redirect(f'/manual-options?class_id={class_id}')

    cursor.execute("""
        SELECT COUNT(*) AS cnt FROM weekly_timetable
        WHERE day=%s AND slot_id=%s AND class_id=%s
    """, (day, slot_id, class_id))
    if cursor.fetchone()['cnt'] > 0:
        if timetable_id:
            conn.rollback()
        conn.close()
        flash(f"⚠ Clash: Slot already occupied for this class on {day}.", "error")
        return redirect(f'/manual-options?class_id={class_id}')

    cursor.execute("SELECT max_hours_per_day FROM faculty WHERE faculty_id = %s", (faculty_id,))
    fac     = cursor.fetchone()
    max_day = (fac['max_hours_per_day'] or 3) if fac else 3

    cursor.execute("""
        SELECT COUNT(*) AS cnt FROM weekly_timetable
        WHERE day=%s AND faculty_id=%s
    """, (day, faculty_id))
    if cursor.fetchone()['cnt'] >= max_day:
        if timetable_id:
            conn.rollback()
        conn.close()
        flash(f"⚠ Faculty has reached their max of {max_day} lectures on {day}.", "error")
        return redirect(f'/manual-options?class_id={class_id}')

    cursor.execute("""
        INSERT INTO weekly_timetable (class_id, subject_id, faculty_id, slot_id, day)
        VALUES (%s, %s, %s, %s, %s)
    """, (class_id, subject_id, faculty_id, slot_id, day))
    conn.commit()
    conn.close()

    flash("✓ Lecture saved successfully.", "success")
    return redirect(f'/manual-options?class_id={class_id}')


# ================================================================
#  DELETE SINGLE TIMETABLE ENTRY
# ================================================================
@app.route('/delete-timetable-entry', methods=['POST'])
def delete_timetable_entry():
    if session.get('role') != 'admin':
        return redirect('/')

    timetable_id = request.form['timetable_id']
    class_id     = request.form['class_id']

    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM weekly_timetable WHERE timetable_id = %s", (timetable_id,)
    )
    conn.commit()
    conn.close()

    flash("✓ Lecture removed.", "success")
    return redirect(f'/manual-options?class_id={class_id}')


# ================================================================
#  CLEAR ENTIRE TIMETABLE FOR A CLASS
# ================================================================
@app.route('/clear-timetable/<int:class_id>', methods=['POST'])
def clear_timetable(class_id):
    if session.get('role') != 'admin':
        return redirect('/')

    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM weekly_timetable WHERE class_id = %s", (class_id,))
    conn.commit()
    conn.close()

    flash("✓ Timetable cleared.", "success")
    return redirect(f'/manual-options?class_id={class_id}')


# ================================================================
#  COPY TIMETABLE FROM ONE CLASS TO ANOTHER
# ================================================================
@app.route('/copy-timetable', methods=['POST'])
def copy_timetable():
    if session.get('role') != 'admin':
        return redirect('/')

    source_class_id = int(request.form['source_class_id'])
    target_class_id = int(request.form['target_class_id'])

    if source_class_id == target_class_id:
        flash("⚠ Source and target class cannot be the same.", "error")
        return redirect(f'/manual-options?class_id={source_class_id}')

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT subject_id, faculty_id, slot_id, day
        FROM weekly_timetable WHERE class_id = %s
    """, (source_class_id,))
    source_entries = cursor.fetchall()

    if not source_entries:
        conn.close()
        flash("⚠ Source class has no timetable to copy.", "error")
        return redirect(f'/manual-options?class_id={source_class_id}')

    cursor.execute("""
        SELECT subject_id, faculty_id FROM class_subject_faculty WHERE class_id = %s
    """, (target_class_id,))
    target_faculty_map = {r['subject_id']: r['faculty_id'] for r in cursor.fetchall()}

    cursor.execute("DELETE FROM weekly_timetable WHERE class_id = %s", (target_class_id,))

    skipped = 0
    for e in source_entries:
        faculty_id = target_faculty_map.get(e['subject_id'], e['faculty_id'])
        try:
            cursor.execute("""
                INSERT INTO weekly_timetable (class_id, subject_id, faculty_id, slot_id, day)
                VALUES (%s, %s, %s, %s, %s)
            """, (target_class_id, e['subject_id'], faculty_id, e['slot_id'], e['day']))
        except Exception:
            skipped += 1

    conn.commit()

    cursor.execute("SELECT division FROM class WHERE class_id = %s", (target_class_id,))
    target = cursor.fetchone()
    conn.close()

    msg = f"✓ Timetable copied to Division {target['division']}."
    if skipped:
        msg += f" ({skipped} entries skipped due to clashes.)"
    flash(msg, "success")
    return redirect(f'/manual-options?class_id={target_class_id}')


# ================================================================
#  FACULTY DASHBOARD
# ================================================================
@app.route('/faculty-dashboard')
def faculty_dashboard():
    if session.get('role') != 'faculty':
        return redirect('/')

    faculty_id = session.get('linked_id')
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT wt.day, ts.slot_name, ts.start_time,
               s.subject_name, c.semester, c.division
        FROM weekly_timetable wt
        JOIN subject   s  ON wt.subject_id = s.subject_id
        JOIN time_slot ts ON wt.slot_id     = ts.slot_id
        JOIN class     c  ON wt.class_id    = c.class_id
        WHERE wt.faculty_id = %s
        ORDER BY FIELD(wt.day,'Monday','Tuesday','Wednesday','Thursday','Friday'),
                 ts.start_time
    """, (faculty_id,))
    rows = cursor.fetchall()
    conn.close()

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    seen = {}
    for r in rows:
        if r['slot_name'] not in seen:
            seen[r['slot_name']] = r['start_time']
    slots = sorted(seen.keys(), key=lambda n: seen[n])

    schedule = {d: {s: "" for s in slots} for d in DAYS}
    for r in rows:
        schedule[r['day']][r['slot_name']] = (
            f"{r['subject_name']}<br>"
            f"<small>Sem {r['semester']} Div {r['division']}</small>"
        )

    return render_template('faculty_dashboard.html', slots=slots, schedule=schedule)


# ================================================================
#  STUDENT DASHBOARD
# ================================================================
@app.route('/student-dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect('/')

    class_id = session.get('linked_id')
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT semester, division FROM class WHERE class_id = %s", (class_id,))
    cls = cursor.fetchone()

    cursor.execute("""
        SELECT wt.day, ts.slot_name, ts.start_time,
               s.subject_name, f.faculty_name
        FROM weekly_timetable wt
        JOIN subject   s  ON wt.subject_id = s.subject_id
        JOIN faculty   f  ON wt.faculty_id  = f.faculty_id
        JOIN time_slot ts ON wt.slot_id     = ts.slot_id
        WHERE wt.class_id = %s
        ORDER BY FIELD(wt.day,'Monday','Tuesday','Wednesday','Thursday','Friday'),
                 ts.start_time
    """, (class_id,))
    rows = cursor.fetchall()
    conn.close()

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    seen = {}
    for r in rows:
        if r['slot_name'] not in seen:
            seen[r['slot_name']] = r['start_time']
    slots = sorted(seen.keys(), key=lambda n: seen[n])

    timetable = {d: {s: "" for s in slots} for d in DAYS}
    for r in rows:
        timetable[r['day']][r['slot_name']] = (
            f"{r['subject_name']}<br><small>{r['faculty_name']}</small>"
        )

    return render_template('student_dashboard.html',
                           semester=cls['semester'] if cls else '',
                           division=cls['division'] if cls else '',
                           slots=slots,
                           timetable=timetable)


# ================================================================
#  LOGOUT
# ================================================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ================================================================
#  RUN
# ================================================================
if __name__ == "__main__":
    app.run(debug=True)
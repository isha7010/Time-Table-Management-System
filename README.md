# Time Table Management System

A web-based **Time Table Management System** built using **Flask (Python)** and **MySQL**, designed for academic institutions to automatically generate weekly timetables while satisfying real-world constraints such as faculty availability, subject hour limits, shifts, and division-wise scheduling.

---

## 🔹 Features

### 👤 Role-Based Access
- **Admin**
  - Add classes, subjects, and faculties
  - Assign faculty to subjects
  - Generate weekly timetable
  - View division-wise timetable
- **Faculty**
  - View personal timetable
- **Student**
  - View class timetable (read-only)

---

### 📅 Timetable Generation
- Weekly timetable (Monday–Friday)
- Shift-based scheduling (Morning / Afternoon)
- One subject per day per class
- Faculty clash prevention
- Subject hours per week respected
- Division-wise timetable view

---

## 🔹 Algorithm Used

### **Constraint-Based Greedy Scheduling Algorithm**

The timetable is generated using a **greedy, constraint-based scheduling algorithm** with the following constraints:

1. **Faculty Clash Constraint**
   - A faculty cannot be assigned to more than one class in the same time slot.

2. **Subject Per Day Constraint**
   - The same subject cannot appear more than once per day for the same class.

3. **Weekly Hour Constraint**
   - Each subject is scheduled exactly according to its `hours_per_week`.

4. **Shift Constraint**
   - Classes are scheduled only within their assigned shift time slots.

The algorithm places subjects incrementally in the earliest available valid slot while satisfying all constraints.

---

## 🔹 Technology Stack

- **Backend**: Python (Flask)
- **Frontend**: HTML, CSS (Jinja2 Templates)
- **Database**: MySQL
- **Version Control**: Git, GitHub

---

## 🔹 Database Schema (Key Tables)

- `class`
- `subject`
- `faculty`
- `time_slot`
- `class_subject_faculty`
- `weekly_timetable`

---

## 🔹 How to Run the Project

### 1️⃣ Clone the repository
```bash
git clone https://github.com/isha7010/Time-Table-Management-System.git

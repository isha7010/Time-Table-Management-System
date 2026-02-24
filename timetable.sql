-- ================================================================
--  timetable_complete.sql
--  Complete fixed schema — drop and recreate everything cleanly.
--
--  UPDATED to match app.py v2:
--  - weekly_timetable starts EMPTY (generate from dashboard)
--  - users table has accounts for all 5 faculty + 3 student divisions
--  - class_subject_faculty has full ON DELETE CASCADE
--  - weekly_timetable UNIQUE keys enforce double-booking at DB level
--  - max_hours_per_week column present (used by app.py edit-faculty)
--  - room_id nullable (room assignment not yet implemented in app.py)
--
--  Import with:
--      mysql -u root -p timetable < timetable_complete.sql
--  OR paste into MySQL Workbench and execute.
-- ================================================================

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';

-- ================================================================
--  DROP ALL TABLES (children first to avoid FK errors)
-- ================================================================
DROP TABLE IF EXISTS `weekly_timetable`;
DROP TABLE IF EXISTS `class_subject_faculty`;
DROP TABLE IF EXISTS `class_subject`;
DROP TABLE IF EXISTS `class`;
DROP TABLE IF EXISTS `subject`;
DROP TABLE IF EXISTS `faculty`;
DROP TABLE IF EXISTS `time_slot`;
DROP TABLE IF EXISTS `student_shift`;
DROP TABLE IF EXISTS `faculty_shift`;
DROP TABLE IF EXISTS `room`;
DROP TABLE IF EXISTS `users`;
DROP TABLE IF EXISTS `department`;

SET FOREIGN_KEY_CHECKS = 1;


-- ================================================================
--  DEPARTMENT
--  One department seeded. Add more via Workbench if needed.
-- ================================================================
CREATE TABLE `department` (
  `dept_id`   INT          NOT NULL AUTO_INCREMENT,
  `dept_name` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`dept_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `department` VALUES
  (1, 'CSE Data Science');


-- ================================================================
--  STUDENT SHIFT
--  Defines when students attend. Linked to time_slot and class.
-- ================================================================
CREATE TABLE `student_shift` (
  `student_shift_id` INT         NOT NULL AUTO_INCREMENT,
  `shift_name`       VARCHAR(20) DEFAULT NULL,
  `start_time`       TIME        DEFAULT NULL,
  `end_time`         TIME        DEFAULT NULL,
  PRIMARY KEY (`student_shift_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `student_shift` VALUES
  (1, 'Morning',   '08:00:00', '14:00:00'),
  (2, 'Afternoon', '12:00:00', '18:00:00');


-- ================================================================
--  FACULTY SHIFT
--  Defines when faculty are available. Not yet used by app.py
--  constraint logic, but kept for future enhancement.
-- ================================================================
CREATE TABLE `faculty_shift` (
  `faculty_shift_id` INT         NOT NULL AUTO_INCREMENT,
  `shift_name`       VARCHAR(20) DEFAULT NULL,
  `start_time`       TIME        DEFAULT NULL,
  `end_time`         TIME        DEFAULT NULL,
  PRIMARY KEY (`faculty_shift_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `faculty_shift` VALUES
  (1, 'Morning', '08:00:00', '14:00:00'),
  (2, 'Evening', '10:00:00', '18:00:00');


-- ================================================================
--  TIME SLOT
--  FIX (original bug): Old dump had slot 7 AND 8 both named '12-1'
--  for shift 2. Slot 8 corrected to '1-2' (13:00–14:00).
--
--  Morning   shift (1): slots  1–6  → 8-9 through 1-2
--  Afternoon shift (2): slots  7–12 → 12-1 through 5-6
--
--  app.py reads these ordered by start_time for each class's shift.
-- ================================================================
CREATE TABLE `time_slot` (
  `slot_id`          INT         NOT NULL AUTO_INCREMENT,
  `slot_name`        VARCHAR(20) DEFAULT NULL,
  `start_time`       TIME        DEFAULT NULL,
  `end_time`         TIME        DEFAULT NULL,
  `student_shift_id` INT         DEFAULT NULL,
  PRIMARY KEY (`slot_id`),
  KEY `student_shift_id` (`student_shift_id`),
  CONSTRAINT `fk_ts_shift` FOREIGN KEY (`student_shift_id`)
    REFERENCES `student_shift` (`student_shift_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `time_slot` VALUES
  -- Morning shift (student_shift_id = 1)
  (1,  '8-9',   '08:00:00', '09:00:00', 1),
  (2,  '9-10',  '09:00:00', '10:00:00', 1),
  (3,  '10-11', '10:00:00', '11:00:00', 1),
  (4,  '11-12', '11:00:00', '12:00:00', 1),
  (5,  '12-1',  '12:00:00', '13:00:00', 1),
  (6,  '1-2',   '13:00:00', '14:00:00', 1),
  -- Afternoon shift (student_shift_id = 2)
  (7,  '12-1',  '12:00:00', '13:00:00', 2),
  (8,  '1-2',   '13:00:00', '14:00:00', 2),  -- was duplicate '12-1', now fixed
  (9,  '2-3',   '14:00:00', '15:00:00', 2),
  (10, '3-4',   '15:00:00', '16:00:00', 2),
  (11, '4-5',   '16:00:00', '17:00:00', 2),
  (12, '5-6',   '17:00:00', '18:00:00', 2);


-- ================================================================
--  ROOM
--  room_id is stored in weekly_timetable but not yet assigned
--  by the auto-generator (future enhancement). Manual editor
--  can be extended to include room selection.
-- ================================================================
CREATE TABLE `room` (
  `room_id`     INT         NOT NULL AUTO_INCREMENT,
  `room_number` VARCHAR(20) NOT NULL,
  `room_type`   VARCHAR(30) DEFAULT NULL,
  `capacity`    INT         DEFAULT NULL,
  `dept_id`     INT         DEFAULT NULL,
  PRIMARY KEY (`room_id`),
  KEY `dept_id` (`dept_id`),
  CONSTRAINT `fk_room_dept` FOREIGN KEY (`dept_id`)
    REFERENCES `department` (`dept_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `room` VALUES
  (1, 'D201', 'Classroom', 80, 1),
  (2, 'D205', 'Lab',       30, 1),
  (3, 'D207', 'Lab',       30, 1),
  (4, 'D206', 'Lab',       30, 1),
  (5, 'D208', 'Classroom', 70, 1),
  (6, 'D204', 'Classroom', 70, 1);


-- ================================================================
--  FACULTY
--  max_hours_per_day  → checked by generate_timetable() and
--                        save_manual_timetable() in app.py
--  max_hours_per_week → stored and shown; week-limit enforcement
--                        is a known limitation (future fix).
--  New routes in app.py: /edit-faculty/<id>, /delete-faculty/<id>
--  Delete is blocked if faculty has weekly_timetable entries.
-- ================================================================
CREATE TABLE `faculty` (
  `faculty_id`         INT          NOT NULL AUTO_INCREMENT,
  `faculty_name`       VARCHAR(100) NOT NULL,
  `designation`        VARCHAR(50)  DEFAULT NULL,
  `max_hours_per_day`  INT          DEFAULT 3,
  `shift`              VARCHAR(20)  DEFAULT NULL,
  `dept_id`            INT          DEFAULT NULL,
  `max_hours_per_week` INT          DEFAULT 16,
  PRIMARY KEY (`faculty_id`),
  KEY `dept_id` (`dept_id`),
  CONSTRAINT `fk_faculty_dept` FOREIGN KEY (`dept_id`)
    REFERENCES `department` (`dept_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `faculty` VALUES
  (1, 'Dr. A. Sharma',      'HOD', 3, 'Morning', 1, 16),
  (2, 'Dr. Rupali Mahajan', NULL,  3, 'Morning', 1, 18),
  (3, 'Dr. Deepa Abin',     NULL,  3, 'Morning', 1, 18),
  (4, 'Prashant Mandale',   NULL,  3, 'Morning', 1, 18),
  (5, 'Keshav Tambre',      NULL,  3, 'Morning', 1, 18);


-- ================================================================
--  CLASS
--  New routes in app.py:
--    /add-class        → validates duplicate (semester + division)
--    /edit-class/<id>  → update semester, division, shift
--    /duplicate-class/<id> → copy class + assignments to new division
--    /delete-class/<id>    → cascades to weekly_timetable + csf
--
--  division is stored as VARCHAR so values like 'A', 'B', 'C',
--  'D1', 'D2' etc. all work. app.py enforces .upper() on input.
-- ================================================================
CREATE TABLE `class` (
  `class_id`         INT         NOT NULL AUTO_INCREMENT,
  `semester`         INT         NOT NULL,
  `division`         VARCHAR(10) DEFAULT NULL,
  `student_shift_id` INT         DEFAULT NULL,
  `dept_id`          INT         DEFAULT NULL,
  PRIMARY KEY (`class_id`),
  KEY `student_shift_id` (`student_shift_id`),
  KEY `dept_id` (`dept_id`),
  CONSTRAINT `fk_class_shift` FOREIGN KEY (`student_shift_id`)
    REFERENCES `student_shift` (`student_shift_id`),
  CONSTRAINT `fk_class_dept`  FOREIGN KEY (`dept_id`)
    REFERENCES `department`   (`dept_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `class` VALUES
  (1, 3, 'C', 1, 1),
  (2, 3, 'A', 1, 1),
  (3, 3, 'B', 1, 1);


-- ================================================================
--  SUBJECT
--  FIX (original bug): Old dump had 8 rows with duplicates
--  (subject 6 = DT duplicate, 7 = ML duplicate, 8 = P&S duplicate).
--  Cleaned to 5 unique subjects for Sem 3.
--
--  hours_per_week drives the number of lecture slots placed per
--  week during auto-generation. Total = 2+4+4+3+3 = 16 lectures.
--  Available slots = 6 slots/day × 5 days = 30.  Feasible ✅
--
--  New routes in app.py:
--    /add-subject         → validates name + semester not empty
--    /delete-subject/<id> → blocked if timetable entries exist
-- ================================================================
CREATE TABLE `subject` (
  `subject_id`     INT          NOT NULL AUTO_INCREMENT,
  `subject_name`   VARCHAR(100) NOT NULL,
  `semester`       INT          NOT NULL,
  `subject_type`   VARCHAR(20)  DEFAULT 'Theory',
  `hours_per_week` INT          DEFAULT NULL,
  `dept_id`        INT          DEFAULT NULL,
  PRIMARY KEY (`subject_id`),
  KEY `dept_id` (`dept_id`),
  CONSTRAINT `fk_subject_dept` FOREIGN KEY (`dept_id`)
    REFERENCES `department` (`dept_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `subject` VALUES
  (1, 'System Programming and Operating Systems', 3, 'Theory', 2, 1),
  (2, 'DBMS',                                     3, 'Theory', 4, 1),
  (3, 'Machine Learning',                         3, 'Theory', 4, 1),
  (4, 'Design & Analysis of Algorithms',          3, 'Theory', 3, 1),
  (5, 'Probability & Statistics',                 3, 'Theory', 3, 1);

-- ================================================================
--  Lecture hour breakdown per class:
--  SPOS(2) + DBMS(4) + ML(4) + DAA(3) + P&S(3) = 16 hrs/week
--  6 slots/day × 5 days = 30 slots available  ✅
-- ================================================================


-- ================================================================
--  CLASS_SUBJECT  (legacy table — kept for schema completeness)
--  NOT used by app.py. The app uses class_subject_faculty instead.
--  Kept so existing references or reports don't break.
-- ================================================================
CREATE TABLE `class_subject` (
  `class_subject_id` INT NOT NULL AUTO_INCREMENT,
  `class_id`         INT DEFAULT NULL,
  `subject_id`       INT DEFAULT NULL,
  `hours_per_week`   INT DEFAULT NULL,
  `faculty_id`       INT DEFAULT NULL,
  PRIMARY KEY (`class_subject_id`),
  KEY `class_id`   (`class_id`),
  KEY `subject_id` (`subject_id`),
  KEY `fk_cs_faculty` (`faculty_id`),
  CONSTRAINT `fk_cs_class`   FOREIGN KEY (`class_id`)   REFERENCES `class`   (`class_id`),
  CONSTRAINT `fk_cs_subject` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`subject_id`),
  CONSTRAINT `fk_cs_faculty` FOREIGN KEY (`faculty_id`) REFERENCES `faculty` (`faculty_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
-- No data — this table is unused by the application.


-- ================================================================
--  CLASS_SUBJECT_FACULTY
--  Core mapping: which faculty teaches which subject to which class.
--
--  UNIQUE KEY (class_id, subject_id) → one faculty per subject per class.
--  ON DELETE CASCADE on all 3 FKs   → deleting a class, subject, or
--  faculty automatically cleans up assignments.
--
--  FIX (original bug): Old dump was missing all rows for class 3
--  (Division B) and used wrong subject IDs (6, 7) which pointed to
--  now-deleted duplicate subjects.
--
--  New routes in app.py:
--    /assign-faculty   → INSERT ... ON DUPLICATE KEY UPDATE
--    /remove-assignment → DELETE single (class_id, subject_id) row
--    /duplicate-class  → copies all rows from source to new class_id
-- ================================================================
CREATE TABLE `class_subject_faculty` (
  `csf_id`     INT NOT NULL AUTO_INCREMENT,
  `class_id`   INT NOT NULL,
  `subject_id` INT NOT NULL,
  `faculty_id` INT NOT NULL,
  PRIMARY KEY (`csf_id`),
  UNIQUE KEY `uq_class_subject` (`class_id`, `subject_id`),
  KEY `subject_id` (`subject_id`),
  KEY `faculty_id` (`faculty_id`),
  CONSTRAINT `fk_csf_class`   FOREIGN KEY (`class_id`)   REFERENCES `class`   (`class_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_csf_subject` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`subject_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_csf_faculty` FOREIGN KEY (`faculty_id`) REFERENCES `faculty` (`faculty_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Division C (class_id = 1)
INSERT INTO `class_subject_faculty` (`class_id`, `subject_id`, `faculty_id`) VALUES
  (1, 1, 1),  -- SPOS        → Dr. A. Sharma
  (1, 2, 2),  -- DBMS        → Dr. Rupali Mahajan
  (1, 3, 3),  -- ML          → Dr. Deepa Abin
  (1, 4, 4),  -- DAA         → Prashant Mandale
  (1, 5, 5);  -- Prob & Stat → Keshav Tambre

-- Division A (class_id = 2)
INSERT INTO `class_subject_faculty` (`class_id`, `subject_id`, `faculty_id`) VALUES
  (2, 1, 1),  -- SPOS        → Dr. A. Sharma
  (2, 2, 2),  -- DBMS        → Dr. Rupali Mahajan
  (2, 3, 3),  -- ML          → Dr. Deepa Abin
  (2, 4, 4),  -- DAA         → Prashant Mandale
  (2, 5, 5);  -- Prob & Stat → Keshav Tambre

-- Division B (class_id = 3)  ← was COMPLETELY MISSING in original dump
INSERT INTO `class_subject_faculty` (`class_id`, `subject_id`, `faculty_id`) VALUES
  (3, 1, 1),  -- SPOS        → Dr. A. Sharma
  (3, 2, 2),  -- DBMS        → Dr. Rupali Mahajan
  (3, 3, 3),  -- ML          → Dr. Deepa Abin
  (3, 4, 4),  -- DAA         → Prashant Mandale
  (3, 5, 5);  -- Prob & Stat → Keshav Tambre


-- ================================================================
--  WEEKLY TIMETABLE
--  The heart of the system. Populated by:
--    /generate-timetable  → full auto-generation (greedy algorithm)
--    /save-manual-timetable → single-entry manual editor
--    /copy-timetable      → copies one class's schedule to another
--    /delete-timetable-entry → removes one row
--    /clear-timetable/<id>   → removes all rows for a class (NEW)
--
--  UNIQUE KEY uq_class_slot_day:
--    Enforces one subject per time slot per class per day.
--    Python checks this first; DB is the hard backstop.
--
--  UNIQUE KEY uq_faculty_slot_day:
--    Enforces no faculty double-booking across classes.
--    Python checks faculty_busy set; DB is the hard backstop.
--
--  room_id is nullable — room assignment not yet implemented
--  in the generator. Manual assignment is future work.
--
--  ON DELETE CASCADE on all FKs — deleting a class, subject,
--  faculty, or slot auto-removes timetable rows cleanly.
--
--  Starts EMPTY. Generate fresh from Admin Dashboard.
-- ================================================================
CREATE TABLE `weekly_timetable` (
  `timetable_id` INT  NOT NULL AUTO_INCREMENT,
  `class_id`     INT  DEFAULT NULL,
  `subject_id`   INT  DEFAULT NULL,
  `faculty_id`   INT  DEFAULT NULL,
  `slot_id`      INT  DEFAULT NULL,
  `day`          ENUM('Monday','Tuesday','Wednesday','Thursday','Friday') DEFAULT NULL,
  `room_id`      INT  DEFAULT NULL,
  PRIMARY KEY (`timetable_id`),
  UNIQUE KEY `uq_class_slot_day`   (`class_id`,  `slot_id`, `day`),
  UNIQUE KEY `uq_faculty_slot_day` (`faculty_id`, `slot_id`, `day`),
  KEY `class_id`   (`class_id`),
  KEY `subject_id` (`subject_id`),
  KEY `faculty_id` (`faculty_id`),
  KEY `slot_id`    (`slot_id`),
  KEY `room_id`    (`room_id`),
  CONSTRAINT `fk_wt_class`   FOREIGN KEY (`class_id`)   REFERENCES `class`     (`class_id`)   ON DELETE CASCADE,
  CONSTRAINT `fk_wt_subject` FOREIGN KEY (`subject_id`) REFERENCES `subject`   (`subject_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_wt_faculty` FOREIGN KEY (`faculty_id`) REFERENCES `faculty`   (`faculty_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_wt_slot`    FOREIGN KEY (`slot_id`)    REFERENCES `time_slot` (`slot_id`)    ON DELETE CASCADE,
  CONSTRAINT `fk_wt_room`    FOREIGN KEY (`room_id`)    REFERENCES `room`      (`room_id`)    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table intentionally starts EMPTY.
-- Go to: Admin Dashboard → Timetable Management → Auto-Generate
-- OR use Manual Editor to build slot by slot.


-- ================================================================
--  USERS
--  FIX (original bug): Old dump only had 2 users (admin + 1 faculty).
--
--  Now includes:
--    - 1 admin account
--    - 5 faculty accounts (one per faculty row, linked_id = faculty_id)
--    - 3 student accounts (one per class/division, linked_id = class_id)
--
--  linked_id meaning by role:
--    admin   → NULL (no entity linked)
--    faculty → faculty.faculty_id  (used by /faculty-dashboard)
--    student → class.class_id      (used by /student-dashboard)
--
--  ⚠ Passwords are plain text for development only.
--    Hash with bcrypt before any production deployment.
--
--  New routes in app.py read session['linked_id'] to scope
--  faculty/student dashboards to their own data only.
-- ================================================================
CREATE TABLE `users` (
  `user_id`   INT          NOT NULL AUTO_INCREMENT,
  `username`  VARCHAR(100) NOT NULL,
  `password`  VARCHAR(100) NOT NULL,
  `role`      ENUM('admin','faculty','student') NOT NULL,
  `linked_id` INT          DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `users` VALUES
  -- Admin
  (1,  'admin',    'admin123', 'admin',   NULL),
  -- Faculty (linked_id = faculty_id)
  (2,  'sharma',   'f123',     'faculty', 1),
  (3,  'rupali',   'f123',     'faculty', 2),
  (4,  'deepa',    'f123',     'faculty', 3),
  (5,  'prashant', 'f123',     'faculty', 4),
  (6,  'keshav',   'f123',     'faculty', 5),
  -- Students (linked_id = class_id → determines whose timetable they see)
  (7,  'student_c', 's123',    'student', 1),  -- Sem 3 Div C
  (8,  'student_a', 's123',    'student', 2),  -- Sem 3 Div A
  (9,  'student_b', 's123',    'student', 3);  -- Sem 3 Div B


-- ================================================================
--  DONE.
--
--  Quick start after import:
--  1.  mysql -u root -p timetable < timetable_complete.sql
--  2.  python app.py
--  3.  Open http://127.0.0.1:5000
--  4.  Login: admin / admin123
--  5.  Admin Dashboard → Auto-Generate → pick a class → Generate
--
--  Login credentials summary:
--  ┌─────────────┬──────────┬─────────┬──────────────────────┐
--  │ Username    │ Password │ Role    │ Sees                 │
--  ├─────────────┼──────────┼─────────┼──────────────────────┤
--  │ admin       │ admin123 │ admin   │ Full dashboard       │
--  │ sharma      │ f123     │ faculty │ Dr. A. Sharma sched  │
--  │ rupali      │ f123     │ faculty │ Dr. Rupali schedule  │
--  │ deepa       │ f123     │ faculty │ Dr. Deepa schedule   │
--  │ prashant    │ f123     │ faculty │ Prashant schedule    │
--  │ keshav      │ f123     │ faculty │ Keshav schedule      │
--  │ student_c   │ s123     │ student │ Sem 3 Div C timetable│
--  │ student_a   │ s123     │ student │ Sem 3 Div A timetable│
--  │ student_b   │ s123     │ student │ Sem 3 Div B timetable│
--  └─────────────┴──────────┴─────────┴──────────────────────┘
-- ================================================================
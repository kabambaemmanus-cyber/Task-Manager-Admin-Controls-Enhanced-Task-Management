# Task Manager: Admin Controls & Enhanced Task Management

## Overview
This version extends the Task Manager with advanced features for administrators and improved task handling. It introduces role-based access, modular functions, and defensive coding practices to make the system more robust and scalable.

---

## Tools & Technologies
- Python 3  
- File I/O for persistent storage (`user.txt`, `tasks.txt`)  
- Modular functions for maintainability (`register_user`, `add_task`, etc.)  
- Exception handling (`try-except`)  

---

## Features
- **Admin-only registration**: Only administrators can register new users.  
- **Extended menu options**:
  - View completed tasks.  
  - Delete tasks.  
- **Improved task display**: Outputs are formatted for readability.  
- **Defensive coding**: Handles missing files and invalid inputs gracefully.  

---

## Example Usage
<img width="249" height="211" alt="image" src="https://github.com/user-attachments/assets/4121a105-881b-4816-8603-9bd71938a657" />

---

## What I Learned
- How to enforce role-based access (admin vs regular users).  
- The importance of modular functions for maintainability.  
- How to use exception handling to prevent runtime errors.  

---

## Future Improvements
- Add reporting functionality (task overview and user overview).  
- Allow editing of tasks by users.  
- Introduce recursion for validating task selection.  

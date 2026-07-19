import datetime
from pathlib import Path

USERS_FILE = Path("user.txt")
TASKS_FILE = Path("tasks.txt")
TASK_OVERVIEW_FILE = Path("task_overview.txt")
USER_OVERVIEW_FILE = Path("user_overview.txt")


# ---------- Utility helpers ----------

def read_users():
    """Return dict {username: password} from user.txt, creating default admin if missing."""
    users = {}
    if not USERS_FILE.exists():
        USERS_FILE.write_text("admin, adm1n")
    with USERS_FILE.open("r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                username, password = line.split(", ")
            except ValueError:
                # Defensive: skip malformed lines
                continue
            users[username] = password
    return users


def append_user(username, password):
    """Append a single 'username, password' line to user.txt."""
    with USERS_FILE.open("a") as f:
        # Ensure newline if file already has content
        f.write(f"\n{username}, {password}")


def read_tasks():
    """
    Return list of task dicts from tasks.txt.
    Each task: {username, title, description, assigned_date, due_date, completed}
    Dates are strings 'YYYY-MM-DD'; completed is 'Yes' or 'No'.
    """
    tasks = []
    if not TASKS_FILE.exists():
        # Create empty file (optional) so reads don’t fail later
        TASKS_FILE.touch()
    with TASKS_FILE.open("r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                username, title, description, assigned_date, due_date, completed = line.split(", ")
                tasks.append({
                    "username": username,
                    "title": title,
                    "description": description,
                    "assigned_date": assigned_date,
                    "due_date": due_date,
                    "completed": completed
                })
            except ValueError:
                # Defensive: skip malformed lines
                continue
    return tasks


def write_tasks(tasks):
    """Overwrite tasks.txt with provided tasks list."""
    with TASKS_FILE.open("w") as f:
        for i, t in enumerate(tasks):
            line = f"{t['username']}, {t['title']}, {t['description']}, {t['assigned_date']}, {t['due_date']}, {t['completed']}"
            if i > 0:
                f.write("\n" + line)
            else:
                f.write(line)


def today_str():
    return datetime.date.today().strftime("%Y-%m-%d")


def parse_date(d):
    """Parse YYYY-MM-DD into date; return None if invalid."""
    try:
        return datetime.datetime.strptime(d, "%Y-%m-%d").date()
    except Exception:
        return None


# ---------- Required functions (modular) ----------

def reg_user(current_user, users):
    """Register user (admin only), avoiding duplicate usernames."""
    if current_user != "admin":
        print("Permission denied: only admin can register users.")
        return users

    while True:
        new_username = input("Enter new username (or -1 to cancel): ").strip()
        if new_username == "-1":
            print("Registration cancelled.")
            return users
        if not new_username:
            print("Username cannot be empty.")
            continue
        if new_username in users:
            print("That username already exists. Please choose a different username.")
            continue

        new_password = input("Enter new password: ").strip()
        confirm_password = input("Confirm new password: ").strip()
        if new_password != confirm_password:
            print("Passwords do not match. Try again.")
            continue

        append_user(new_username, new_password)
        users[new_username] = new_password
        print(f"User '{new_username}' registered successfully.")
        return users


def add_task():
    """Add a new task to tasks.txt."""
    users = read_users()
    assigned_to = input("Enter the username the task is assigned to: ").strip()
    if assigned_to not in users:
        print("That user does not exist. Please register the user first or assign to an existing user.")
        return

    title = input("Enter the title of the task: ").strip()
    description = input("Enter the description of the task: ").strip()

    # Defensive date input
    while True:
        due_date = input("Enter the due date (YYYY-MM-DD): ").strip()
        if parse_date(due_date):
            break
        print("Invalid date format. Please use YYYY-MM-DD.")

    tasks = read_tasks()
    tasks.append({
        "username": assigned_to,
        "title": title,
        "description": description,
        "assigned_date": today_str(),
        "due_date": due_date,
        "completed": "No"
    })
    write_tasks(tasks)
    print("Task added successfully.")


def view_all():
    """Display all tasks in a readable format."""
    tasks = read_tasks()
    if not tasks:
        print("No tasks available.")
        return
    for i, t in enumerate(tasks, start=1):
        print(f"\nTask #{i}")
        print(f"Assigned to   : {t['username']}")
        print(f"Title         : {t['title']}")
        print(f"Assigned date : {t['assigned_date']}")
        print(f"Due date      : {t['due_date']}")
        print(f"Completed     : {t['completed']}")
        print(f"Description   : {t['description']}")


def view_mine(current_user):
    """Display tasks for the current user, allow select/mark complete/edit."""
    tasks = read_tasks()
    my_tasks = [(i, t) for i, t in enumerate(tasks) if t["username"] == current_user]

    if not my_tasks:
        print("You have no tasks assigned.")
        return

    for idx, (orig_index, t) in enumerate(my_tasks, start=1):
        print(f"\n[{idx}] {t['title']} (Due: {t['due_date']}, Completed: {t['completed']})")
        print(f"    Description: {t['description']}")
        print(f"    Assigned: {t['assigned_date']}")

    # Optional recursion helper for robust input
    def get_valid_task_number(prompt):
        inp = input(prompt).strip()
        if inp == "-1":
            return -1
        try:
            num = int(inp)
        except ValueError:
            print("Please enter a valid integer, or -1 to return.")
            return get_valid_task_number(prompt)
        if num < 1 or num > len(my_tasks):
            print("That task number doesn’t exist. Try again or enter -1 to return.")
            return get_valid_task_number(prompt)
        return num

    selection = get_valid_task_number("\nSelect a task number to manage, or -1 to return: ")
    if selection == -1:
        return

    # Map displayed index back to original tasks list index
    orig_index = my_tasks[selection - 1][0]
    selected_task = tasks[orig_index]

    print("\nChoose an action:")
    print("1 - Mark task as complete")
    print("2 - Edit task (assignee and/or due date)")
    print("3 - Return to main menu")

    action = input("Enter choice: ").strip()
    if action == "1":
        selected_task["completed"] = "Yes"
        write_tasks(tasks)
        print("Task marked as complete.")
    elif action == "2":
        if selected_task["completed"].lower() == "yes":
            print("Completed tasks cannot be edited.")
            return

        # Edit assignee
        change_assignee = input("Edit assignee? (y/n): ").strip().lower()
        if change_assignee == "y":
            users = read_users()
            while True:
                new_user = input("Enter new assignee username: ").strip()
                if new_user in users:
                    selected_task["username"] = new_user
                    break
                print("User does not exist. Try again.")

        # Edit due date
        change_due = input("Edit due date? (y/n): ").strip().lower()
        if change_due == "y":
            while True:
                new_due = input("Enter new due date (YYYY-MM-DD): ").strip()
                if parse_date(new_due):
                    selected_task["due_date"] = new_due
                    break
                print("Invalid date format. Please use YYYY-MM-DD.")

        write_tasks(tasks)
        print("Task updated successfully.")
    else:
        print("Returning to main menu.")


def view_completed():
    """Admin: View all completed tasks."""
    tasks = read_tasks()
    completed = [t for t in tasks if t["completed"].lower() == "yes"]
    if not completed:
        print("No completed tasks found.")
        return
    for i, t in enumerate(completed, start=1):
        print(f"\nCompleted Task #{i}")
        print(f"Assigned to   : {t['username']}")
        print(f"Title         : {t['title']}")
        print(f"Assigned date : {t['assigned_date']}")
        print(f"Due date      : {t['due_date']}")
        print(f"Description   : {t['description']}")


def delete_task():
    """Admin: Delete a task by number (safer than by title)."""
    tasks = read_tasks()
    if not tasks:
        print("No tasks to delete.")
        return

    view_all()  # Show all with numbers for clarity
    while True:
        choice = input("\nEnter the task number to delete (or -1 to cancel): ").strip()
        if choice == "-1":
            print("Deletion cancelled.")
            return
        try:
            num = int(choice)
        except ValueError:
            print("Please enter a valid number.")
            continue
        if num < 1 or num > len(tasks):
            print("That number is out of range.")
            continue
        break

    deleted = tasks.pop(num - 1)
    write_tasks(tasks)
    print(f"Deleted task: {deleted['title']} (assigned to {deleted['username']})")


# ---------- Reports and statistics ----------

def generate_reports():
    """Create task_overview.txt and user_overview.txt based on current data."""
    tasks = read_tasks()
    users = read_users()

    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t["completed"].lower() == "yes")
    uncompleted_tasks = total_tasks - completed_tasks

    # Overdue and incomplete
    today = datetime.date.today()
    overdue_incomplete = 0
    for t in tasks:
        due = parse_date(t["due_date"])
        if due and t["completed"].lower() != "yes" and due < today:
            overdue_incomplete += 1

    pct_incomplete = (uncompleted_tasks / total_tasks * 100) if total_tasks else 0
    pct_overdue = (overdue_incomplete / total_tasks * 100) if total_tasks else 0

    TASK_OVERVIEW_FILE.write_text(
        "\n".join([
            f"Total tasks: {total_tasks}",
            f"Completed tasks: {completed_tasks}",
            f"Uncompleted tasks: {uncompleted_tasks}",
            f"Overdue and incomplete: {overdue_incomplete}",
            f"Percent incomplete: {pct_incomplete:.2f}%",
            f"Percent overdue: {pct_overdue:.2f}%"
        ])
    )

    # User overview
    user_lines = []
    user_lines.append(f"Total users: {len(users)}")
    user_lines.append(f"Total tasks: {total_tasks}")

    # Per-user stats
    for u in users:
        user_tasks = [t for t in tasks if t["username"] == u]
        count_user_tasks = len(user_tasks)
        pct_of_all = (count_user_tasks / total_tasks * 100) if total_tasks else 0
        completed_user = sum(1 for t in user_tasks if t["completed"].lower() == "yes")
        incomplete_user = count_user_tasks - completed_user
        overdue_user = sum(
            1 for t in user_tasks
            if t["completed"].lower() != "yes" and parse_date(t["due_date"]) and parse_date(t["due_date"]) < today
        )

        pct_completed_user = (completed_user / count_user_tasks * 100) if count_user_tasks else 0
        pct_incomplete_user = (incomplete_user / count_user_tasks * 100) if count_user_tasks else 0
        pct_overdue_user = (overdue_user / count_user_tasks * 100) if count_user_tasks else 0

        user_lines.append(f"\nUser: {u}")
        user_lines.append(f"  Tasks assigned: {count_user_tasks}")
        user_lines.append(f"  % of all tasks: {pct_of_all:.2f}%")
        user_lines.append(f"  % completed: {pct_completed_user:.2f}%")
        user_lines.append(f"  % incomplete: {pct_incomplete_user:.2f}%")
        user_lines.append(f"  % overdue: {pct_overdue_user:.2f}%")

    USER_OVERVIEW_FILE.write_text("\n".join(user_lines))
    print("Reports generated: task_overview.txt and user_overview.txt")


def display_statistics():
    """Print the contents of task_overview.txt and user_overview.txt nicely.
       If they don't exist, generate them first.
    """
    if not TASK_OVERVIEW_FILE.exists() or not USER_OVERVIEW_FILE.exists():
        generate_reports()

    print("\n--- Task Overview ---")
    print(TASK_OVERVIEW_FILE.read_text())

    print("\n--- User Overview ---")
    print(USER_OVERVIEW_FILE.read_text())


# ---------- Program entry ----------

def main():
    users = read_users()

    # Login loop
    while True:
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()

        if username in users and users[username] == password:
            print(f"Login successful! Welcome, {username}.")
            current_user = username
            break
        else:
            print("Invalid username or password. Please try again.")

    # Menu loop
    while True:
        if current_user == "admin":
            menu = input(
                '''\nPlease select one of the following options:
r  - register user
a  - add task
va - view all tasks
vm - view my tasks
vc - view completed tasks
del - delete a task
ds - display statistics
gr - generate reports
e  - exit
: '''
            ).lower().strip()
        else:
            menu = input(
                '''\nPlease select one of the following options:
a  - add task
va - view all tasks
vm - view my tasks
e  - exit
: '''
            ).lower().strip()

        if menu == "r" and current_user == "admin":
            users = reg_user(current_user, users)
        elif menu == "a":
            add_task()
        elif menu == "va":
            view_all()
        elif menu == "vm":
            view_mine(current_user)
        elif menu == "vc" and current_user == "admin":
            view_completed()
        elif menu == "del" and current_user == "admin":
            delete_task()
        elif menu == "ds" and current_user == "admin":
            display_statistics()
        elif menu == "gr" and current_user == "admin":
            generate_reports()
        elif menu == "e":
            print("Goodbye!!!")
            break
        else:
            print("Invalid input or insufficient permissions.")

if __name__ == "__main__":
    main()


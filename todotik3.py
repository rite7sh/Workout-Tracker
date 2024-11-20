import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Save tasks for a specific day
def save_tasks_to_file(day):
    with open(f"{day}_tasks.txt", "w") as file:
        for task in task_data[day]["tasks"]:
            file.write(task + "\n")

# Load tasks for a specific day
def load_tasks_from_file(day):
    try:
        with open(f"{day}_tasks.txt", "r") as file:
            return [line.strip() for line in file]
    except FileNotFoundError:
        return []

# Add a new task
def add_task(day):
    task_name = task_inputs[day].get().strip()
    if task_name:
        minutes = ask_for_time()
        if minutes is not None:
            time_seconds = minutes * 60
            task_data[day]["tasks"].append(task_name)
            task_data[day]["timers"][task_name] = time_seconds
            task_id = task_lists[day].insert("", tk.END, values=(task_name, f"{minutes} min"), tags=(task_name,))
            task_data[day]["task_ids"][task_name] = task_id  # Store the task_id
            save_tasks_to_file(day)
            task_inputs[day].delete(0, tk.END)
    else:
        messagebox.showwarning("No Task", "Please enter a task before adding!")

# Ask user for time in minutes
def ask_for_time():
    try:
        time_str = simpledialog.askstring("Task Timer", "Enter time in minutes (0 for no timer):")
        if time_str is None:
            return None
        time_minutes = int(time_str)
        if time_minutes < 0:
            raise ValueError
        return time_minutes
    except (ValueError, TypeError):
        messagebox.showwarning("Invalid Time", "Please enter a valid positive number.")
        return None

# Delete the selected task
def delete_task(day):
    selected_item = task_lists[day].selection()
    if selected_item:
        task_name = task_lists[day].item(selected_item[0], "values")[0]
        task_lists[day].delete(selected_item)
        task_data[day]["tasks"].remove(task_name)
        task_data[day]["timers"].pop(task_name, None)
        del task_data[day]["task_ids"][task_name]  # Remove the task_id
        save_tasks_to_file(day)
    else:
        messagebox.showwarning("No Selection", "Please select a task to delete!")

# Clear all tasks
def clear_all_tasks(day):
    if messagebox.askyesno("Clear All", f"Are you sure you want to clear all tasks for {day}?"):
        task_lists[day].delete(*task_lists[day].get_children())
        task_data[day]["tasks"].clear()
        task_data[day]["timers"].clear()
        task_data[day]["task_ids"].clear()  # Clear task_ids
        save_tasks_to_file(day)

# Start the timer for the selected task
def start_timer(day):
    selected_item = task_lists[day].selection()
    if selected_item:
        task_name = task_lists[day].item(selected_item[0], "values")[0]
        countdown(day, task_name)
    else:
        messagebox.showwarning("No Selection", "Please select a task to start the timer!")

# Timer countdown function
def countdown(day, task_name):
    if task_name in task_data[day]["timers"]:
        remaining_time = task_data[day]["timers"][task_name]
        if remaining_time > 0:
            minutes, seconds = divmod(remaining_time, 60)
            task_id = task_data[day]["task_ids"][task_name]
            task_lists[day].item(task_id, values=(task_name, f"{minutes:02d}:{seconds:02d}"))
            task_data[day]["timers"][task_name] -= 1
            if remaining_time < 60:
                task_lists[day].tag_configure("urgent", background="red")
                task_lists[day].item(task_id, tags=("urgent",))
            else:
                task_lists[day].item(task_id, tags=())
            root.after(1000, countdown, day, task_name)
        else:
            task_id = task_data[day]["task_ids"][task_name]
            task_lists[day].item(task_id, values=(task_name, "Time's up!"))
            messagebox.showinfo("Timer Done", f"Time's up for: {task_name}!")

# Main application window
root = tk.Tk()
root.iconbitmap("icon.ico")
root.title("Workout Tracker")
root.geometry("600x500")

# widget for tab
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# list of days of week
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
task_data = {day: {"tasks": load_tasks_from_file(day), "timers": {}, "task_ids": {}} for day in days}
task_lists = {}
task_inputs = {}

# create tab for each workout day split  (monday se sat)
for day in days:
    # Frame for the tab
    tab = tk.Frame(notebook)
    notebook.add(tab, text=day)

    # input box frame for adding task
    input_frame = tk.Frame(tab)
    input_frame.pack(pady=10)
    task_input = tk.Entry(input_frame, width=30)
    task_input.pack(side=tk.LEFT, padx=5)
    task_inputs[day] = task_input
    add_button = tk.Button(input_frame, text="Add Task", command=lambda d=day: add_task(d), bg="green", fg="white")
    add_button.pack(side=tk.LEFT)

    # column for task list
    columns = ("Task", "Time Left")
    task_list = ttk.Treeview(tab, columns=columns, show="headings")
    task_list.heading("Task", text="Task")
    task_list.heading("Time Left", text="Time Left")
    task_list.column("Task", width=350, anchor="w")
    task_list.column("Time Left", width=100, anchor="e")
    task_list.pack(fill="both", expand=True)
    task_lists[day] = task_list

    # saving inserted tasks
    for task in task_data[day]["tasks"]:
        task_id = task_list.insert("", tk.END, values=(task, "No Timer"))
        task_data[day]["task_ids"][task] = task_id  # Store the task_id

    # all the operations in each tab sep
    action_frame = tk.Frame(tab)
    action_frame.pack(pady=10)
    delete_button = tk.Button(action_frame, text="Delete Task", command=lambda d=day: delete_task(d), bg="red", fg="white")
    delete_button.pack(side=tk.LEFT, padx=5)
    clear_button = tk.Button(action_frame, text="Clear All", command=lambda d=day: clear_all_tasks(d), bg="orange", fg="white")
    clear_button.pack(side=tk.LEFT, padx=5)
    start_button = tk.Button(action_frame, text="Start Timer", command=lambda d=day: start_timer(d), bg="blue", fg="white")
    start_button.pack(side=tk.LEFT, padx=5)

#running the main loop
root.mainloop()

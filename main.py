import streamlit as st
import psycopg2

# Database Connection
conn = psycopg2.connect(database="todolist", user="postgres", password="admin", host="127.0.0.1", port="5432")
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                  (id SERIAL PRIMARY KEY,
                  user_id INT,
                  title TEXT NOT NULL,
                  description TEXT,
                  status TEXT)''')
conn.commit()


# User Authentication
def authenticate(username, password):
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    return cursor.fetchone()


def create_user(username, password):
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    conn.commit()


def logout():
    st.session_state['authenticated'] = False
    st.session_state['username'] = None


def get_user_id(username):
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    return cursor.fetchone()[0]


# Task Management
def create_task(user_id, title, description):
    cursor.execute("INSERT INTO tasks (user_id, title, description, status) VALUES (%s, %s, %s, %s)",
                   (user_id, title, description, "Pending"))
    conn.commit()


def update_task(user_id, task_id, status):
    cursor.execute("UPDATE tasks SET status = %s WHERE id = %s AND user_id = %s", (status, task_id, user_id))
    conn.commit()


def delete_task(user_id, task_id):
    cursor.execute("DELETE FROM tasks WHERE id = %s AND user_id = %s", (task_id, user_id))
    conn.commit()


def get_tasks(user_id):
    cursor.execute("SELECT * FROM tasks WHERE user_id = %s", (user_id,))
    return cursor.fetchall()


def main():
    st.title("To-Do List App Jas")

    if 'authenticated' in st.session_state and st.session_state['authenticated']:
        userloggedin()
    else:
        # User Registration and Authentication
        st.header("User Registration and Authentication")
        register = st.checkbox("Register")
        login = st.checkbox("Login")

        if register:
            username = st.text_input("Username", key="register-username")
            password = st.text_input("Password", type="password", key="register-password")
            if st.button("Register"):
                create_user(username, password)
                st.success("Registration successful! Please log in.")

        if login:
            username = st.text_input("Username", key="login-username")
            password = st.text_input("Password", type="password", key="login-password")
            if st.button("Login"):
                user = authenticate(username, password)
                if user:
                    st.session_state['authenticated'] = True
                    st.session_state['username'] = username
                    st.success("Login successful!")
                    userloggedin()
                else:
                    st.error("Invalid username or password")


def userloggedin():
    username = st.session_state['username']
    user_id = get_user_id(username)

    # Display existing tasks for the user
    st.header("Tasks")
    tasks = get_tasks(user_id)
    if len(tasks) > 0:
        for task in tasks:
            task_id, _, title, description, status = task
            st.write(f"- {title} ({status})")
            if description:
                st.write(f"  Description: {description}")
            st.write('---')

    # Add new task
    st.header("Add New Task")
    new_title = st.text_input("Title")
    new_description = st.text_input("Description (optional)")
    if st.button("Add Task"):
        create_task(user_id, new_title, new_description)
        st.success("Task added successfully!")
        # Retrieve updated tasks
        tasks = get_tasks(user_id)

    # Update task status
    st.header("Update Task Status")
    selected_task = st.selectbox("Select Task", tasks, format_func=lambda task: task[2])
    new_status = st.selectbox("Status", ("Pending", "In Progress", "Completed"))
    if st.button("Update Status"):
        task_id = selected_task[0]
        update_task(user_id, task_id, new_status)
        st.success("Task status updated successfully!")
        # Retrieve updated tasks
        tasks = get_tasks(user_id)

    # Delete task
    st.header("Delete Task")
    task_id_to_delete = st.selectbox("Select Task to Delete", tasks, format_func=lambda task: task[2])
    if st.button("Delete Task"):
        task_id = task_id_to_delete[0]
        delete_task(user_id, task_id)
        st.warning("Task deleted successfully!")
        # Retrieve updated tasks
        tasks = get_tasks(user_id)


if __name__ == "__main__":
    main()

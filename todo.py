import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# Page Configurations
st.set_page_config(page_title="Hackathon Management System", layout="wide")

# Database Setup
conn = sqlite3.connect('hackathon.db')
cursor = conn.cursor()

# Create Tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS organizing_team (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        team TEXT,
        contact TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT,
        assigned_to TEXT,
        due_date DATE,
        status TEXT DEFAULT 'Pending',
        priority TEXT,
        team TEXT
    )
''')
conn.commit()

# Sidebar for Navigation
st.sidebar.title("Hackathon Navigation")
menu = st.sidebar.radio(
    "Select an Option",
    ["Dashboard", "Organizing Team", "Tasks Management", "Team Pages", "Export Data"]
)

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Dashboard
if menu == "Dashboard":
    st.title("Hackathon Management Dashboard")

    # Layout for displaying stats in a more organized way
    col1, col2, col3 = st.columns(3)
    
    # Fetch Stats
    team_count = cursor.execute("SELECT COUNT(*) FROM organizing_team").fetchone()[0]
    pending_tasks = cursor.execute("SELECT COUNT(*) FROM tasks WHERE status='Pending'").fetchone()[0]
    completed_tasks = cursor.execute("SELECT COUNT(*) FROM tasks WHERE status='Completed'").fetchone()[0]

    # Display Stats with Metrics
    with col1:
        st.metric("Total Organizing Team Members", team_count)
    with col2:
        st.metric("Pending Tasks", pending_tasks)
    with col3:
        st.metric("Completed Tasks", completed_tasks)

    # Visualization: Pie Chart for Task Status
    task_status_data = {
        "Status": ["Pending", "Completed"],
        "Count": [pending_tasks, completed_tasks]
    }
    task_status_df = pd.DataFrame(task_status_data)
    fig = px.pie(task_status_df, names="Status", values="Count", title="Task Status Distribution")
    st.plotly_chart(fig)

    # Visualization: Bar Chart for Team Distribution
    team_data = cursor.execute("SELECT team, COUNT(*) FROM tasks GROUP BY team").fetchall()
    teams_df = pd.DataFrame(team_data, columns=["Team", "Task Count"])
    bar_fig = px.bar(teams_df, x="Team", y="Task Count", title="Tasks Distribution by Team", color="Team")
    st.plotly_chart(bar_fig)

    # # Countdown Timer
    # st.subheader("Time Remaining until Hackathon")

    # # Set hackathon end date and calculate the time remaining
    # hackathon_end_date = datetime(2024, 11, 27, 18, 0)  # Example end date: November 27, 2024, 18:00
    # current_time = datetime.now()
    # time_remaining = hackathon_end_date - current_time

    # # Display countdown
    # if time_remaining > timedelta(0):
    #     hours, remainder = divmod(time_remaining.seconds, 3600)
    #     minutes, seconds = divmod(remainder, 60)
    #     st.markdown(f"**{time_remaining.days} days, {hours:02}:{minutes:02}:{seconds:02} remaining**")
    # else:
    #     st.markdown("**Hackathon has ended!**")

    # # Progress Bar for Pending Tasks
    # st.subheader("Progress of Pending Tasks")
    # total_tasks = team_count + pending_tasks + completed_tasks  # Example calculation
    # if total_tasks > 0:
    #     progress = (completed_tasks / total_tasks) * 100
    #     st.progress(progress)
    # else:
    #     st.write("No tasks available.")

    # Custom CSS for enhanced UI
    st.markdown(
        """
        <style>
        .stButton button {
            background-color: #1e90ff;
            color: white;
            border-radius: 10px;
            padding: 10px 20px;
            font-size: 16px;
        }
        .stButton button:hover {
            background-color: #4682b4;
        }
        .stMetric {
            font-size: 22px;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Displaying Background Color & Styling the Page
    st.markdown(
        """
        <style>
        body {
            background-color: #f4f7fa;
        }
        .css-1v3fvcr {
            background-color: #ffffff;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .css-1dpxtcx {
            margin: 20px 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# Organizing Team Management
elif menu == "Organizing Team":
    st.title("Organizing Team Management")
    
    # Add Team Member Form
    with st.form("add_team_member_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            name = st.text_input("Name(Roll No.)")
        with col2:
            role = st.selectbox("Role", ["Event Head", "Guide", "Team Lead", "Member", "Volunteer"])
        with col3:
            team = st.selectbox("Team Name", [
                "Event Management Team",
                "Creative Team",
                "Design Team",
                "Marketing Team",
                "Sponsorship Team",
                "Hospitality Team",
                "Media Team",
                "Documentation Team"
            ])
        with col4:
            contact = st.text_input("Contact (Phone/Email)")
        submitted = st.form_submit_button("Add Team Member")

        if submitted and name and role:
            cursor.execute("INSERT INTO organizing_team (name, role, team, contact) VALUES (?, ?, ?, ?)",
                           (name, role, team, contact))
            conn.commit()
            st.success(f"Team Member '{name}' added successfully!")
        elif submitted:
            st.error("Name and Role are required fields!")

    st.header("Organizing Team Members")
    
    # Fetching team members from the database
    team_members = pd.read_sql_query("SELECT * FROM organizing_team", conn)

    # Displaying team members in a table
    if not team_members.empty:
        # Create a table to display the members
        team_members['Delete'] = team_members.apply(lambda row: st.button(f"Delete {row['name']}", key=row['id']), axis=1)

        # Display table with buttons for deletion
        for _, row in team_members.iterrows():
            col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 3, 1])
            with col1:
                st.write(row['name'])
            with col2:
                st.write(row['role'])
            with col3:
                st.write(row['team'])
            with col4:
                st.write(row['contact'])
            with col5:
                # Display delete button
                if row['Delete']:
                    cursor.execute("DELETE FROM organizing_team WHERE id = ?", (row['id'],))
                    conn.commit()
                    st.warning(f"Team Member '{row['name']}' deleted successfully!")
                    st.experimental_rerun()  # Refresh the page to reflect changes
    else:
        st.write("No team members found.")

# Tasks Management
elif menu == "Tasks Management":
    st.title("Tasks Management")
    
    # Add New Task
    st.subheader("Assign New Task")
    with st.form("add_task_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            task_name = st.text_input("Task Name")
        with col2:
            assigned_to = st.selectbox(
                "Assign To",
                [f"{row[0]} - {row[1]} ({row[2]})" for row in cursor.execute("SELECT id, name, role FROM organizing_team").fetchall()]
            )
        with col3:
            due_date = st.date_input("Due Date", datetime.now())
        with col4:
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        
        # Dropdown for selecting a team
        team = st.selectbox("Team Name", [
            "Event Management Team",
            "Creative Team",
            "Design Team",
            "Marketing Team",
            "Sponsorship Team",
            "Hospitality Team",
            "Media Team",
            "Documentation Team"
        ])
        
        submitted = st.form_submit_button("Assign Task")

        if submitted and task_name and assigned_to and team:
            assignee_name = assigned_to.split(" - ")[1].split(" (")[0]  # Extract name from dropdown text
            cursor.execute("INSERT INTO tasks (task_name, assigned_to, due_date, priority, team) VALUES (?, ?, ?, ?, ?)",
                           (task_name, assignee_name, due_date, priority, team))
            conn.commit()
            st.success(f"Task '{task_name}' assigned to {assignee_name} for team '{team}'!")
        elif submitted:
            st.error("Task Name, Assignee, and Team are required!")

    # Display Tasks
    st.subheader("Task List")
    tasks = pd.read_sql_query("SELECT * FROM tasks", conn)
    for _, row in tasks.iterrows():
        st.markdown(f"### {row['task_name']} (Priority: {row['priority']})")
        st.write(f"Assigned to: {row['assigned_to']} | Due: {row['due_date']} | Status: {row['status']} | Team: {row['team']}")
        col1, col2 = st.columns(2)
        with col1:
            if row['status'] == "Pending" and st.button("Mark as Completed", key=f"complete_{row['id']}"):
                cursor.execute("UPDATE tasks SET status='Completed' WHERE id=?", (row['id'],))
                conn.commit()
                st.success(f"Task '{row['task_name']}' marked as completed!")
        with col2:
            if st.button("Delete Task", key=f"delete_{row['id']}"):
                cursor.execute("DELETE FROM tasks WHERE id=?", (row['id'],))
                conn.commit()
                st.warning(f"Task '{row['task_name']}' deleted!")

# Team Pages
elif menu == "Team Pages":
    st.title("Team Pages")
    
    # List all teams dynamically
    teams = cursor.execute("SELECT DISTINCT team FROM organizing_team WHERE team != ''").fetchall()
    selected_team = st.selectbox("Select a Team", [team[0] for team in teams])

    if selected_team:
        st.header(f"Team: {selected_team}")
        
        # Display Members of Selected Team
        st.subheader("Team Members")
        team_members = pd.read_sql_query(f"SELECT * FROM organizing_team WHERE team = '{selected_team}'", conn)
        st.dataframe(team_members)
        
        # Display Tasks Assigned to Selected Team
        st.subheader("Tasks Assigned to this Team")
        tasks = pd.read_sql_query(f"SELECT * FROM tasks WHERE team = '{selected_team}' ORDER BY priority DESC", conn)
        
        for index, row in tasks.iterrows():
            st.markdown(f"### {row['task_name']} (Priority: {row['priority']})")
            st.write(f"Assigned to: {row['assigned_to']} | Due: {row['due_date']} | Status: {row['status']}")
            
            # Add buttons for moving up/down
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if index > 0 and st.button("⬆️", key=f"up_{row['id']}"):
                    # Move task up (reorder in database)
                    new_priority = tasks.iloc[index - 1]['priority']
                    cursor.execute("UPDATE tasks SET priority=? WHERE id=?", (new_priority, row['id']))
                    cursor.execute("UPDATE tasks SET priority=? WHERE id=?", (tasks.iloc[index]['priority'], tasks.iloc[index - 1]['id']))
                    conn.commit()
                    st.success(f"Task '{row['task_name']}' moved up!")
                    st.experimental_rerun()  # Re-run to reflect changes
                    
            with col2:
                if index < len(tasks) - 1 and st.button("⬇️", key=f"down_{row['id']}"):
                    # Move task down (reorder in database)
                    new_priority = tasks.iloc[index + 1]['priority']
                    cursor.execute("UPDATE tasks SET priority=? WHERE id=?", (new_priority, row['id']))
                    cursor.execute("UPDATE tasks SET priority=? WHERE id=?", (tasks.iloc[index]['priority'], tasks.iloc[index + 1]['id']))
                    conn.commit()
                    st.success(f"Task '{row['task_name']}' moved down!")
                    st.experimental_rerun()  # Re-run to reflect changes

# Export Data (CSV/PDF)
elif menu == "Export Data":
    st.title("Export Hackathon Data")
    
    # Export Organizing Team to CSV
    if st.button("Export Organizing Team to CSV"):
        team_data = pd.read_sql_query("SELECT * FROM organizing_team", conn)
        st.download_button(
            label="Download CSV",
            data=team_data.to_csv(index=False),
            file_name="organizing_team.csv",
            mime="text/csv"
        )
    
    # Export Tasks to CSV
    if st.button("Export Tasks to CSV"):
        tasks_data = pd.read_sql_query("SELECT * FROM tasks", conn)
        st.download_button(
            label="Download CSV",
            data=tasks_data.to_csv(index=False),
            file_name="tasks.csv",
            mime="text/csv"
        )
    
    # Export Organizing Team to PDF
    if st.button("Export Organizing Team to PDF"):
        team_data = pd.read_sql_query("SELECT * FROM organizing_team", conn)
        pdf = BytesIO()
        doc = SimpleDocTemplate(pdf, pagesize=A4)
        table_data = [["ID", "Name", "Role", "Team", "Contact"]]
        table_data += team_data.values.tolist()
        table = Table(table_data)
        table.setStyle(TableStyle([("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                                   ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                                   ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                   ("SIZE", (0, 0), (-1, -1), 10),
                                   ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                                   ("GRID", (0, 0), (-1, -1), 0.25, colors.black)]))
        doc.build([table])
        pdf.seek(0)
        st.download_button("Download PDF", data=pdf, file_name="organizing_team.pdf", mime="application/pdf")

from subtasks import (
    initialize_subtasks_database,
    fetch_subtasks_from_db,
    save_subtasks_to_db,
    delete_subtask_from_db,
    render_saved_subtasks,
)

# Example usage in `backend.py`:
conn = initialize_subtasks_database()

# Call `render_saved_subtasks(conn)` where required to display the saved subtasks.

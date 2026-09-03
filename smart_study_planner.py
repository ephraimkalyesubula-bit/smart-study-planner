
import os

# Name of the file used to persist sessions between runs.
LOG_FILE = "study_log.txt"

# The character used to separate the fields of a session when it is
# written to / read from the log file. A pipe is unlikely to appear
# naturally in a subject/topic/date, which keeps the file simple to parse.
FIELD_SEPARATOR = "|"

# classify_session(duration)
def classify_session(duration):
    """
    Classify a session based on its duration in minutes.
    Short  -> under 30 minutes
    Medium -> 30 to 90 minutes (inclusive)
    Long   -> over 90 minutes
    """
    if duration < 30:
        return "Short"
    elif duration <= 90:
        return "Medium"
    else:
        return "Long"

#  add_session() function
def add_session(sessions):
    """
    Prompt the user for the details of a new study session, validate the
    duration, then store the session as a dictionary inside the sessions
    list (sessions is modified in place).
    """
    subject = input("Enter subject name: ").strip()
    topic = input("Enter topic covered: ").strip()
    date = input("Enter date or day label (e.g. 2026-09-02 or Monday): ").strip()

    # Keep asking until the user gives a valid positive number for duration.
    duration = None
    while duration is None:
        raw_duration = input("Enter duration of session in minutes: ").strip()
        try:
            value = float(raw_duration)
            if value <= 0:
                print("Duration must be a positive number. Please try again.")
            else:
                duration = value
        except ValueError:
            print("That's not a valid number. Please try again.")

    session = {
        "subject": subject,
        "topic": topic,
        "date": date,
        "duration": duration,
    }
    sessions.append(session)
    print(f"Session added: {subject} ({classify_session(duration)}, {duration} min)\n")

# (d) view_sessions()
def view_sessions(sessions):
    """
    Display every logged session in a neatly formatted table, including
    its Short/Medium/Long classification.
    """
    if not sessions:
        print("No sessions have been logged yet.\n")
        return

    # Column widths chosen to comfortably fit typical subject/topic names.
    header = f"{'Subject':<15}{'Topic':<20}{'Date':<15}{'Duration (min)':<16}{'Type':<8}"
    print(header)
    print("-" * len(header))

    for s in sessions:
        classification = classify_session(s["duration"])
        row = (
            f"{s['subject']:<15}"
            f"{s['topic']:<20}"
            f"{s['date']:<15}"
            f"{s['duration']:<16}"
            f"{classification:<8}"
        )
        print(row)
    print()  # blank line after the table for readability

# the search_by_subject(subject)
def search_by_subject(sessions):
    """
    Ask the user for a subject name (case-insensitive match) and display
    only the sessions recorded for that subject, plus the total time
    spent on it. If nothing is found, show a clear message instead of
    an empty table.
    """
    query = input("Enter subject name to search for: ").strip().lower()

    matches = [s for s in sessions if s["subject"].strip().lower() == query]

    if not matches:
        print(f"No sessions found for subject '{query}'.\n")
        return

    print(f"\nSessions found for subject '{query}':")
    header = f"{'Topic':<20}{'Date':<15}{'Duration (min)':<16}{'Type':<8}"
    print(header)
    print("-" * len(header))

    total_time = 0
    for s in matches:
        classification = classify_session(s["duration"])
        total_time += s["duration"]
        row = (
            f"{s['topic']:<20}"
            f"{s['date']:<15}"
            f"{s['duration']:<16}"
            f"{classification:<8}"
        )
        print(row)

    print(f"\nTotal time spent on '{query}': {total_time} minutes\n")

#  study_statistics() function
def study_statistics(sessions):
    """
    Compute and display:
      - total hours studied overall
      - total hours studied per subject
      - the subject with the least total study time (weakest area)
      - the single longest session recorded
    """
    if not sessions:
        print("No sessions have been logged yet, so there are no statistics to show.\n")
        return

    # Build a dictionary mapping subject -> total minutes studied.
    subject_totals = {}
    for s in sessions:
        subject = s["subject"]
        subject_totals[subject] = subject_totals.get(subject, 0) + s["duration"]

    total_minutes_overall = sum(subject_totals.values())

    # Find the subject with the least total study time.
    weakest_subject = min(subject_totals, key=subject_totals.get)

    # Find the single longest session (by duration).
    longest_session = max(sessions, key=lambda s: s["duration"])

    print("\n--- Study Statistics ---")
    print(f"Total time studied overall: {total_minutes_overall} minutes "
          f"({total_minutes_overall / 60:.2f} hours)\n")

    print("Time studied per subject:")
    for subject, minutes in subject_totals.items():
        print(f"  {subject:<15} {minutes} minutes ({minutes / 60:.2f} hours)")

    print(f"\nWeakest area (least total study time): {weakest_subject} "
          f"({subject_totals[weakest_subject]} minutes)")

    print(
        "Longest single session: "
        f"{longest_session['subject']} - {longest_session['topic']} "
        f"({longest_session['duration']} minutes, "
        f"{classify_session(longest_session['duration'])})\n"
    )

# (g) save_sessions() and load_sessions()
def save_sessions(sessions):
    """
    Save every logged session to LOG_FILE, one session per line, with
    fields separated by FIELD_SEPARATOR. Called when the user exits.
    """
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        for s in sessions:
            line = FIELD_SEPARATOR.join(
                [s["subject"], s["topic"], s["date"], str(s["duration"])]
            )
            f.write(line + "\n")
    print(f"Saved {len(sessions)} session(s) to {LOG_FILE}.")


def load_sessions():
    """
    Load sessions from LOG_FILE if it exists, returning them as a list
    of dictionaries. If the file does not exist yet (e.g. first run),
    return an empty list instead of crashing.
    """
    sessions = []

    # Guard against the file not existing yet, e.g. on the very first run.
    if not os.path.exists(LOG_FILE):
        return sessions

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # skip any blank lines
            parts = line.split(FIELD_SEPARATOR)
            if len(parts) != 4:
                continue  # skip malformed lines rather than crashing
            subject, topic, date, duration_str = parts
            try:
                duration = float(duration_str)
            except ValueError:
                continue  # skip lines with an invalid duration value
            sessions.append(
                {"subject": subject, "topic": topic, "date": date, "duration": duration}
            )

    return sessions

# (a) A menu-driven interface
def display_menu():
    """Print the main menu options."""
    print("===== Smart Study Planner =====")
    print("1. Add a study session")
    print("2. View all sessions")
    print("3. Search sessions by subject")
    print("4. View statistics")
    print("5. Save and exit")


def main():
    """
    Main entry point of the programme. Loads any existing sessions,
    then repeatedly shows the menu and handles the user's choice until
    they choose to save and exit.
    """
    sessions = load_sessions()

    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            add_session(sessions)
        elif choice == "2":
            view_sessions(sessions)
        elif choice == "3":
            search_by_subject(sessions)
        elif choice == "4":
            study_statistics(sessions)
        elif choice == "5":
            save_sessions(sessions)
            print("Goodbye!")
            break
        else:
            # Reject invalid menu choices without crashing.
            print("Invalid choice. Please enter a number from 1 to 5.\n")


if __name__ == "__main__":
    main()

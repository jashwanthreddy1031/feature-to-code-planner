"""
app.py
======
Feature to Code Planner - Web Application
Built with Python Flask and SQLite.

Converts project requirements and feature descriptions into complete,
multi-section architectural specifications and modular, production-ready source code.
"""

import os
import json
import sqlite3
from functools import wraps
from flask import (
    Flask, request, redirect, url_for, session,
    flash, render_template, Response
)
from werkzeug.security import generate_password_hash, check_password_hash

import planner_engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
app.secret_key = os.environ.get("SECRET_KEY", "planner-secure-secret-key-2026")
DATABASE = os.path.join(BASE_DIR, "planner.db")
SUPPORTED_LANGUAGES = ["Python", "Java", "C", "JavaScript"]


# ---------------- DATABASE HELPERS ----------------

def get_db():
    """Returns a connection to the SQLite database with row factory enabled."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    """Initializes database tables if they do not already exist."""
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            language TEXT NOT NULL,
            plan TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    db.commit()
    db.close()


# ---------------- AUTHENTICATION DECORATOR ----------------

def login_required(function):
    """Restricts access to authenticated users only."""
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access this page.", "error")
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapper


def get_user_project(project_id):
    """Fetches a project by ID ensuring it belongs to the logged-in user."""
    db = get_db()
    project = db.execute("""
        SELECT * FROM projects
        WHERE id = ? AND user_id = ?
    """, (project_id, session["user_id"])).fetchone()
    db.close()
    return project


# ---------------- VALIDATION HELPERS ----------------

def validate_project_input(name, description, language):
    """
    Performs comprehensive backend validation on project input parameters.
    Returns (is_valid: bool, error_message: str).
    """
    if not name or not name.strip():
        return False, "Project name is required and cannot be empty or whitespace only."
    
    clean_name = name.strip()
    if len(clean_name) < 3:
        return False, "Project name must be at least 3 characters long."
    if len(clean_name) > 100:
        return False, "Project name cannot exceed 100 characters."

    if not description or not description.strip():
        return False, "Feature description is required and cannot be empty."

    clean_desc = description.strip()
    if len(clean_desc) < 10:
        return False, "Feature description must be at least 10 characters long."
    if len(clean_desc) > 2000:
        return False, "Feature description cannot exceed 2000 characters."

    if not language or language not in SUPPORTED_LANGUAGES:
        return False, f"Please select a valid programming language: {', '.join(SUPPORTED_LANGUAGES)}."

    return True, ""


# ---------------- ROUTES ----------------

@app.route("/")
def home():
    """Landing page or direct redirect to dashboard for logged-in users."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("home.html", title="Welcome")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """User account creation with validation."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Backend validations
        if not name or len(name) < 2:
            flash("Full name is required (at least 2 characters).", "error")
            return render_template("signup.html", title="Sign Up", name=name, email=email)

        if not email or "@" not in email or "." not in email:
            flash("A valid email address is required.", "error")
            return render_template("signup.html", title="Sign Up", name=name, email=email)

        if not password or len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("signup.html", title="Sign Up", name=name, email=email)

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password))
            )
            db.commit()
            db.close()
            flash("Account successfully created! Please sign in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            db.close()
            flash("An account with this email address already exists.", "error")
            return render_template("signup.html", title="Sign Up", name=name, email=email)
        except Exception as e:
            db.close()
            flash(f"An unexpected error occurred: {str(e)}", "error")
            return render_template("signup.html", title="Sign Up", name=name, email=email)

    return render_template("signup.html", title="Sign Up")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User sign-in."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "error")
            return render_template("login.html", title="Sign In", email=email)

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        db.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password. Please try again.", "error")
        return render_template("login.html", title="Sign In", email=email)

    return render_template("login.html", title="Sign In")


@app.route("/logout")
def logout():
    """Logs out the active user."""
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    """Main SaaS dashboard displaying user stats and recent projects."""
    db = get_db()
    user_id = session["user_id"]

    total = db.execute(
        "SELECT COUNT(*) FROM projects WHERE user_id = ?",
        (user_id,)
    ).fetchone()[0]

    recent = db.execute(
        "SELECT * FROM projects WHERE user_id = ? ORDER BY id DESC LIMIT 5",
        (user_id,)
    ).fetchall()

    db.close()

    return render_template(
        "dashboard.html",
        title="Dashboard",
        name=session.get("user_name"),
        total=total,
        recent=recent
    )


@app.route("/new", methods=["GET", "POST"])
@login_required
def new_project():
    """Creates a new project and generates a 13-section plan with modular source code."""
    if request.method == "POST":
        name = request.form.get("name", "")
        description = request.form.get("description", "")
        language = request.form.get("language", "")

        is_valid, err_msg = validate_project_input(name, description, language)
        if not is_valid:
            flash(err_msg, "error")
            return render_template(
                "new_project.html",
                title="Create Project",
                form_data={"name": name, "description": description, "language": language}
            )

        clean_name = name.strip()
        clean_desc = description.strip()

        try:
            # Generate complete 13-section plan + modular source code
            plan_data = planner_engine.generate_complete_plan(clean_name, clean_desc, language)

            db = get_db()
            cursor = db.execute("""
                INSERT INTO projects (user_id, name, description, language, plan)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session["user_id"],
                clean_name,
                clean_desc,
                language,
                json.dumps(plan_data)
            ))
            project_id = cursor.lastrowid
            db.commit()
            db.close()

            flash("Project plan & modular code generated successfully!", "success")
            return redirect(url_for("view_project", project_id=project_id))

        except Exception as e:
            flash(f"Error generating plan: {str(e)}", "error")
            return render_template(
                "new_project.html",
                title="Create Project",
                form_data={"name": name, "description": description, "language": language}
            )

    return render_template("new_project.html", title="Create Project")


@app.route("/project/<int:project_id>")
@login_required
def view_project(project_id):
    """Displays the full 13-section technical specification and modular code."""
    project = get_user_project(project_id)
    if not project:
        flash("Project not found or access denied.", "error")
        return redirect(url_for("history"))

    # Safely load and normalize plan (supports both existing & new plans)
    plan = planner_engine.normalize_plan(project["plan"], project["name"], project["language"])

    return render_template(
        "view_project.html",
        title=f"{project['name']} – Plan",
        project=project,
        plan=plan
    )


@app.route("/download/<int:project_id>")
@login_required
def download_project(project_id):
    """Generates a downloadable full text report covering all 13 sections and modular code."""
    project = get_user_project(project_id)
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for("history"))

    plan = planner_engine.normalize_plan(project["plan"], project["name"], project["language"])

    separator = "=" * 70
    sub_sep = "-" * 70

    lines = [
        separator,
        f"  FEATURE TO CODE PLANNER – TECHNICAL PROJECT REPORT",
        separator,
        f"Project Name   : {project['name']}",
        f"Target Language: {project['language']}",
        f"Created Date   : {project['created_at']}",
        f"Estimated Time : {plan.get('estimated_days', 10)} Days (~{plan.get('estimated_weeks', 1.5)} Weeks)",
        "",
        separator,
        "1. PROJECT SPECIFICATION",
        separator,
        plan.get("title", project["name"]),
        "",
        separator,
        "2. PROJECT OVERVIEW",
        separator,
        plan.get("overview", plan.get("summary", "")),
        "",
        separator,
        "3. PROBLEM STATEMENT",
        separator,
        plan.get("problem_statement", "N/A"),
        "",
        separator,
        "4. PROJECT OBJECTIVES",
        separator,
    ]

    for obj in plan.get("objectives", []):
        lines.append(f"  * {obj}")

    lines.extend([
        "",
        separator,
        "5. FUNCTIONAL REQUIREMENTS (FR)",
        separator,
    ])
    for fr in plan.get("functional_requirements", []):
        lines.append(f"  [{fr.get('id', 'FR')}] {fr.get('title', '')}")
        lines.append(f"    Description: {fr.get('description', '')}")

    lines.extend([
        "",
        separator,
        "6. NON-FUNCTIONAL REQUIREMENTS (NFR)",
        separator,
    ])
    for nfr in plan.get("non_functional_requirements", []):
        lines.append(f"  - {nfr.get('category', '')}: {nfr.get('requirement', '')}")

    lines.extend([
        "",
        separator,
        "7. SYSTEM MODULES & 8. MODULE DESCRIPTIONS",
        separator,
    ])
    for md in plan.get("module_descriptions", []):
        lines.append(f"  Module : {md.get('name', '')}")
        lines.append(f"  Role   : {md.get('role', '')}")
        lines.append(f"  Detail : {md.get('description', '')}")
        lines.append(f"  Inputs : {md.get('inputs', '')}")
        lines.append(f"  Outputs: {md.get('outputs', '')}")
        lines.append("")

    tech = plan.get("tech_requirements", {})
    lines.extend([
        separator,
        "9. TECHNOLOGY REQUIREMENTS",
        separator,
        f"  Frontend / CLI : {tech.get('frontend', plan.get('frontend', 'N/A'))}",
        f"  Backend Runtime: {tech.get('backend', plan.get('backend', 'N/A'))}",
        f"  Database Layer : {tech.get('database', plan.get('database', 'N/A'))}",
        f"  Tools / Libs   : {tech.get('tools', 'Standard Toolchain')}",
        "",
        separator,
        "10. IMPLEMENTATION ROADMAP",
        separator,
    ])
    for step in plan.get("roadmap", []):
        lines.append(f"  * {step.get('stage', '')} ({step.get('days', 1)} days)")
        lines.append(f"    {step.get('details', '')}")

    lines.extend([
        "",
        separator,
        "11. SUGGESTED FOLDER STRUCTURE",
        separator,
        plan.get("folder_tree", ""),
        "",
        separator,
        "MODULAR SOURCE CODE GENERATION",
        separator,
    ])

    modules = plan.get("modules", [])
    if modules:
        for mod in modules:
            lines.append(sub_sep)
            lines.append(f"FILE: {mod.get('filename')} ({mod.get('module_name')})")
            lines.append(f"ROLE: {mod.get('role')} | PURPOSE: {mod.get('purpose')}")
            lines.append(sub_sep)
            lines.append(mod.get("code", ""))
            lines.append("")
    else:
        lines.append(plan.get("code", ""))

    lines.extend([
        "",
        separator,
        "12. TESTING APPROACH",
        separator,
    ])
    for test in plan.get("testing_approach", []):
        lines.append(f"  * {test.get('type')}: {test.get('scope')}")
        lines.append(f"    {test.get('description')}")

    lines.extend([
        "",
        separator,
        "13. EXPECTED OUTPUT",
        separator,
        plan.get("expected_output", ""),
        "",
        separator,
        "End of Report | Generated by Feature to Code Planner",
        separator,
    ])

    report_text = "\n".join(lines)
    clean_filename = "".join(c for c in project["name"] if c.isalnum() or c in (' ', '_', '-')).rstrip()
    clean_filename = clean_filename.replace(" ", "_").lower()

    return Response(
        report_text,
        mimetype="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename={clean_filename}_report.txt"
        }
    )


@app.route("/history")
@login_required
def history():
    """Project history listing with live keyword search and language filters."""
    db = get_db()
    query = request.args.get("q", "").strip()

    if query:
        projects = db.execute("""
            SELECT * FROM projects
            WHERE user_id = ? AND name LIKE ?
            ORDER BY id DESC
        """, (session["user_id"], f"%{query}%")).fetchall()
    else:
        projects = db.execute("""
            SELECT * FROM projects
            WHERE user_id = ?
            ORDER BY id DESC
        """, (session["user_id"],)).fetchall()

    db.close()

    return render_template(
        "history.html",
        title="Project History",
        projects=projects,
        query=query
    )


@app.route("/edit/<int:project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    """Edits an existing project and regenerates the plan and modular code."""
    project = get_user_project(project_id)
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for("history"))

    if request.method == "POST":
        name = request.form.get("name", "")
        description = request.form.get("description", "")
        language = request.form.get("language", "")

        is_valid, err_msg = validate_project_input(name, description, language)
        if not is_valid:
            flash(err_msg, "error")
            return render_template(
                "edit_project.html",
                title="Edit Project",
                project=project,
                form_data={"name": name, "description": description, "language": language}
            )

        clean_name = name.strip()
        clean_desc = description.strip()

        try:
            plan_data = planner_engine.generate_complete_plan(clean_name, clean_desc, language)

            db = get_db()
            db.execute("""
                UPDATE projects
                SET name = ?, description = ?, language = ?, plan = ?
                WHERE id = ? AND user_id = ?
            """, (
                clean_name,
                clean_desc,
                language,
                json.dumps(plan_data),
                project_id,
                session["user_id"]
            ))
            db.commit()
            db.close()

            flash("Project plan & code updated successfully!", "success")
            return redirect(url_for("view_project", project_id=project_id))

        except Exception as e:
            flash(f"Error updating plan: {str(e)}", "error")
            return render_template(
                "edit_project.html",
                title="Edit Project",
                project=project,
                form_data={"name": name, "description": description, "language": language}
            )

    return render_template("edit_project.html", title="Edit Project", project=project)


@app.route("/delete/<int:project_id>", methods=["POST"])
@login_required
def delete_project(project_id):
    """Deletes a project after verification."""
    project = get_user_project(project_id)
    if not project:
        flash("Project not found or unauthorized.", "error")
        return redirect(url_for("history"))

    db = get_db()
    db.execute(
        "DELETE FROM projects WHERE id = ? AND user_id = ?",
        (project_id, session["user_id"])
    )
    db.commit()
    db.close()

    flash(f"Project '{project['name']}' has been deleted.", "success")
    return redirect(url_for("history"))


# ---------------- APPLICATION STARTUP ----------------

if __name__ == "__main__":
    init_db()
    # Default to port 5001 to prevent collisions with macOS AirPlay (port 5000)
    port = int(os.environ.get("PORT", 5001))
    print(f"Starting Feature to Code Planner on http://127.0.0.1:{port}")
    app.run(debug=True, port=port)

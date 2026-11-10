"""
planner_engine.py
=================
Core business logic for the Feature to Code Planner.
Generates comprehensive 13-section software project plans and complete,
modular source code for Python, Java, C, and JavaScript.

Designed for clarity and educational value (college mini-project vivas).
"""

import re
import json


def extract_entity_name(project_name, features):
    """
    Extracts a representative singular entity name from the project title or features.
    Example: "Student Management System" -> "Student"
             "Online Book Store" -> "Book"
             "Hospital Management" -> "Patient"
             "Task Tracker" -> "Task"
    """
    name = project_name.strip()

    # Common domain keyword mapping
    mappings = [
        (r'\b(student|school|college|admission|grading)\b', 'Student'),
        (r'\b(library|book|books)\b', 'Book'),
        (r'\b(hospital|clinic|patient|doctor|medical)\b', 'Patient'),
        (r'\b(task|todo|issue|ticket)\b', 'Task'),
        (r'\b(inventory|product|store|shop|ecommerce|warehouse)\b', 'Product'),
        (r'\b(bank|banking|account|transaction|wallet)\b', 'Account'),
        (r'\b(employee|staff|payroll|hr|worker)\b', 'Employee'),
        (r'\b(hotel|room|reservation|booking)\b', 'Reservation'),
        (r'\b(vehicle|car|parking|rental|transport)\b', 'Vehicle'),
        (r'\b(course|tutorial|learning|quiz)\b', 'Course'),
        (r'\b(user|customer|member|client)\b', 'User'),
        (r'\b(order|bill|invoice)\b', 'Order'),
        (r'\b(movie|cinema|theatre)\b', 'Movie'),
        (r'\b(chat|message|messaging)\b', 'Message'),
        (r'\b(fitness|workout|gym)\b', 'Workout'),
        (r'\b(recipe|food|restaurant)\b', 'Recipe'),
    ]

    haystack = (name + " " + " ".join(features)).lower()
    for pattern, entity in mappings:
        if re.search(pattern, haystack):
            return entity

    # Extract first prominent noun from project name
    words = re.sub(r'[^a-zA-Z\s]', '', name).split()
    filter_out = {
        'management', 'system', 'app', 'application', 'portal', 'platform',
        'hub', 'planner', 'tracker', 'service', 'online', 'smart', 'automated',
        'digital', 'pro', 'tool', 'manager', 'software', 'mini', 'project'
    }
    candidates = [w.capitalize() for w in words if w.lower() not in filter_out]
    if candidates:
        first = candidates[0]
        # simple de-pluralize
        if first.endswith('ies') and len(first) > 4:
            return first[:-3] + 'y'
        if first.endswith('s') and not first.endswith('ss') and len(first) > 3:
            return first[:-1]
        return first

    return "Item"


def parse_features(description):
    """
    Splits, cleans, and standardizes user-entered features.
    """
    if not description:
        return ["Analyze requirements", "Data management", "Report generation"]

    raw = description.replace(";", ",").replace("\n", ",").replace("•", ",")
    items = []
    for chunk in raw.split(","):
        cleaned = re.sub(r'^\s*[-*0-9.]+\s*', '', chunk).strip()
        if cleaned:
            # Capitalize first letter
            capitalized = cleaned[0].upper() + cleaned[1:]
            items.append(capitalized)

    # De-duplicate while preserving order
    unique_items = list(dict.fromkeys(items))
    if not unique_items:
        return ["Record registration", "Search records", "Update records", "Generate reports"]
    return unique_items


def categorize_features(features, entity):
    """
    Classifies parsed features into action categories to generate specialized code.
    """
    categories = {
        'create': [],
        'read': [],
        'search': [],
        'update': [],
        'delete': [],
        'other': []
    }

    for feat in features:
        low = feat.lower()
        if any(w in low for w in ['create', 'add', 'register', 'insert', 'new', 'enroll', 'book', 'issue']):
            categories['create'].append(feat)
        elif any(w in low for w in ['search', 'find', 'filter', 'lookup', 'query']):
            categories['search'].append(feat)
        elif any(w in low for w in ['update', 'edit', 'modify', 'change', 'return']):
            categories['update'].append(feat)
        elif any(w in low for w in ['delete', 'remove', 'cancel', 'drop']):
            categories['delete'].append(feat)
        elif any(w in low for w in ['view', 'list', 'show', 'display', 'get', 'fetch', 'all']):
            categories['read'].append(feat)
        else:
            categories['other'].append(feat)

    # Defaults if missing core CRUD
    if not categories['create']:
        categories['create'].append(f"Add new {entity.lower()}")
    if not categories['read']:
        categories['read'].append(f"View all {entity.lower()}s")
    if not categories['search']:
        categories['search'].append(f"Search {entity.lower()} by name or ID")

    return categories


# ==============================================================================
# MODULAR CODE GENERATION (Python, Java, C, JavaScript)
# ==============================================================================

def generate_python_modules(project_name, entity, features):
    e_lower = entity.lower()
    e_class = entity.capitalize()

    # Module 1: models.py
    models_code = f'''"""
models.py
---------
Domain Data Models for {project_name}.
Defines the {e_class} entity with validation, serialization, and string formatting.
"""

from datetime import datetime
from typing import Dict, Any, Optional


class {e_class}:
    """
    Represents a {e_lower} record in the {project_name}.
    """

    def __init__(
        self,
        record_id: int,
        name: str,
        category: str = "General",
        details: str = "",
        status: str = "Active",
        created_at: Optional[str] = None
    ):
        self.record_id = int(record_id)
        self.name = name.strip()
        self.category = category.strip()
        self.details = details.strip()
        self.status = status.strip()
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def validate(self) -> bool:
        """Validates that mandatory fields are present and valid."""
        if not self.name:
            raise ValueError("Name cannot be empty.")
        if self.record_id <= 0:
            raise ValueError("Record ID must be a positive integer.")
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the model into a dictionary for JSON/DB storage."""
        return {{
            "id": self.record_id,
            "name": self.name,
            "category": self.category,
            "details": self.details,
            "status": self.status,
            "created_at": self.created_at
        }}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "{e_class}":
        """Deserializes a dictionary into a {e_class} instance."""
        return cls(
            record_id=data["id"],
            name=data["name"],
            category=data.get("category", "General"),
            details=data.get("details", ""),
            status=data.get("status", "Active"),
            created_at=data.get("created_at")
        )

    def __str__(self) -> str:
        return f"[{{self.record_id}}] {{self.name}} ({{self.category}}) - Status: {{self.status}}"
'''

    # Module 2: storage.py
    storage_code = f'''"""
storage.py
----------
Data Persistence Layer for {project_name}.
Handles reading and writing {e_class} records with JSON storage and error handling.
"""

import json
import os
from typing import List, Optional
from models import {e_class}


class {e_class}Storage:
    """Handles persistent file storage and in-memory caching for {e_class} records."""

    def __init__(self, filename: str = "{e_lower}s.json"):
        self.filename = filename
        self._records: List[{e_class}] = []
        self.load_from_disk()

    def load_from_disk(self) -> None:
        """Loads records from the JSON storage file."""
        if not os.path.exists(self.filename):
            self._records = []
            return

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._records = [{e_class}.from_dict(item) for item in data]
        except (json.JSONDecodeError, IOError) as e:
            print(f"[Warning] Could not load storage file: {{e}}. Starting empty.")
            self._records = []

    def save_to_disk(self) -> bool:
        """Persists all current records to disk."""
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                data = [rec.to_dict() for rec in self._records]
                json.dump(data, f, indent=4)
            return True
        except IOError as e:
            print(f"[Error] Failed to save data: {{e}}")
            return False

    def add(self, item: {e_class}) -> bool:
        """Adds a new record after verifying uniqueness."""
        item.validate()
        if self.find_by_id(item.record_id):
            raise ValueError(f"Record with ID {{item.record_id}} already exists.")
        self._records.append(item)
        return self.save_to_disk()

    def find_by_id(self, record_id: int) -> Optional[{e_class}]:
        """Finds a single record by its numeric ID."""
        for rec in self._records:
            if rec.record_id == record_id:
                return rec
        return None

    def find_all(self) -> List[{e_class}]:
        """Returns a copy of all current records."""
        return list(self._records)

    def search_by_name(self, query: str) -> List[{e_class}]:
        """Case-insensitive search across name and details."""
        q = query.lower().strip()
        return [r for r in self._records if q in r.name.lower() or q in r.details.lower()]

    def update(self, updated: {e_class}) -> bool:
        """Updates an existing record matching ID."""
        updated.validate()
        for i, rec in enumerate(self._records):
            if rec.record_id == updated.record_id:
                self._records[i] = updated
                return self.save_to_disk()
        return False

    def delete(self, record_id: int) -> bool:
        """Removes a record by ID."""
        initial_len = len(self._records)
        self._records = [r for r in self._records if r.record_id != record_id]
        if len(self._records) < initial_len:
            return self.save_to_disk()
        return False
'''

    # Module 3: service.py
    service_code = f'''"""
service.py
----------
Business Logic Service Layer for {project_name}.
Implements the core requested features:
{chr(10).join(f"- {f}" for f in features)}
"""

from typing import List, Optional, Tuple
from models import {e_class}
from storage import {e_class}Storage


class {e_class}Service:
    """Coordinates business rules, validations, and storage operations."""

    def __init__(self, storage: Optional[{e_class}Storage] = None):
        self.storage = storage or {e_class}Storage()

    def register_{e_lower}(
        self,
        record_id: int,
        name: str,
        category: str,
        details: str
    ) -> Tuple[bool, str]:
        """Feature: Register / Create new {e_lower}."""
        if not name or len(name.strip()) < 2:
            return False, "Validation error: Name must have at least 2 characters."
        if record_id <= 0:
            return False, "Validation error: ID must be a positive integer."

        try:
            item = {e_class}(record_id, name, category, details)
            self.storage.add(item)
            return True, f"Success: {e_class} '{{name}}' registered with ID {{record_id}}."
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error during registration: {{e}}"

    def list_all_{e_lower}s(self) -> List[{e_class}]:
        """Feature: View / List all {e_lower} records."""
        return self.storage.find_all()

    def search_{e_lower}s(self, query: str) -> List[{e_class}]:
        """Feature: Search {e_lower}s by name or keyword."""
        return self.storage.search_by_name(query)

    def get_{e_lower}_by_id(self, record_id: int) -> Optional[{e_class}]:
        """Retrieves a single {e_lower} by ID."""
        return self.storage.find_by_id(record_id)

    def update_{e_lower}(
        self,
        record_id: int,
        name: str,
        category: str,
        details: str,
        status: str
    ) -> Tuple[bool, str]:
        """Feature: Update details of an existing {e_lower}."""
        existing = self.storage.find_by_id(record_id)
        if not existing:
            return False, f"Error: {e_class} with ID {{record_id}} not found."

        try:
            updated = {e_class}(record_id, name, category, details, status, existing.created_at)
            if self.storage.update(updated):
                return True, f"Success: {e_class} ID {{record_id}} updated."
            return False, "Update failed: could not write changes to storage."
        except Exception as e:
            return False, f"Error updating record: {{e}}"

    def delete_{e_lower}(self, record_id: int) -> Tuple[bool, str]:
        """Feature: Delete / Remove a {e_lower} record."""
        existing = self.storage.find_by_id(record_id)
        if not existing:
            return False, f"Error: No {e_lower} found with ID {{record_id}}."

        if self.storage.delete(record_id):
            return True, f"Success: {e_class} '{{existing.name}}' (ID: {{record_id}}) removed."
        return False, "Delete operation failed."

    def count(self) -> int:
        """Returns total records count."""
        return len(self.storage.find_all())
'''

    # Module 4: main.py
    main_code = f'''"""
main.py
-------
Main Entry Point & Interactive CLI for {project_name}.
Provides a clean user menu to execute all project features.
"""

import sys
from service import {e_class}Service


def print_header(title: str):
    print("\\n" + "=" * 50)
    print(f"  {{title}}")
    print("=" * 50)


def prompt_int(prompt: str) -> int:
    while True:
        try:
            val = input(prompt).strip()
            return int(val)
        except ValueError:
            print("[Error] Please enter a valid number.")


def main():
    service = {e_class}Service()
    print_header("{project_name}")
    print("System initialized. Ready for operations.")

    while True:
        print("\\n--- MAIN MENU ---")
        print("1. Add / Register New {e_class}")
        print("2. View All {e_class} Records")
        print("3. Search {e_class} by Name/Keyword")
        print("4. Update {e_class} Details")
        print("5. Delete {e_class} Record")
        print("6. Exit")

        choice = input("\\nEnter your choice (1-6): ").strip()

        if choice == "1":
            print_header("Register New {e_class}")
            rid = prompt_int("Enter ID: ")
            name = input("Enter Name: ").strip()
            category = input("Enter Category/Type [General]: ").strip() or "General"
            details = input("Enter Additional Details: ").strip()

            success, msg = service.register_{e_lower}(rid, name, category, details)
            print(f"\\n[{{'SUCCESS' if success else 'ERROR'}}] {{msg}}")

        elif choice == "2":
            print_header("All {e_class} Records")
            records = service.list_all_{e_lower}s()
            if not records:
                print("No records found in storage.")
            else:
                print(f"Total Records: {{len(records)}}\\n")
                print(f"{{'ID':<6}} | {{'Name':<20}} | {{'Category':<15}} | {{'Status':<10}}")
                print("-" * 58)
                for r in records:
                    print(f"{{r.record_id:<6}} | {{r.name:<20}} | {{r.category:<15}} | {{r.status:<10}}")

        elif choice == "3":
            print_header("Search {e_class}")
            query = input("Enter search keyword: ").strip()
            if not query:
                print("[!] Please provide a search keyword.")
                continue
            matches = service.search_{e_lower}s(query)
            if not matches:
                print(f"No records matching '{{query}}'.")
            else:
                print(f"Found {{len(matches)}} match(es):")
                for r in matches:
                    print(f"  - {{r}}")

        elif choice == "4":
            print_header("Update {e_class}")
            rid = prompt_int("Enter ID of {e_lower} to update: ")
            existing = service.get_{e_lower}_by_id(rid)
            if not existing:
                print(f"[!] No record found with ID {{rid}}.")
                continue

            print(f"Current Name: {{existing.name}}")
            name = input("New Name (press Enter to keep): ").strip() or existing.name
            category = input(f"New Category [{{existing.category}}]: ").strip() or existing.category
            details = input(f"New Details [{{existing.details}}]: ").strip() or existing.details
            status = input(f"New Status (Active/Inactive) [{{existing.status}}]: ").strip() or existing.status

            success, msg = service.update_{e_lower}(rid, name, category, details, status)
            print(f"\\n[{{'SUCCESS' if success else 'ERROR'}}] {{msg}}")

        elif choice == "5":
            print_header("Delete {e_class}")
            rid = prompt_int("Enter ID to delete: ")
            confirm = input(f"Are you sure you want to delete ID {{rid}}? (y/N): ").lower().strip()
            if confirm == 'y':
                success, msg = service.delete_{e_lower}(rid)
                print(f"\\n[{{'SUCCESS' if success else 'ERROR'}}] {{msg}}")
            else:
                print("Operation cancelled.")

        elif choice == "6":
            print("\\nThank you for using {project_name}. Goodbye!")
            sys.exit(0)
        else:
            print("[!] Invalid option. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
'''

    return [
        {
            "filename": "models.py",
            "module_name": "Data Model Module",
            "role": "Entity & Data Validation",
            "purpose": f"Defines the {e_class} class with constructor, validation, dictionary serialization, and string representation.",
            "code": models_code
        },
        {
            "filename": "storage.py",
            "module_name": "Storage / Persistence Module",
            "role": "Data Access & File Repository",
            "purpose": f"Handles reading and writing {e_class} records to persistent JSON storage with error recovery and lookup methods.",
            "code": storage_code
        },
        {
            "filename": "service.py",
            "module_name": "Service / Business Logic Module",
            "role": "Core Feature Operations",
            "purpose": f"Coordinates business rules, sanitizes input, and handles CRUD operations for requested features ({', '.join(features[:3])}).",
            "code": service_code
        },
        {
            "filename": "main.py",
            "module_name": "Application Entry Point",
            "role": "User Interface & Controller",
            "purpose": "Provides the interactive terminal CLI menu, guides user inputs, calls service functions, and prints structured tables.",
            "code": main_code
        }
    ]


def generate_java_modules(project_name, entity, features):
    e_class = entity.capitalize()
    e_lower = entity.lower()

    # File 1: Entity
    entity_code = f'''// {e_class}.java
package com.planner.{e_lower};

import java.io.Serializable;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Entity Model representing a {e_class} in {project_name}.
 */
public class {e_class} implements Serializable {{
    private static final long serialVersionUID = 1L;

    private int id;
    private String name;
    private String category;
    private String details;
    private String status;
    private String createdAt;

    public {e_class}(int id, String name, String category, String details) {{
        if (id <= 0) throw new IllegalArgumentException("ID must be positive.");
        if (name == null || name.trim().isEmpty()) throw new IllegalArgumentException("Name is required.");

        this.id = id;
        this.name = name.trim();
        this.category = (category == null || category.trim().isEmpty()) ? "General" : category.trim();
        this.details = (details == null) ? "" : details.trim();
        this.status = "Active";
        this.createdAt = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
    }}

    // Getters and Setters
    public int getId() {{ return id; }}
    public void setId(int id) {{ this.id = id; }}

    public String getName() {{ return name; }}
    public void setName(String name) {{ this.name = name; }}

    public String getCategory() {{ return category; }}
    public void setCategory(String category) {{ this.category = category; }}

    public String getDetails() {{ return details; }}
    public void setDetails(String details) {{ this.details = details; }}

    public String getStatus() {{ return status; }}
    public void setStatus(String status) {{ this.status = status; }}

    public String getCreatedAt() {{ return createdAt; }}

    @Override
    public String toString() {{
        return String.format("[%d] %s (%s) - Status: %s", id, name, category, status);
    }}
}}
'''

    # File 2: Repository
    repo_code = f'''// {e_class}Repository.java
package com.planner.{e_lower};

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Data Access Layer for {e_class} storage and querying.
 */
public class {e_class}Repository {{
    private final List<{e_class}> database = new ArrayList<>();

    public synchronized boolean add({e_class} item) {{
        if (findById(item.getId()).isPresent()) {{
            return false;
        }}
        return database.add(item);
    }}

    public Optional<{e_class}> findById(int id) {{
        return database.stream()
                .filter(item -> item.getId() == id)
                .findFirst();
    }}

    public List<{e_class}> findAll() {{
        return new ArrayList<>(database);
    }}

    public List<{e_class}> searchByName(String keyword) {{
        String q = keyword.toLowerCase();
        return database.stream()
                .filter(item -> item.getName().toLowerCase().contains(q) ||
                                item.getDetails().toLowerCase().contains(q))
                .collect(Collectors.toList());
    }}

    public synchronized boolean update({e_class} updated) {{
        for (int i = 0; i < database.size(); i++) {{
            if (database.get(i).getId() == updated.getId()) {{
                database.set(i, updated);
                return true;
            }}
        }}
        return false;
    }}

    public synchronized boolean delete(int id) {{
        return database.removeIf(item -> item.getId() == id);
    }}

    public int count() {{
        return database.size();
    }}
}}
'''

    # File 3: Service
    service_code = f'''// {e_class}Service.java
package com.planner.{e_lower};

import java.util.List;
import java.util.Optional;

/**
 * Service Layer for {project_name}.
 * Encapsulates business rules and operational workflows.
 */
public class {e_class}Service {{
    private final {e_class}Repository repository;

    public {e_class}Service({e_class}Repository repository) {{
        this.repository = repository;
    }}

    public String register(int id, String name, String category, String details) {{
        try {{
            {e_class} item = new {e_class}(id, name, category, details);
            boolean added = repository.add(item);
            if (!added) {{
                return "Error: ID " + id + " is already registered.";
            }}
            return "Success: " + item.getName() + " registered successfully.";
        }} catch (IllegalArgumentException e) {{
            return "Validation Error: " + e.getMessage();
        }}
    }}

    public List<{e_class}> listAll() {{
        return repository.findAll();
    }}

    public List<{e_class}> search(String query) {{
        return repository.searchByName(query);
    }}

    public Optional<{e_class}> getById(int id) {{
        return repository.findById(id);
    }}

    public String updateDetails(int id, String newName, String newCategory, String newDetails, String newStatus) {{
        Optional<{e_class}> existing = repository.findById(id);
        if (!existing.isPresent()) {{
            return "Error: Record with ID " + id + " not found.";
        }}

        {e_class} item = existing.get();
        if (newName != null && !newName.trim().isEmpty()) item.setName(newName.trim());
        if (newCategory != null && !newCategory.trim().isEmpty()) item.setCategory(newCategory.trim());
        if (newDetails != null) item.setDetails(newDetails.trim());
        if (newStatus != null && !newStatus.trim().isEmpty()) item.setStatus(newStatus.trim());

        repository.update(item);
        return "Success: Record ID " + id + " updated successfully.";
    }}

    public String remove(int id) {{
        if (repository.delete(id)) {{
            return "Success: Record ID " + id + " deleted.";
        }}
        return "Error: Record ID " + id + " could not be found.";
    }}
}}
'''

    # File 4: Main.java
    main_code = f'''// Main.java
package com.planner.{e_lower};

import java.util.List;
import java.util.Optional;
import java.util.Scanner;

/**
 * Main Application Entry Point for {project_name}.
 */
public class Main {{
    private static final Scanner scanner = new Scanner(System.in);
    private static final {e_class}Service service = new {e_class}Service(new {e_class}Repository());

    public static void main(String[] args) {{
        System.out.println("==================================================");
        System.out.println("   {project_name} - Java Edition");
        System.out.println("==================================================");

        boolean running = true;
        while (running) {{
            printMenu();
            System.out.print("Enter choice (1-6): ");
            String input = scanner.nextLine().trim();

            switch (input) {{
                case "1":
                    handleAdd();
                    break;
                case "2":
                    handleList();
                    break;
                case "3":
                    handleSearch();
                    break;
                case "4":
                    handleUpdate();
                    break;
                case "5":
                    handleDelete();
                    break;
                case "6":
                    System.out.println("Exiting application. Goodbye!");
                    running = false;
                    break;
                default:
                    System.out.println("[!] Invalid choice. Please choose 1 to 6.");
            }}
        }}
    }}

    private static void printMenu() {{
        System.out.println("\\n--- MAIN MENU ---");
        System.out.println("1. Register New {e_class}");
        System.out.println("2. View All {e_class} Records");
        System.out.println("3. Search {e_class} by Keyword");
        System.out.println("4. Update {e_class} Details");
        System.out.println("5. Delete {e_class} Record");
        System.out.println("6. Exit");
    }}

    private static void handleAdd() {{
        System.out.print("Enter ID: ");
        int id = Integer.parseInt(scanner.nextLine().trim());
        System.out.print("Enter Name: ");
        String name = scanner.nextLine().trim();
        System.out.print("Enter Category: ");
        String cat = scanner.nextLine().trim();
        System.out.print("Enter Details: ");
        String details = scanner.nextLine().trim();

        String res = service.register(id, name, cat, details);
        System.out.println(res);
    }}

    private static void handleList() {{
        List<{e_class}> all = service.listAll();
        if (all.isEmpty()) {{
            System.out.println("No records found.");
            return;
        }}
        System.out.printf("%-6s | %-20s | %-15s | %-10s%n", "ID", "Name", "Category", "Status");
        System.out.println("----------------------------------------------------------");
        for ({e_class} item : all) {{
            System.out.printf("%-6d | %-20s | %-15s | %-10s%n",
                    item.getId(), item.getName(), item.getCategory(), item.getStatus());
        }}
    }}

    private static void handleSearch() {{
        System.out.print("Enter keyword: ");
        String q = scanner.nextLine().trim();
        List<{e_class}> results = service.search(q);
        System.out.println("Found " + results.size() + " matches:");
        results.forEach(item -> System.out.println(" - " + item));
    }}

    private static void handleUpdate() {{
        System.out.print("Enter ID to update: ");
        int id = Integer.parseInt(scanner.nextLine().trim());
        Optional<{e_class}> opt = service.getById(id);
        if (!opt.isPresent()) {{
            System.out.println("Record not found.");
            return;
        }}
        {e_class} current = opt.get();
        System.out.print("New Name (" + current.getName() + "): ");
        String name = scanner.nextLine().trim();
        System.out.print("New Category (" + current.getCategory() + "): ");
        String cat = scanner.nextLine().trim();
        System.out.print("New Details: ");
        String det = scanner.nextLine().trim();
        System.out.print("New Status (" + current.getStatus() + "): ");
        String status = scanner.nextLine().trim();

        String msg = service.updateDetails(id, name, cat, det, status);
        System.out.println(msg);
    }}

    private static void handleDelete() {{
        System.out.print("Enter ID to delete: ");
        int id = Integer.parseInt(scanner.nextLine().trim());
        System.out.println(service.remove(id));
    }}
}}
'''

    return [
        {
            "filename": f"{e_class}.java",
            "module_name": "Domain Model",
            "role": "Encapsulated Entity Class",
            "purpose": f"Defines private member variables for {e_class}, constructors, getters/setters, validation, and serialization.",
            "code": entity_code
        },
        {
            "filename": f"{e_class}Repository.java",
            "module_name": "Data Access Repository",
            "role": "CRUD & Query Operations",
            "purpose": "Manages in-memory data store with thread-safe synchronized collections, stream-based searches, and filters.",
            "code": repo_code
        },
        {
            "filename": f"{e_class}Service.java",
            "module_name": "Business Service Layer",
            "role": "Business Rule Enforcement",
            "purpose": "Decouples presentation from data operations; validates inputs and coordinates feature workflows.",
            "code": service_code
        },
        {
            "filename": "Main.java",
            "module_name": "Interactive CLI Runner",
            "role": "User Interface & Controller",
            "purpose": "Interactive terminal scanner loop with menu navigation, formatted table display, and exception handling.",
            "code": main_code
        }
    ]


def generate_c_modules(project_name, entity, features):
    e_lower = entity.lower()
    e_upper = entity.upper()

    header_code = f'''/*
 * {e_lower}.h
 * Header file for {project_name}.
 * Defines constants, structures, and function prototypes.
 */

#ifndef {e_upper}_H
#define {e_upper}_H

#define MAX_NAME 50
#define MAX_CATEGORY 30
#define MAX_DETAILS 128
#define MAX_RECORDS 200

/* {entity} entity representation */
typedef struct {{
    int id;
    char name[MAX_NAME];
    char category[MAX_CATEGORY];
    char details[MAX_DETAILS];
    char status[20];
}} {entity};

/* System Database Structure */
typedef struct {{
    {entity} records[MAX_RECORDS];
    int count;
}} Database;

/* Function Prototypes */
void db_init(Database *db);
int db_add(Database *db, int id, const char *name, const char *category, const char *details);
{entity}* db_find_by_id(Database *db, int id);
void db_display_all(const Database *db);
void db_search(const Database *db, const char *keyword);
int db_update(Database *db, int id, const char *name, const char *category, const char *details, const char *status);
int db_delete(Database *db, int id);
int db_save_file(const Database *db, const char *filename);
int db_load_file(Database *db, const char *filename);

#endif /* {e_upper}_H */
'''

    source_code = f'''/*
 * {e_lower}.c
 * Core implementations for {project_name}.
 * Handles data validation, storage mutations, and file persistence.
 */

#include <stdio.h>
#include <string.h>
#include "{e_lower}.h"

void db_init(Database *db) {{
    db->count = 0;
}}

int db_add(Database *db, int id, const char *name, const char *category, const char *details) {{
    if (db->count >= MAX_RECORDS) {{
        printf("[Error] Storage full! Max capacity reached.\\n");
        return 0;
    }}
    if (db_find_by_id(db, id) != NULL) {{
        printf("[Error] Record with ID %d already exists.\\n", id);
        return 0;
    }}

    {entity} *item = &db->records[db->count];
    item->id = id;
    strncpy(item->name, name, MAX_NAME - 1);
    item->name[MAX_NAME - 1] = '\\0';

    strncpy(item->category, category, MAX_CATEGORY - 1);
    item->category[MAX_CATEGORY - 1] = '\\0';

    strncpy(item->details, details, MAX_DETAILS - 1);
    item->details[MAX_DETAILS - 1] = '\\0';

    strcpy(item->status, "Active");
    db->count++;
    return 1;
}}

{entity}* db_find_by_id(Database *db, int id) {{
    for (int i = 0; i < db->count; i++) {{
        if (db->records[i].id == id) {{
            return &db->records[i];
        }}
    }}
    return NULL;
}}

void db_display_all(const Database *db) {{
    if (db->count == 0) {{
        printf("No records found in database.\\n");
        return;
    }}

    printf("\\n%-6s | %-20s | %-15s | %-10s\\n", "ID", "Name", "Category", "Status");
    printf("----------------------------------------------------------\\n");
    for (int i = 0; i < db->count; i++) {{
        const {entity} *r = &db->records[i];
        printf("%-6d | %-20s | %-15s | %-10s\\n", r->id, r->name, r->category, r->status);
    }}
}}

void db_search(const Database *db, const char *keyword) {{
    int found = 0;
    printf("\\nSearching for '%s':\\n", keyword);
    for (int i = 0; i < db->count; i++) {{
        const {entity} *r = &db->records[i];
        if (strstr(r->name, keyword) != NULL || strstr(r->details, keyword) != NULL) {{
            printf(" - [%d] %s (%s) | Status: %s | Info: %s\\n",
                   r->id, r->name, r->category, r->status, r->details);
            found++;
        }}
    }}
    if (!found) {{
        printf("No matching records found.\\n");
    }}
}}

int db_update(Database *db, int id, const char *name, const char *category, const char *details, const char *status) {{
    {entity} *item = db_find_by_id(db, id);
    if (item == NULL) return 0;

    if (strlen(name) > 0) {{
        strncpy(item->name, name, MAX_NAME - 1);
        item->name[MAX_NAME - 1] = '\\0';
    }}
    if (strlen(category) > 0) {{
        strncpy(item->category, category, MAX_CATEGORY - 1);
        item->category[MAX_CATEGORY - 1] = '\\0';
    }}
    if (strlen(details) > 0) {{
        strncpy(item->details, details, MAX_DETAILS - 1);
        item->details[MAX_DETAILS - 1] = '\\0';
    }}
    if (strlen(status) > 0) {{
        strncpy(item->status, status, 19);
        item->status[19] = '\\0';
    }}
    return 1;
}}

int db_delete(Database *db, int id) {{
    int target = -1;
    for (int i = 0; i < db->count; i++) {{
        if (db->records[i].id == id) {{
            target = i;
            break;
        }}
    }}
    if (target == -1) return 0;

    // Shift remaining records
    for (int i = target; i < db->count - 1; i++) {{
        db->records[i] = db->records[i + 1];
    }}
    db->count--;
    return 1;
}}

int db_save_file(const Database *db, const char *filename) {{
    FILE *fp = fopen(filename, "wb");
    if (!fp) return 0;
    fwrite(&db->count, sizeof(int), 1, fp);
    fwrite(db->records, sizeof({entity}), db->count, fp);
    fclose(fp);
    return 1;
}}

int db_load_file(Database *db, const char *filename) {{
    FILE *fp = fopen(filename, "rb");
    if (!fp) return 0;
    fread(&db->count, sizeof(int), 1, fp);
    fread(db->records, sizeof({entity}), db->count, fp);
    fclose(fp);
    return 1;
}}
'''

    main_c_code = f'''/*
 * main.c
 * Terminal UI and Command Loop for {project_name}.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "{e_lower}.h"

#define DATA_FILE "{e_lower}s.dat"

void clear_stdin() {{
    int c;
    while ((c = getchar()) != '\\n' && c != EOF) {{ }}
}}

int main() {{
    Database db;
    db_init(&db);
    db_load_file(&db, DATA_FILE);

    printf("==================================================\\n");
    printf("   {project_name} (C Edition)\\n");
    printf("==================================================\\n");

    int choice = 0;
    while (1) {{
        printf("\\n--- MAIN MENU ---\\n");
        printf("1. Register New {entity}\\n");
        printf("2. View All {entity} Records\\n");
        printf("3. Search {entity}\\n");
        printf("4. Update {entity} Details\\n");
        printf("5. Delete {entity}\\n");
        printf("6. Save & Exit\\n");
        printf("Select an option (1-6): ");

        if (scanf("%d", &choice) != 1) {{
            printf("[!] Invalid input. Numbers only.\\n");
            clear_stdin();
            continue;
        }}
        clear_stdin();

        if (choice == 1) {{
            int id;
            char name[MAX_NAME], cat[MAX_CATEGORY], det[MAX_DETAILS];

            printf("Enter ID: ");
            scanf("%d", &id);
            clear_stdin();

            printf("Enter Name: ");
            fgets(name, MAX_NAME, stdin);
            name[strcspn(name, "\\n")] = '\\0';

            printf("Enter Category [General]: ");
            fgets(cat, MAX_CATEGORY, stdin);
            cat[strcspn(cat, "\\n")] = '\\0';
            if (strlen(cat) == 0) strcpy(cat, "General");

            printf("Enter Details: ");
            fgets(det, MAX_DETAILS, stdin);
            det[strcspn(det, "\\n")] = '\\0';

            if (db_add(&db, id, name, cat, det)) {{
                printf("[SUCCESS] Record registered successfully.\\n");
            }}

        }} else if (choice == 2) {{
            db_display_all(&db);

        }} else if (choice == 3) {{
            char q[MAX_NAME];
            printf("Enter search keyword: ");
            fgets(q, MAX_NAME, stdin);
            q[strcspn(q, "\\n")] = '\\0';
            db_search(&db, q);

        }} else if (choice == 4) {{
            int id;
            char name[MAX_NAME], cat[MAX_CATEGORY], det[MAX_DETAILS], st[20];
            printf("Enter ID to update: ");
            scanf("%d", &id);
            clear_stdin();

            {entity} *item = db_find_by_id(&db, id);
            if (!item) {{
                printf("[!] Record not found.\\n");
                continue;
            }}

            printf("New Name (leave blank to keep '%s'): ", item->name);
            fgets(name, MAX_NAME, stdin);
            name[strcspn(name, "\\n")] = '\\0';

            printf("New Category (leave blank to keep '%s'): ", item->category);
            fgets(cat, MAX_CATEGORY, stdin);
            cat[strcspn(cat, "\\n")] = '\\0';

            printf("New Details: ");
            fgets(det, MAX_DETAILS, stdin);
            det[strcspn(det, "\\n")] = '\\0';

            printf("New Status (Active/Inactive): ");
            fgets(st, 20, stdin);
            st[strcspn(st, "\\n")] = '\\0';

            if (db_update(&db, id, name, cat, det, st)) {{
                printf("[SUCCESS] Record updated.\\n");
            }}

        }} else if (choice == 5) {{
            int id;
            printf("Enter ID to delete: ");
            scanf("%d", &id);
            clear_stdin();

            if (db_delete(&db, id)) {{
                printf("[SUCCESS] Record deleted.\\n");
            }} else {{
                printf("[!] ID not found.\\n");
            }}

        }} else if (choice == 6) {{
            db_save_file(&db, DATA_FILE);
            printf("Data persisted to disk. Goodbye!\\n");
            break;

        }} else {{
            printf("[!] Invalid choice. Please pick 1-6.\\n");
        }}
    }}

    return 0;
}}
'''

    return [
        {
            "filename": f"{e_lower}.h",
            "module_name": "Header & Declarations",
            "role": "Type Definitions & Prototypes",
            "purpose": f"Defines {entity} struct, Database container, and prototypes for memory-safe CRUD operations.",
            "code": header_code
        },
        {
            "filename": f"{e_lower}.c",
            "module_name": "Core Implementation",
            "role": "Business Operations & Storage",
            "purpose": "Implements validation, array operations, linear searches, and binary file save/load functions.",
            "code": source_code
        },
        {
            "filename": "main.c",
            "module_name": "Main Program",
            "role": "Interactive Console UI",
            "purpose": "Interactive menu driver utilizing fgets and safe input parsing with file persistence on exit.",
            "code": main_c_code
        }
    ]


def generate_js_modules(project_name, entity, features):
    e_class = entity.capitalize()
    e_lower = entity.lower()

    # Module 1: Model
    model_code = f'''/**
 * models/{e_class}.js
 * Domain Model for {project_name}.
 */

class {e_class} {{
    constructor({{ id, name, category = "General", details = "", status = "Active", createdAt = null }}) {{
        if (!id || isNaN(id)) throw new Error("A valid numeric ID is required.");
        if (!name || !name.trim()) throw new Error("Name cannot be blank.");

        this.id = parseInt(id, 10);
        this.name = name.trim();
        this.category = category.trim();
        this.details = details.trim();
        this.status = status.trim();
        this.createdAt = createdAt || new Date().toISOString();
    }}

    toJSON() {{
        return {{
            id: this.id,
            name: this.name,
            category: this.category,
            details: this.details,
            status: this.status,
            createdAt: this.createdAt
        }};
    }}

    static fromJSON(json) {{
        return new {e_class}(json);
    }}
}}

module.exports = {e_class};
'''

    # Module 2: Store
    storage_code = f'''/**
 * storage/dataStore.js
 * Persistent File & Memory Storage for {project_name}.
 */

const fs = require("fs");
const path = require("path");
const {e_class} = require("../models/{e_class}");

class DataStore {{
    constructor(filePath = "{e_lower}s.json") {{
        this.filePath = path.resolve(process.cwd(), filePath);
        this.records = [];
        this.load();
    }}

    load() {{
        try {{
            if (fs.existsSync(this.filePath)) {{
                const raw = fs.readFileSync(this.filePath, "utf-8");
                const parsed = JSON.parse(raw);
                this.records = parsed.map(item => {e_class}.fromJSON(item));
            }}
        }} catch (err) {{
            console.warn("[Warning] Could not read storage file, initializing empty:", err.message);
            this.records = [];
        }}
    }}

    save() {{
        try {{
            const data = this.records.map(r => r.toJSON());
            fs.writeFileSync(this.filePath, JSON.stringify(data, null, 2), "utf-8");
            return true;
        }} catch (err) {{
            console.error("[Error] Failed to write to disk:", err.message);
            return false;
        }}
    }}

    add(entity) {{
        if (this.findById(entity.id)) {{
            throw new Error(`Record with ID ${{entity.id}} already exists.`);
        }}
        this.records.push(entity);
        return this.save();
    }}

    findById(id) {{
        return this.records.find(r => r.id === parseInt(id, 10)) || null;
    }}

    findAll() {{
        return [...this.records];
    }}

    search(query) {{
        const q = query.toLowerCase();
        return this.records.filter(r =>
            r.name.toLowerCase().includes(q) ||
            r.details.toLowerCase().includes(q)
        );
    }}

    update(updatedEntity) {{
        const index = this.records.findIndex(r => r.id === updatedEntity.id);
        if (index === -1) return false;
        this.records[index] = updatedEntity;
        return this.save();
    }}

    delete(id) {{
        const initial = this.records.length;
        this.records = this.records.filter(r => r.id !== parseInt(id, 10));
        if (this.records.length < initial) {{
            this.save();
            return true;
        }}
        return false;
    }}
}}

module.exports = DataStore;
'''

    # Module 3: Service
    service_code = f'''/**
 * services/{e_lower}Service.js
 * Business Logic Layer for {project_name}.
 */

const {e_class} = require("../models/{e_class}");
const DataStore = require("../storage/dataStore");

class {e_class}Service {{
    constructor(store = new DataStore()) {{
        this.store = store;
    }}

    register(id, name, category, details) {{
        try {{
            const record = new {e_class}({{ id, name, category, details }});
            this.store.add(record);
            return {{ success: true, message: `Successfully registered ${{record.name}} (ID: ${{id}}).` }};
        }} catch (err) {{
            return {{ success: false, message: err.message }};
        }}
    }}

    listAll() {{
        return this.store.findAll();
    }}

    search(query) {{
        return this.store.search(query);
    }}

    getById(id) {{
        return this.store.findById(id);
    }}

    update(id, updates) {{
        const existing = this.store.findById(id);
        if (!existing) {{
            return {{ success: false, message: `No record found with ID ${{id}}` }};
        }}
        const updated = new {e_class}({{
            ...existing.toJSON(),
            ...updates,
            id: existing.id
        }});
        this.store.update(updated);
        return {{ success: true, message: `Record ID ${{id}} successfully updated.` }};
    }}

    remove(id) {{
        const ok = this.store.delete(id);
        return ok
            ? {{ success: true, message: `Record ID ${{id}} removed.` }}
            : {{ success: false, message: `Record ID ${{id}} not found.` }};
    }}
}}

module.exports = {e_class}Service;
'''

    # Module 4: CLI Index
    cli_code = f'''/**
 * index.js
 * Main Interactive Terminal Application for {project_name}.
 */

const readline = require("readline");
const {e_class}Service = require("./services/{e_lower}Service");

const service = new {e_class}Service();
const rl = readline.createInterface({{
    input: process.stdin,
    output: process.stdout
}});

function prompt(query) {{
    return new Promise(resolve => rl.question(query, resolve));
}}

async function printMenu() {{
    console.log("\\n==================================================");
    console.log("   {project_name} (Node.js)");
    console.log("==================================================");
    console.log("1. Register New {e_class}");
    console.log("2. View All {e_class} Records");
    console.log("3. Search {e_class}");
    console.log("4. Update {e_class} Details");
    console.log("5. Delete {e_class}");
    console.log("6. Exit");
}}

async function main() {{
    let active = true;
    while (active) {{
        await printMenu();
        const choice = (await prompt("Choose an option (1-6): ")).trim();

        switch (choice) {{
            case "1": {{
                const id = await prompt("Enter ID: ");
                const name = await prompt("Enter Name: ");
                const cat = await prompt("Enter Category [General]: ") || "General";
                const details = await prompt("Enter Details: ");
                const result = service.register(id, name, cat, details);
                console.log(`\\n[${{result.success ? "SUCCESS" : "ERROR"}}] ${{result.message}}`);
                break;
            }}
            case "2": {{
                const all = service.listAll();
                console.log(`\\nTotal Records: ${{all.length}}`);
                if (all.length > 0) {{
                    console.table(all.map(r => r.toJSON()));
                }}
                break;
            }}
            case "3": {{
                const q = await prompt("Enter search keyword: ");
                const matches = service.search(q);
                console.log(`\\nFound ${{matches.length}} match(es):`);
                matches.forEach(m => console.log(` - [${{m.id}}] ${{m.name}} (${{m.category}}) - ${{m.status}}`));
                break;
            }}
            case "4": {{
                const id = await prompt("Enter ID to update: ");
                const existing = service.getById(id);
                if (!existing) {{
                    console.log("[!] Record not found.");
                    break;
                }}
                const name = await prompt(`New Name [${{existing.name}}]: `) || existing.name;
                const category = await prompt(`New Category [${{existing.category}}]: `) || existing.category;
                const details = await prompt(`New Details [${{existing.details}}]: `) || existing.details;
                const status = await prompt(`New Status [${{existing.status}}]: `) || existing.status;

                const res = service.update(id, {{ name, category, details, status }});
                console.log(`\\n[${{res.success ? "SUCCESS" : "ERROR"}}] ${{res.message}}`);
                break;
            }}
            case "5": {{
                const id = await prompt("Enter ID to delete: ");
                const res = service.remove(id);
                console.log(`\\n[${{res.success ? "SUCCESS" : "ERROR"}}] ${{res.message}}`);
                break;
            }}
            case "6":
                console.log("Shutting down. Goodbye!");
                active = false;
                rl.close();
                break;
            default:
                console.log("[!] Invalid selection. Please pick 1-6.");
        }}
    }}
}}

main().catch(err => {{
    console.error("Fatal error:", err);
    rl.close();
}});
'''

    return [
        {
            "filename": f"models/{e_class}.js",
            "module_name": "Entity Data Model",
            "role": "Model & Validation",
            "purpose": f"Encapsulates {e_class} domain attributes, validation checks, and JSON serialization methods.",
            "code": model_code
        },
        {
            "filename": "storage/dataStore.js",
            "module_name": "Persistence Layer",
            "role": "Filesystem / JSON Storage",
            "purpose": "Manages persistent read/write operations using Node.js fs module with in-memory caching.",
            "code": storage_code
        },
        {
            "filename": f"services/{e_lower}Service.js",
            "module_name": "Service / Business Logic",
            "role": "Core Feature Handlers",
            "purpose": f"Coordinates validation, search algorithms, mutations, and error handling for features.",
            "code": service_code
        },
        {
            "filename": "index.js",
            "module_name": "Main CLI Driver",
            "role": "Console UI & Event Loop",
            "purpose": "Uses readline and async/await to render interactive CLI menus and console.table output.",
            "code": cli_code
        }
    ]


def generate_folder_tree(language, entity):
    e_lower = entity.lower()
    e_class = entity.capitalize()

    if language == "Python":
        return f"""{e_lower}_project/
├── models.py       # Domain entity, attributes, validation & serialization
├── storage.py      # JSON file persistence & data access repository
├── service.py      # Business logic service handling requested features
├── main.py         # Main entry point & interactive CLI interface
└── {e_lower}s.json     # Auto-generated persistent storage file"""

    elif language == "Java":
        return f"""{e_lower}_project/
└── src/
    └── com/
        └── planner/
            └── {e_lower}/
                ├── {e_class}.java           # Encapsulated Entity Model
                ├── {e_class}Repository.java # Data Access & Query Repository
                ├── {e_class}Service.java    # Business Logic Layer
                └── Main.java              # Entry Point & CLI Scanner Menu"""

    elif language == "C":
        return f"""{e_lower}_project/
├── {e_lower}.h       # Struct definitions, constants & function prototypes
├── {e_lower}.c       # Data storage operations & file serialization
├── main.c          # Console UI menu driver and command loop
└── {e_lower}s.dat     # Binary file storage for persistent records"""

    else: # JavaScript
        return f"""{e_lower}_project/
├── package.json           # Node.js project manifest & scripts
├── index.js               # CLI interface & interactive menu loop
├── models/
│   └── {e_class}.js        # Domain Model with schema & validation
├── storage/
│   └── dataStore.js       # Persistent JSON store manager
├── services/
│   └── {e_lower}Service.js # Business rules & operation workflows
└── {e_lower}s.json         # Auto-generated data file"""


# ==============================================================================
# 13-SECTION PROJECT PLAN GENERATOR
# ==============================================================================

def generate_complete_plan(name, description, language):
    """
    Produces a comprehensive, professional 13-section software engineering plan
    along with full modular code files and folder structure.
    """
    clean_name = name.strip()
    features = parse_features(description)
    entity = extract_entity_name(clean_name, features)

    # Complexity calculation
    count = len(features)
    extra_days = 0
    desc_lower = description.lower()
    keywords = ["payment", "security", "chat", "notification", "ai", "api", "auth", "token", "export"]
    for kw in keywords:
        if kw in desc_lower:
            extra_days += 2

    estimated_days = max(7, 5 + (count * 2) + extra_days)
    estimated_weeks = round(estimated_days / 7, 1)

    # Categorize features for FRs
    categorized = categorize_features(features, entity)

    # Technology Stack
    if language == "Python":
        frontend = "CLI Console Interface / HTML5 & Jinja2 (Web Interface)"
        backend = "Python 3 (Standard Library / Flask Microframework)"
        database = "JSON Storage / SQLite3 Relational Database"
        tools = "Python 3.10+, VS Code / PyCharm, pytest, Git Version Control"
    elif language == "Java":
        frontend = "Console Scanner CLI / JavaFX Modern Desktop GUI"
        backend = "Java SE 17+ (Core OOP, Collections, Streams, I/O)"
        database = "File Serialization / MySQL Database via JDBC"
        tools = "JDK 17+, IntelliJ IDEA / Eclipse, JUnit 5, Maven"
    elif language == "C":
        frontend = "Standard Terminal Output with ANSI Formatting"
        backend = "C99 / C11 Standard Library (POSIX Compliant)"
        database = "Binary File I/O (`fread`/`fwrite`) / In-Memory Struct Array"
        tools = "GCC / Clang Compiler, Make / CMake, GDB Debugger, VS Code"
    else: # JavaScript
        frontend = "Interactive Node.js CLI / HTML5, TailwindCSS & Vanilla JS"
        backend = "Node.js (LTS) / Express.js Modular Architecture"
        database = "JSON File Persistence / NeDB / MongoDB"
        tools = "Node.js 18+, npm / yarn, VS Code, Jest / Mocha"

    # Section 1: Title
    title = f"{clean_name} – Software Development Plan & Architecture"

    # Section 2: Project Overview
    overview = (
        f"{clean_name} is a comprehensive software engineering solution built using {language}. "
        f"The primary goal of this application is to streamline, automate, and organize operations relating "
        f"to {entity.lower()} management. By replacing manual, fragmented, or error-prone processes, "
        f"the system provides a reliable and modular framework that guarantees structured data retention, "
        f"rapid lookup capabilities, and intuitive user interactions. The application is architected with "
        f"separation of concerns, isolating data models, persistence layers, and user presentation interfaces."
    )

    # Section 3: Problem Statement
    problem_statement = (
        f"Traditional and manual tracking of {entity.lower()} operations frequently suffers from "
        f"human recording errors, inconsistent data formats, lack of search indexing, and high retrieval times. "
        f"Without a centralized software system, maintaining audit trails, updating records dynamically, "
        f"and generating on-demand summary reports becomes tedious and inefficient. {clean_name} directly addresses "
        f"these challenges by introducing a digital, standardized, and automated workflow."
    )

    # Section 4: Objectives
    objectives = [
        f"Design an intuitive and fail-safe system for managing all {entity.lower()} records.",
        f"Implement modular and reusable code architecture adhering to {language} best practices.",
        f"Ensure persistent and reliable data storage to prevent loss across application restarts.",
        f"Provide comprehensive search, filtering, update, and deletion mechanisms.",
        f"Incorporate robust input validation to guard against corrupted or invalid user inputs.",
        f"Deliver complete, ready-to-present technical documentation suitable for college evaluation."
    ]

    # Section 5: Functional Requirements
    functional_requirements = []
    fr_counter = 1

    # Add core user features
    for feat in features:
        functional_requirements.append({
            "id": f"FR-{fr_counter:02d}",
            "title": feat,
            "description": f"The system shall provide a dedicated workflow allowing users to execute: {feat}."
        })
        fr_counter += 1

    # Ensure essential CRUD & Search are explicitly documented
    if not any("search" in fr["title"].lower() for fr in functional_requirements):
        functional_requirements.append({
            "id": f"FR-{fr_counter:02d}",
            "title": f"Search & Filter {entity} Records",
            "description": f"The system shall allow users to search {entity.lower()}s by keyword, identifier, or category."
        })
        fr_counter += 1

    if not any("report" in fr["title"].lower() or "view" in fr["title"].lower() for fr in functional_requirements):
        functional_requirements.append({
            "id": f"FR-{fr_counter:02d}",
            "title": "Tabular Data Display & Reporting",
            "description": "The system shall display active records in a clean tabular view with status indicators."
        })
        fr_counter += 1

    # Section 6: Non-Functional Requirements
    non_functional_requirements = [
        {"category": "Performance", "requirement": "Response times for standard record queries and mutations must complete within 200ms."},
        {"category": "Reliability", "requirement": "Gracefully handle missing files, corrupted records, and invalid inputs without crashing."},
        {"category": "Usability", "requirement": "Provide self-explanatory menus, clear error prompts, and confirmation before destructive actions."},
        {"category": "Maintainability", "requirement": "Adhere to modular separation so models, storage, and logic can be modified independently."},
        {"category": "Portability", "requirement": f"Execute smoothly across standard operating systems supporting {language}."}
    ]

    # Section 7: System Modules
    system_modules = [
        f"{entity} Domain Entity Model",
        "Data Persistence & Storage Repository",
        "Business Logic & Service Layer",
        "User Interface & Controller Manager",
        "Input Validation & Exception Handler"
    ]

    # Section 8: Module Descriptions
    module_descriptions = [
        {
            "name": f"1. {entity} Entity Model",
            "role": "Data Encapsulation & Schema",
            "inputs": f"Record attributes (ID, name, category, details, timestamp)",
            "outputs": "Validated entity object with serialization methods",
            "description": f"Defines the fundamental data structure for {entity.lower()}s. Guarantees mandatory fields are present and valid."
        },
        {
            "name": "2. Storage Repository",
            "role": "Persistence & Query Management",
            "inputs": "Entity objects, ID queries, search terms",
            "outputs": "Persistent records on disk (JSON/Binary/DB) and record collections",
            "description": "Abstracts file and database operations. Implements CRUD methods (add, find, update, remove) with file error recovery."
        },
        {
            "name": "3. Business Logic Service",
            "role": "Rules & Feature Execution",
            "inputs": "Parsed user requests and form parameters",
            "outputs": "Operation status flags and user-friendly response messages",
            "description": f"Coordinates requested features ({', '.join(features[:3])}). Enforces uniqueness, business constraints, and workflow order."
        },
        {
            "name": "4. User Interface Controller",
            "role": "Presentation & Interaction",
            "inputs": "Keyboard inputs, menu choices, search strings",
            "outputs": "Formatted data tables, prompts, and status alerts",
            "description": "Guides the user through an interactive menu loop, validates inputs prior to dispatch, and renders results."
        }
    ]

    # Section 9: Technology Requirements
    tech_requirements = {
        "frontend": frontend,
        "backend": backend,
        "database": database,
        "tools": tools
    }

    # Section 10: Implementation Steps (Roadmap)
    roadmap = [
        {
            "stage": "Phase 1: Requirements & Specification",
            "details": f"Analyze functional requirements for {clean_name}. Formalize schema for {entity.lower()} records and inputs.",
            "days": 2
        },
        {
            "stage": "Phase 2: Architecture & Data Modeling",
            "details": f"Construct domain model files ({entity} entity) with validation rules, getters/setters, and serialization.",
            "days": 2
        },
        {
            "stage": "Phase 3: Persistence & Storage Layer",
            "details": "Implement file read/write repositories, handle exceptions (missing files, syntax corruption), and verify CRUD integrity.",
            "days": 2
        },
        {
            "stage": "Phase 4: Core Feature Implementation",
            "details": f"Develop business service workflows for requested features: {', '.join(features)}.",
            "days": max(3, count * 2)
        },
        {
            "stage": "Phase 5: UI & CLI Integration",
            "details": "Build interactive menu loops, input parsing, formatted output tables, and delete confirmations.",
            "days": 2
        },
        {
            "stage": "Phase 6: Testing, Edge Cases & Documentation",
            "details": "Execute unit and integration tests, verify persistence across restarts, and prepare college viva presentation.",
            "days": 2
        }
    ]

    # Section 11: Folder Structure
    folder_tree = generate_folder_tree(language, entity)

    # Section 12: Testing Approach
    testing_approach = [
        {
            "type": "Unit Testing",
            "scope": "Models & Validation Logic",
            "description": f"Verify that invalid {entity.lower()} IDs (<= 0) or blank names raise expected validation errors."
        },
        {
            "type": "Persistence Testing",
            "scope": "Storage Layer",
            "description": "Verify that creating records persists them to disk, and restarting the program reloads data without loss."
        },
        {
            "type": "Boundary & Edge Case Testing",
            "scope": "Input Sanitization",
            "description": "Test blank inputs, special characters, duplicate IDs, non-existent ID lookups, and cancel operations."
        },
        {
            "type": "Integration & Workflow Testing",
            "scope": "End-to-End Features",
            "description": f"Execute complete lifecycle: Register {entity} -> Search -> Update details -> Display table -> Delete."
        }
    ]

    # Section 13: Expected Output
    expected_output = (
        f"Upon execution, {clean_name} launches an interactive console interface displaying a structured menu. "
        f"Users can select numerical options to register new {entity.lower()}s, view formatted tabular summaries, "
        f"perform instant keyword searches across stored data, edit existing records with retained defaults, "
        f"and safely remove obsolete entries. All changes persist automatically to file storage."
    )

    # Generate Modular Source Code based on language
    if language == "Python":
        modules = generate_python_modules(clean_name, entity, features)
    elif language == "Java":
        modules = generate_java_modules(clean_name, entity, features)
    elif language == "C":
        modules = generate_c_modules(clean_name, entity, features)
    else:
        modules = generate_js_modules(clean_name, entity, features)

    # Build primary unified sample code for legacy compatibility
    primary_code = "\n\n".join([
        f"# ==========================================\n# File: {m['filename']} ({m['module_name']})\n# ==========================================\n" + m["code"]
        for m in modules
    ])

    return {
        "title": title,
        "overview": overview,
        "problem_statement": problem_statement,
        "objectives": objectives,
        "functional_requirements": functional_requirements,
        "non_functional_requirements": non_functional_requirements,
        "system_modules": system_modules,
        "module_descriptions": module_descriptions,
        "tech_requirements": tech_requirements,
        "roadmap": roadmap,
        "folder_tree": folder_tree,
        "testing_approach": testing_approach,
        "expected_output": expected_output,
        "estimated_days": estimated_days,
        "estimated_weeks": estimated_weeks,
        "entity": entity,
        "features": features,
        "modules": modules,
        # Legacy backward-compatible keys
        "summary": overview,
        "frontend": frontend,
        "backend": backend,
        "database": database,
        "code": primary_code
    }


def normalize_plan(raw_plan, project_name, language):
    """
    Ensures plans retrieved from the database (both old legacy format and new format)
    have all required keys for the enhanced template.
    """
    if not isinstance(raw_plan, dict):
        try:
            plan = json.loads(raw_plan)
        except Exception:
            plan = {}
    else:
        plan = dict(raw_plan)

    # If this is already a new plan with modules and all 13 sections, return it
    if "modules" in plan and "functional_requirements" in plan and "objectives" in plan:
        return plan

    # Otherwise, migrate/upgrade legacy plan on the fly!
    features = plan.get("features", [])
    if not features and "summary" in plan:
        features = parse_features(project_name)

    entity = extract_entity_name(project_name, features)

    # Regenerate fresh 13-section plan with modular code
    enhanced = generate_complete_plan(project_name, ", ".join(features), language)

    # Preserve any user customization if present
    if "estimated_days" in plan:
        enhanced["estimated_days"] = plan["estimated_days"]
        enhanced["estimated_weeks"] = plan.get("estimated_weeks", round(plan["estimated_days"] / 7, 1))

    return enhanced

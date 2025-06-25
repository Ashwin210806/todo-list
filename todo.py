import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class TodoItem:
    def __init__(self, task: str, priority: str = "medium", due_date: Optional[str] = None):
        self.id = None
        self.task = task
        self.completed = False
        self.priority = priority.lower()
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.due_date = due_date
        self.completed_at = None
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'task': self.task,
            'completed': self.completed,
            'priority': self.priority,
            'created_at': self.created_at,
            'due_date': self.due_date,
            'completed_at': self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        item = cls(data['task'], data['priority'], data['due_date'])
        item.id = data['id']
        item.completed = data['completed']
        item.created_at = data['created_at']
        item.completed_at = data['completed_at']
        return item

class TodoManager:
    def __init__(self, filename: str = "todos.json"):
        self.filename = filename
        self.todos: List[TodoItem] = []
        self.next_id = 1
        self.load_todos()
    
    def load_todos(self):
        """Load todos from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.todos = [TodoItem.from_dict(item) for item in data.get('todos', [])]
                    self.next_id = data.get('next_id', 1)
            except (json.JSONDecodeError, FileNotFoundError):
                self.todos = []
                self.next_id = 1
    
    def save_todos(self):
        """Save todos to JSON file"""
        data = {
            'todos': [todo.to_dict() for todo in self.todos],
            'next_id': self.next_id
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_todo(self, task: str, priority: str = "medium", due_date: Optional[str] = None) -> int:
        """Add a new todo item"""
        if priority not in ["low", "medium", "high"]:
            priority = "medium"
        
        todo = TodoItem(task, priority, due_date)
        todo.id = self.next_id
        self.todos.append(todo)
        self.next_id += 1
        self.save_todos()
        return todo.id
    
    def remove_todo(self, todo_id: int) -> bool:
        """Remove a todo item by ID"""
        for i, todo in enumerate(self.todos):
            if todo.id == todo_id:
                del self.todos[i]
                self.save_todos()
                return True
        return False
    
    def complete_todo(self, todo_id: int) -> bool:
        """Mark a todo as completed"""
        for todo in self.todos:
            if todo.id == todo_id:
                todo.completed = True
                todo.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_todos()
                return True
        return False
    
    def uncomplete_todo(self, todo_id: int) -> bool:
        """Mark a todo as not completed"""
        for todo in self.todos:
            if todo.id == todo_id:
                todo.completed = False
                todo.completed_at = None
                self.save_todos()
                return True
        return False
    
    def get_todos(self, show_completed: bool = True, priority_filter: Optional[str] = None) -> List[TodoItem]:
        """Get todos with optional filtering"""
        filtered_todos = self.todos
        
        if not show_completed:
            filtered_todos = [todo for todo in filtered_todos if not todo.completed]
        
        if priority_filter:
            filtered_todos = [todo for todo in filtered_todos if todo.priority == priority_filter.lower()]
        
        return sorted(filtered_todos, key=lambda x: (x.completed, x.priority != "high", x.priority != "medium"))
    
    def update_todo(self, todo_id: int, task: Optional[str] = None, priority: Optional[str] = None, due_date: Optional[str] = None) -> bool:
        """Update an existing todo"""
        for todo in self.todos:
            if todo.id == todo_id:
                if task:
                    todo.task = task
                if priority and priority.lower() in ["low", "medium", "high"]:
                    todo.priority = priority.lower()
                if due_date is not None:
                    todo.due_date = due_date
                self.save_todos()
                return True
        return False

def display_todos(todos: List[TodoItem]):
    """Display todos in a formatted table"""
    if not todos:
        print("No todos found.")
        return
    
    print("\n" + "="*80)
    print(f"{'ID':<4} {'Status':<10} {'Priority':<10} {'Task':<30} {'Due Date':<15}")
    print("="*80)
    
    for todo in todos:
        status = "✓ Done" if todo.completed else "○ Pending"
        priority_display = f"[{todo.priority.upper()}]"
        due_display = todo.due_date if todo.due_date else "No due date"
        task_display = todo.task[:30] + "..." if len(todo.task) > 30 else todo.task
        
        print(f"{todo.id:<4} {status:<10} {priority_display:<10} {task_display:<30} {due_display:<15}")
    
    print("="*80)

def main():
    """Main CLI interface"""
    manager = TodoManager()
    
    while True:
        print("\n📝 To-Do List Manager")
        print("1. Add todo")
        print("2. View todos")
        print("3. Complete todo")
        print("4. Remove todo")
        print("5. Update todo")
        print("6. View pending todos only")
        print("7. Filter by priority")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == '1':
            task = input("Enter task: ").strip()
            if not task:
                print("Task cannot be empty!")
                continue
            
            priority = input("Enter priority (low/medium/high) [default: medium]: ").strip() or "medium"
            due_date = input("Enter due date (YYYY-MM-DD) [optional]: ").strip() or None
            
            todo_id = manager.add_todo(task, priority, due_date)
            print(f"✅ Todo added with ID: {todo_id}")
        
        elif choice == '2':
            todos = manager.get_todos()
            display_todos(todos)
        
        elif choice == '3':
            try:
                todo_id = int(input("Enter todo ID to complete: "))
                if manager.complete_todo(todo_id):
                    print("✅ Todo marked as completed!")
                else:
                    print("❌ Todo not found!")
            except ValueError:
                print("❌ Please enter a valid ID number!")
        
        elif choice == '4':
            try:
                todo_id = int(input("Enter todo ID to remove: "))
                if manager.remove_todo(todo_id):
                    print("✅ Todo removed!")
                else:
                    print("❌ Todo not found!")
            except ValueError:
                print("❌ Please enter a valid ID number!")
        
        elif choice == '5':
            try:
                todo_id = int(input("Enter todo ID to update: "))
                task = input("Enter new task (press Enter to keep current): ").strip() or None
                priority = input("Enter new priority (low/medium/high, press Enter to keep current): ").strip() or None
                due_date = input("Enter new due date (YYYY-MM-DD, press Enter to keep current): ").strip()
                due_date = due_date if due_date else None
                
                if manager.update_todo(todo_id, task, priority, due_date):
                    print("✅ Todo updated!")
                else:
                    print("❌ Todo not found!")
            except ValueError:
                print("❌ Please enter a valid ID number!")
        
        elif choice == '6':
            todos = manager.get_todos(show_completed=False)
            display_todos(todos)
        
        elif choice == '7':
            priority = input("Enter priority to filter by (low/medium/high): ").strip().lower()
            if priority in ["low", "medium", "high"]:
                todos = manager.get_todos(priority_filter=priority)
                display_todos(todos)
            else:
                print("❌ Invalid priority! Use low, medium, or high.")
        
        elif choice == '8':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice! Please enter 1-8.")

if __name__ == "__main__":
    main()
# CLI Rich Enhancement - Quick Reference

## Quick Start

### Import and Use

```python
# From interactive.py
from src.cli.interactive import (
    display_welcome_banner,
    display_progress_bar,
    display_success_box,
    display_stage_progress,
)

# From utils.py
from src.cli.utils import (
    print_header,
    print_success,
    create_status_table,
    print_step,
)
```

---

## Common Patterns

### 1. Display Welcome

```python
display_welcome_banner("U-AIP Scoping Assistant")
```

### 2. Show Progress

```python
# Progress bar
display_progress_bar(current=3, total=5, label="Stages")

# Stage progress
display_stage_progress(current_stage=2, total_stages=5)

# Step progress
print_step(1, 5, "Loading data")
```

### 3. Display Messages

```python
# Success
print_success("Operation completed!")
display_success_box("Success", "Your session was created")

# Error
print_error("Operation failed!")
display_error_box("Error", "Database connection failed")

# Warning
print_warning("Please review this")
display_warning_box("Warning", "This action cannot be undone")

# Info
print_info("Important information")
display_info_box("Info", "Your session is active")
```

### 4. Display Data

```python
# Key-value pairs
display_key_value_pairs({
    "Session ID": "abc123",
    "Status": "Active",
    "Stage": "2/5"
})

# List items
display_list_items(["Item 1", "Item 2", "Item 3"])

# Table
data = [
    {"Name": "Project A", "Status": "Active"},
    {"Name": "Project B", "Status": "Completed"},
]
table = create_status_table(data, title="Projects")
console.print(table)
```

### 5. Display Boxes

```python
# Simple box
print_box("Your content here", title="Title")

# Styled box
display_info_box("Title", "Content", style="cyan")
display_success_box("Success", "Operation completed!")
display_error_box("Error", "Something went wrong")
display_warning_box("Warning", "Please review")
```

---

## Function Reference

### Interactive Module

| Function | Purpose |
|----------|---------|
| `display_welcome_banner()` | Show welcome banner |
| `display_progress_bar()` | Show progress bar |
| `display_stage_progress()` | Show stage progress |
| `display_info_box()` | Show info box |
| `display_success_box()` | Show success box |
| `display_error_box()` | Show error box |
| `display_warning_box()` | Show warning box |
| `display_key_value_pairs()` | Show key-value table |
| `display_list_items()` | Show bullet list |
| `display_code_block()` | Show code with syntax |
| `display_markdown_content()` | Show markdown |
| `display_spinner_task()` | Show spinner |
| `display_comparison_table()` | Show comparison |
| `display_tree_structure()` | Show tree |

### Utils Module

| Function | Purpose |
|----------|---------|
| `print_header()` | Print header |
| `print_section()` | Print section |
| `print_success()` | Print success |
| `print_error()` | Print error |
| `print_warning()` | Print warning |
| `print_info()` | Print info |
| `print_step()` | Print step |
| `create_status_table()` | Create table |
| `create_key_value_table()` | Create KV table |
| `create_progress_bar()` | Create progress |
| `display_tree()` | Display tree |
| `format_duration()` | Format time |
| `format_size()` | Format bytes |
| `create_status_indicator()` | Create indicator |
| `create_stage_indicator()` | Create stage |
| `print_loading_spinner()` | Show spinner |
| `print_box()` | Print box |
| `print_divider()` | Print divider |
| `print_centered()` | Print centered |
| `print_bullet_list()` | Print bullets |

---

## Color Codes

```python
# Use in strings
"[cyan]Cyan text[/cyan]"
"[green]Green text[/green]"
"[yellow]Yellow text[/yellow]"
"[red]Red text[/red]"
"[white]White text[/white]"
"[dim]Dim text[/dim]"
"[bold]Bold text[/bold]"
"[bold cyan]Bold cyan[/bold cyan]"
```

---

## Icons

```
✓ - Success/Completed
✗ - Error/Failed
► - Current/In Progress
○ - Pending
⚠ - Warning
ℹ - Information
🚀 - Start/Launch
📋 - List
📊 - Data
📄 - Document
🎯 - Goal
💾 - Save
⏸ - Pause
🎉 - Celebration
```

---

## Examples

### Example 1: Session Creation

```python
from src.cli.utils import print_header, print_step, print_success

print_header("Creating Session")
print_step(1, 3, "Validating input")
print_step(2, 3, "Creating database record")
print_step(3, 3, "Initializing session")
print_success("Session created successfully!")
```

### Example 2: Session List

```python
from src.cli.utils import create_status_table
from rich.console import Console

console = Console()
data = [
    {"ID": "abc123", "Project": "Project A", "Status": "Active"},
    {"ID": "def456", "Project": "Project B", "Status": "Completed"},
]
table = create_status_table(data, title="Sessions")
console.print(table)
```

### Example 3: Error Handling

```python
from src.cli.utils import print_error, print_info

try:
    # Some operation
    pass
except Exception as e:
    print_error(f"Operation failed: {str(e)}")
    print_info("Use --verbose for more details")
```

### Example 4: Progress Tracking

```python
from src.cli.utils import print_step, print_loading_spinner

print_step(1, 5, "Loading data")
print_loading_spinner("Processing...", duration=2.0)
print_step(2, 5, "Analyzing results")
```

---

## Tips & Tricks

1. **Combine functions** for complex displays
2. **Use consistent styling** across commands
3. **Add emojis** for visual hierarchy
4. **Use tables** for structured data
5. **Use boxes** for important messages
6. **Use progress** for long operations
7. **Use colors** semantically (green=good, red=bad)
8. **Test in different terminals** for compatibility

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Colors not showing | Check terminal ANSI support |
| Emojis broken | Check terminal Unicode support |
| Tables misaligned | Resize terminal window |
| Text cut off | Increase terminal width |

---

## See Also

- `CLI_RICH_ENHANCEMENT_GUIDE.md` - Full guide
- `src/cli/interactive.py` - Interactive functions
- `src/cli/utils.py` - Utility functions
- `src/cli/main.py` - Main CLI implementation

---

**Happy CLI-ing! 🎉**


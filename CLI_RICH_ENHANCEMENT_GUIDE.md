# CLI Rich Enhancement Guide - U-AIP Scoping Assistant

## Overview

The U-AIP CLI has been enhanced with the **Rich Python module** to provide a beautiful, user-friendly terminal experience with:

- 🎨 **Colored output** with semantic styling
- 📊 **Rich tables** with rounded borders
- 📈 **Progress indicators** and visual feedback
- 🎯 **Stage progress tracking** with visual symbols
- 📝 **Formatted panels** and boxes
- ✨ **Emojis and icons** for better UX
- 🎪 **Multiple display utilities** for various content types

---

## What's New

### 1. Enhanced Interactive Module (`src/cli/interactive.py`)

**New Display Functions:**

```python
# Welcome banner
display_welcome_banner(app_name="U-AIP Scoping Assistant")

# Progress tracking
display_progress_bar(current=3, total=5, label="Stages")
display_stage_progress(current_stage=2, total_stages=5)

# Information boxes
display_info_box(title="Info", content="Your content", style="cyan")
display_success_box(title="Success", content="Operation completed!")
display_error_box(title="Error", content="Something went wrong")
display_warning_box(title="Warning", content="Please review")

# Data display
display_key_value_pairs({"Name": "Project", "Status": "Active"})
display_list_items(["Item 1", "Item 2"], title="Items")
display_comparison_table([{"Name": "A", "Value": 1}])

# Code and markdown
display_code_block(code="print('hello')", language="python")
display_markdown_content("# Heading\n\nContent here")

# Tree structures
display_tree_structure({"Parent": ["Child 1", "Child 2"]})

# Spinners
display_spinner_task("Loading...", duration=2.0)
```

### 2. New CLI Utils Module (`src/cli/utils.py`)

**20+ Helper Functions:**

```python
# Basic printing
print_header("Section Title")
print_section("Title", "Content")
print_success("Operation successful")
print_error("Operation failed")
print_warning("Warning message")
print_info("Information")

# Progress tracking
print_step(1, 5, "Starting process")
print_loading_spinner("Loading data...")

# Table creation
create_status_table(data, title="Status")
create_key_value_table({"Key": "Value"})

# Formatting
format_duration(125.5)  # "2.1m"
format_size(1024000)    # "1000.0KB"

# Indicators
create_status_indicator("completed")  # "✓ Completed"
create_stage_indicator(2, 5)          # "✓ ● ○ ○ ○"

# Display utilities
print_box("Content", title="Title")
print_divider()
print_centered("Centered text")
print_bullet_list(["Item 1", "Item 2"])
```

### 3. Enhanced Main CLI (`src/cli/main.py`)

**Improvements:**

- ✨ Welcome banner on startup
- 🎯 Stage progress indicators with visual symbols
- 📊 Better table formatting with ROUNDED boxes
- 🚀 Emoji icons for better visual hierarchy
- 📋 Improved panel styling
- 🎨 Consistent color scheme throughout

**Visual Enhancements:**

```
┌─────────────────────────────────────────────────────────┐
│                U-AIP Scoping Assistant                  │
│   Universal AI Project Scoping and Framing Protocol     │
│                    v1.0.0-dev                           │
└─────────────────────────────────────────────────────────┘

🚀 Starting New Session
Initializing project evaluation workflow...

🎯 Starting Multi-Stage Interview (Stages 1-5)
═══════════════════════════════════════════════════════════
Stage 1: Business Translation
═══════════════════════════════════════════════════════════
  ✓ Stage 1 → ► Stage 2 → ○ Stage 3 → ○ Stage 4 → ○ Stage 5
```

---

## Usage Examples

### Example 1: Using Interactive Functions

```python
from src.cli.interactive import (
    display_welcome_banner,
    display_stage_progress,
    display_success_box,
)

# Display welcome
display_welcome_banner()

# Show progress
display_stage_progress(current_stage=2, total_stages=5)

# Show success
display_success_box(
    "Session Created",
    "Your project evaluation session has been created successfully!"
)
```

### Example 2: Using Utils Functions

```python
from src.cli.utils import (
    print_header,
    print_step,
    create_status_table,
    print_success,
)

# Print header
print_header("Processing Sessions")

# Show steps
print_step(1, 3, "Loading sessions from database")
print_step(2, 3, "Filtering by status")
print_step(3, 3, "Formatting output")

# Create and display table
data = [
    {"Session ID": "abc123", "Status": "Active"},
    {"Session ID": "def456", "Status": "Completed"},
]
table = create_status_table(data, title="Sessions")
console.print(table)

# Show success
print_success("All sessions loaded successfully")
```

### Example 3: Custom Display

```python
from src.cli.utils import (
    print_box,
    print_bullet_list,
    create_stage_indicator,
)

# Display information box
print_box(
    "Your project evaluation is in progress.\n"
    "Current stage: 2 of 5",
    title="Session Status",
    style="cyan"
)

# Display bullet list
print_bullet_list(
    [
        "Stage 1: Business Translation ✓",
        "Stage 2: Value Quantification (in progress)",
        "Stage 3: Data Feasibility",
        "Stage 4: User Centricity",
        "Stage 5: Ethical Governance",
    ],
    title="Stages"
)

# Display stage indicator
stages = create_stage_indicator(2, 5)
print(f"Progress: {stages}")
```

---

## Color Scheme

The CLI uses a consistent color scheme:

- **Cyan** (`[cyan]`) - Primary information, headers
- **Green** (`[green]`) - Success, completed items
- **Yellow** (`[yellow]`) - Warnings, current items
- **Red** (`[red]`) - Errors, failed items
- **Dim** (`[dim]`) - Secondary information, disabled items
- **White** (`[white]`) - Default text

---

## Icons and Symbols

- ✓ - Completed/Success
- ✗ - Failed/Error
- ► - Current/In Progress
- ○ - Pending/Not Started
- ⚠ - Warning
- ℹ - Information
- 🚀 - Start/Launch
- 📋 - List/Sessions
- 📊 - Statistics/Data
- 📄 - Document/Export
- 🎯 - Target/Goal
- 💾 - Save/Database
- ⏸ - Pause
- 🎉 - Success/Celebration

---

## Integration Points

### In CLI Commands

All CLI commands now use enhanced display:

```bash
# Start command
uaip start "My Project"
# Shows: Welcome banner + stage progress + success box

# List command
uaip list
# Shows: Formatted table with ROUNDED boxes

# Resume command
uaip resume <session-id>
# Shows: Session info + progress indicators

# Export command
uaip export <session-id>
# Shows: Export progress + success message
```

### In Interactive Prompts

Stage interviews now use enhanced prompts:

```python
# Question display
await ask_user_question(
    question="What is your project about?",
    stage_number=1,
    question_number=1,
    context="Please provide a detailed description"
)

# Quality feedback
await display_follow_up(
    follow_up_question="Can you elaborate?",
    quality_score=6,
    issues=["Too vague", "Missing details"]
)
```

---

## Best Practices

1. **Use appropriate functions** for different content types
2. **Maintain consistent styling** across commands
3. **Use emojis sparingly** for visual hierarchy
4. **Provide clear feedback** for user actions
5. **Use progress indicators** for long operations
6. **Group related information** in boxes/panels
7. **Use tables** for structured data
8. **Use bullet lists** for sequential items

---

## Performance Notes

- Rich module is lightweight and fast
- No performance impact on CLI operations
- Rendering is optimized for terminal output
- Works with all modern terminals

---

## Troubleshooting

### Colors not showing?
- Ensure terminal supports ANSI colors
- Check `TERM` environment variable
- Try: `export TERM=xterm-256color`

### Emojis not displaying?
- Ensure terminal font supports Unicode
- Check terminal encoding: `echo $LANG`
- Try: `export LANG=en_US.UTF-8`

### Tables look wrong?
- Ensure terminal width is sufficient
- Try resizing terminal window
- Check box drawing character support

---

## Future Enhancements

Potential additions:
- Live progress bars for long operations
- Interactive menus with arrow keys
- Syntax highlighting for JSON/YAML
- Real-time log streaming
- Progress graphs and charts
- Terminal recording/playback

---

## References

- [Rich Documentation](https://rich.readthedocs.io/)
- [Rich GitHub](https://github.com/Textualize/rich)
- [ANSI Color Codes](https://en.wikipedia.org/wiki/ANSI_escape_code)

---

## Summary

The enhanced CLI provides a professional, user-friendly experience with:
- ✨ Beautiful visual formatting
- 📊 Rich data display options
- 🎯 Clear progress tracking
- 🎨 Consistent styling
- 🚀 Improved user engagement

Enjoy your enhanced U-AIP CLI experience! 🎉


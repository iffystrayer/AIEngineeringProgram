## type: employee-contact employee-id: <% tp.system.prompt("Enter Employee ID") %> phone: <% tp.system.prompt("Enter Phone Number (e.g., (555) 123-4567)") %> email: <% tp.system.prompt("Enter Email Address") %> date-created: <% tp.date.now("YYYY-MM-DD") %>

# 📞 Contact Details for <% tp.file.title %>
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS_DIR = os.path.join(ROOT_DIR, "tools")
TEMPLATE_PATH = os.path.join(ROOT_DIR, "misc", "helpers", "templates", "tool_template.py")
EXCLUDE_DIRS = {"panel_tools", "__pycache__"}

def snake_case(name):
    return name.lower().replace(" ", "_")

def pascal_case(name):
    return "".join(w.capitalize() for w in name.split())

def list_categories():
    cats = []
    for d in os.listdir(TOOLS_DIR):
        p = os.path.join(TOOLS_DIR, d)
        if os.path.isdir(p) and d not in EXCLUDE_DIRS and not d.startswith("."):
            cats.append(d)
    return sorted(cats, key=str.lower)

def choose_category():
    categories = list_categories()
    print("\nAvailable categories:")
    if categories:
        for i, cat in enumerate(categories, start=1):
            print(f"{i}. {cat}")
    else:
        print("(none yet)")

    choice = input("\nChoose category number or type a new one: ").strip()
    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(categories):
            return categories[idx - 1]
        print("Invalid number, please try again.")
        return choose_category()
    return choice

def main():
    tool_name = input("Tool Name: ").strip()
    category = choose_category().strip().lower()

    os.makedirs(os.path.join(TOOLS_DIR, category), exist_ok=True)

    filename = snake_case(tool_name) + ".py"
    dest_path = os.path.join(TOOLS_DIR, category, filename)

    if os.path.exists(dest_path):
        print(f"ERROR: Tool '{filename}' already exists in '{category}'.")
        return

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    template = template.replace("{ToolClassName}", pascal_case(tool_name))
    template = template.replace("{tool_name}", tool_name)

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(template)

    print(f"\nCreated: {dest_path}")

if __name__ == "__main__":
    main()

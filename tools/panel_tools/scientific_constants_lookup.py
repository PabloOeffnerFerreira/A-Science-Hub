from core.data.functions import constants_tools as ct

def list_categories():
    return ct.categories()

def list_constants(category: str):
    return ct.items_by_category(category)

def search(query: str):
    return ct.find_by_name(query)

def get(category: str, name: str):
    return ct.get_constant(category, name)

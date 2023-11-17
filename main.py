#from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import gspread
from oauth2client.service_account import ServiceAccountCredentials
 
app = FastAPI()
 
# Setup gspread client
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('nextrack-395408-c510f040596d.json', scope)
client = gspread.authorize(creds)
 
# Use the sheet name and worksheet appropriately
sheet = client.open("CRM_database")
 
# Define your Pydantic models here 
class User(BaseModel):
    id: str
    role: str
    name: str
    phone: str
    login_email: str
    hashed_password: str
 
class Customer(BaseModel):
    id: str
    name: str
    phone: str
    email: str
    address: str
    created_at: str
    updated_at: str
 
class Product(BaseModel):
    id: str
    name: str
    colour: str
    main_category: str
    category: str
    sub_category: str
    brand: str
    msrp: float
    model: str
    in_stock_qty: int
    taxes: float
    base_price: float
 
class Bill(BaseModel):
    id: str
    customer_id: str
    product_ids: List[str]
    quantities: List[int]
    date: str
    total_amount: float
 
def find_row(worksheet, unique_id, id_column_index=1):
    # gspread starts counting from 1
    for i, row in enumerate(worksheet.get_all_values(), start=1):
        if row[id_column_index - 1] == unique_id:
            return i
    return None

def model_to_row(model: BaseModel):
    return list(model.dict().values())
 
# Helper function to convert a pydantic model to a list for spreadsheet row
def model_to_row(model: BaseModel):
    return list(model.dict().values())

# CRUD operations for Users
@app.post("/users/")
def create_user(user: User):
    users_worksheet = sheet.worksheet('Users')
    users_worksheet.append_row(list(user.dict().values()))
    return {"message": "User created successfully"}
 
@app.get("/users/{user_id}")
def get_user(user_id: int):
    users_worksheet = sheet.worksheet('Users')
    user_records = users_worksheet.get_all_records()
    print(user_records)
    user = next((record for record in user_records if record['id'] == user_id), None)
    if user is not None:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")
 
@app.put("/users/{user_id}")
def update_user(user_id: str, user: User):
    users_worksheet = sheet.worksheet('Users')
    row_number = find_row(users_worksheet, user_id)
    if row_number:
        users_worksheet.update(f"A{row_number}:G{row_number}", [model_to_row(user)])
        return {"message": "User updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

 
@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    users_worksheet = sheet.worksheet('Users')
    row_number = find_row(users_worksheet, user_id)
    if row_number:
        users_worksheet.delete_rows(row_number)
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")
    


 
# CRUD operations for Customers
@app.post("/customers/")
def create_customer(customer: Customer):
    customers_worksheet = sheet.worksheet("Cusomters")
    customers_worksheet.append_row(list(customer.dict().values()))
    return {"message": "Customer created successfully"}

@app.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    customers_worksheet = sheet.worksheet('Customers')
    customer_records = customers_worksheet.get_all_records()
    customer = next((record for record in customer_records if record['id'] == customer_id), None)
    if customer is not None:
        return customer
    else:
        raise HTTPException(status_code=404, detail="Customer not found")
    
@app.put("/customers/{customer_id}")
def update_customer(customer_id: str, customer: Customer):
    customers_worksheet = sheet.worksheet('Customers')
    row_number = find_row(customers_worksheet, customer_id)
    if row_number:
        customers_worksheet.update(f"A{row_number}:G{row_number}", [model_to_row(customer)])
        return {"message": "Customer updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Customer not found")
    
@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: str):
    customers_worksheet = sheet.worksheet('Users')
    row_number = find_row(customers_worksheet, customer_id)
    if row_number:
        customers_worksheet.delete_rows(row_number)
        return {"message": "Customer deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Customer not found")

# CRUD operations for products
@app.post("/products/")
def create_product(product: Product):
    products_worksheet = sheet.worksheet("Products")
    products_worksheet.append_row(list(product.dict().values()))
    return {"message": "Product created successfully"}

@app.get("/products/{product_id}")
def get_product(product_id: int):
    products_worksheet = sheet.worksheet('Products')
    product_records = products_worksheet.get_all_records()
    product = next((record for record in product_records if record['id'] == product_id), None)
    if product is not None:
        return product
    else:
        raise HTTPException(status_code=404, detail="Customer not found")
    
@app.put("/products/{product_id}")
def update_product(product_id: str, product: Product):
    products_worksheet = sheet.worksheet('Products')
    row_number = find_row(products_worksheet, product_id)
    if row_number:
        products_worksheet.update(f"A{row_number}:G{row_number}", [model_to_row(product)])
        return {"message": "Product updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Product not found")
    
@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    products_worksheet = sheet.worksheet('Products')
    row_number = find_row(products_worksheet, product_id)
    if row_number:
        products_worksheet.delete_rows(row_number)
        return {"message": "Product deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Product not found")
    
# bill 
def calculate_total(products_worksheet, product_ids: List[str], quantities: List[int]) -> float:
    total_amount = 0.0
    # Loop through all product IDs
    for product_id, quantity in zip(product_ids, quantities):
        row = find_row(products_worksheet, product_id, id_column_index=1)
        if not row:
            raise ValueError(f"Product ID {product_id} not found")
        product_details = products_worksheet.row_values(row)
        # Assuming the price is in column 9 (MSRP) and taxes in column 11 in the sheet
        price = float(product_details[8])
        tax = float(product_details[10])
        total_amount += (price + tax) * quantity
    return total_amount

@app.post("/bills/")
def create_bill(bill: Bill):
    products_worksheet = sheet.worksheet('Products')
    try:
        # Calculate total amount
        bill.total_amount = calculate_total(products_worksheet, bill.product_ids, bill.quantities)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    bills_worksheet = sheet.worksheet('Bills')
    bill_data = model_to_row(bill)
    bills_worksheet.append_row(bill_data)
    return {"message": "Bill created successfully", "bill": bill}

# Search endpoints
@app.get("/search/products/")
def search_products(query: str):
    products_worksheet = sheet.worksheet('Products')
    product_records = products_worksheet.get_all_records()
    matching_products = [product for product in product_records if query.lower() in product['name'].lower()]
    return matching_products
 
@app.get("/search/customers/")
def search_customers(query: str):
    customers_worksheet = sheet.worksheet('Customers')
    customer_records = customers_worksheet.get_all_records()
    matching_customers = [customer for customer in customer_records if query.lower() in customer['name'].lower()]
    return matching_customers
 
@app.get("/search/users/")
def search_users(query: str):
    users_worksheet = sheet.worksheet('Users')
    user_records = users_worksheet.get_all_records()
    matching_users = [user for user in user_records if query.lower() in user['name'].lower()]
    return matching_users
 
# Tracking purchase history
@app.get("/customers/{customer_id}/purchase_history")
def track_purchase_history(customer_id: str):
    bills_worksheet = sheet.worksheet('Bills')
    bill_records = bills_worksheet.get_all_records()
    customer_bills = [bill for bill in bill_records if bill['customer_id'] == customer_id]
    return customer_bills
 
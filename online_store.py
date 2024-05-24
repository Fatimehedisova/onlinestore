import streamlit as st
import pandas as pd
import os

# File path for the CSV
CSV_FILE = 'products.csv'

# Initialize the CSV file if it doesn't exist
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=['Product ID', 'Product Name', 'Description', 'Price', 'Quantity', 'Image URL'])
    df.to_csv(CSV_FILE, index=False)

# Load products from CSV
def load_products():
    return pd.read_csv(CSV_FILE)

# Save products to CSV
def save_products(df):
    df.to_csv(CSV_FILE, index=False)

# Add a new product
def add_product(product_id, product_name, description, price, quantity, image_url):
    df = load_products()
    new_product = pd.DataFrame({
        'Product ID': [product_id],
        'Product Name': [product_name],
        'Description': [description],
        'Price': [price],
        'Quantity': [quantity],
        'Image URL': [image_url]
    })
    df = pd.concat([df, new_product], ignore_index=True)
    save_products(df)

# Delete a product
def delete_product(product_id):
    df = load_products()
    df = df[df['Product ID'] != product_id]
    save_products(df)

# Edit a product
def edit_product(product_id, product_name, description, price, quantity, image_url):
    df = load_products()
    df.loc[df['Product ID'] == product_id, ['Product Name', 'Description', 'Price', 'Quantity', 'Image URL']] = [product_name, description, price, quantity, image_url]
    save_products(df)

# Streamlit app
st.title('Simple Online Store')

# Navigation
st.sidebar.title("Navigation")
options = st.sidebar.radio('Go to', ['Home', 'Admin', 'Edit', 'Cart'])

if options == 'Home':
    st.header('Product List')
    products = load_products()
    
    for index, row in products.iterrows():
        st.subheader(row['Product Name'])
        if pd.notna(row['Image URL']) and row['Image URL'].strip() != '':
            st.image(row['Image URL'], width=200)
        st.write(f"**Description:** {row['Description']}")
        st.write(f"**Price:** ${row['Price']}")
        st.write(f"**Quantity Available:** {row['Quantity']}")
        if row['Quantity'] > 0:
            if st.button(f'Add to Cart', key=f"add_{row['Product ID']}"):
                if 'cart' not in st.session_state:
                    st.session_state.cart = []
                st.session_state.cart.append(row['Product ID'])
                st.success(f"{row['Product Name']} added to cart!")
        else:
            st.write("Out of Stock")
        st.write("---")

elif options == 'Admin':
    st.header('Admin Panel')

    st.subheader('Add New Product')
    with st.form(key='add_product_form'):
        product_id = st.text_input('Product ID')
        product_name = st.text_input('Product Name')
        description = st.text_input('Description')
        price = st.number_input('Price', min_value=0.0, format='%f')
        quantity = st.number_input('Quantity', min_value=0, format='%d')
        image_url = st.text_input('Image URL')
        submit_button = st.form_submit_button(label='Add Product')
        if submit_button:
            add_product(product_id, product_name, description, price, quantity, image_url)
            st.success('Product added successfully!')

    st.subheader('Delete Product')
    with st.form(key='delete_product_form'):
        product_id_to_delete = st.text_input('Product ID to Delete')
        delete_button = st.form_submit_button(label='Delete Product')
        if delete_button:
            delete_product(product_id_to_delete)
            st.success('Product deleted successfully!')

    st.subheader('Current Products')
    products = load_products()
    st.dataframe(products)

elif options == 'Edit':
    st.header('Edit Product')

    st.subheader('Select Product to Edit')
    products = load_products()
    product_ids = products['Product ID'].tolist()
    product_id_to_edit = st.selectbox('Product ID', product_ids)

    if product_id_to_edit:
        product = products[products['Product ID'] == product_id_to_edit].iloc[0]
        with st.form(key='edit_product_form'):
            product_name = st.text_input('Product Name', value=product['Product Name'])
            description = st.text_input('Description', value=product['Description'])
            price = st.number_input('Price', min_value=0.0, format='%f', value=product['Price'])
            quantity = st.number_input('Quantity', min_value=0, format='%d', value=product['Quantity'])
            image_url = st.text_input('Image URL', value=product['Image URL'])
            submit_button = st.form_submit_button(label='Edit Product')
            if submit_button:
                edit_product(product_id_to_edit, product_name, description, price, quantity, image_url)
                st.success('Product updated successfully!')

elif options == 'Cart':
    st.header('Shopping Cart')
    if 'cart' not in st.session_state or len(st.session_state.cart) == 0:
        st.write("Your cart is empty")
    else:
        cart_items = [product_id for product_id in st.session_state.cart]
        products = load_products()
        cart_products = products[products['Product ID'].isin(cart_items)]
        total = 0
        for index, row in cart_products.iterrows():
            st.subheader(row['Product Name'])
            if pd.notna(row['Image URL']) and row['Image URL'].strip() != '':
                st.image(row['Image URL'], width=200)
            st.write(f"**Description:** {row['Description']}")
            st.write(f"**Price:** ${row['Price']}")
            total += row['Price']
            if st.button(f'Remove from Cart', key=f'remove_{row["Product ID"]}'):
                st.session_state.cart.remove(row['Product ID'])
                st.success(f"{row['Product Name']} removed from cart!")
        st.write("---")
        st.write(f"**Total:** ${total}")

# Refresh the product list
if st.button('Refresh Product List'):
    products = load_products()
    st.dataframe(products)

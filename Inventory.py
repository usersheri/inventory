import streamlit as st
import pandas as pd
from dataclasses import dataclass

# --- OOP DESIGN ---
# Using @dataclass for a clean and simple Product class,
# which aligns with its role as a data container.
@dataclass
class Product:
    """Represents a single product in the inventory."""
    name: str
    price: float
    quantity: int

    def __post_init__(self):
        """Validate data after initialization."""
        if not self.name:
            raise ValueError("Product name cannot be empty.")
        if self.price < 0 or self.quantity < 0:
            raise ValueError("Price and quantity must be non-negative.")
        
        # Ensure correct types
        self.price = float(self.price)
        self.quantity = int(self.quantity)

    def calculate_value(self) -> float:
        """Calculates the total stock value for this product."""
        return self.price * self.quantity

class InventoryManager:
    """
    Manages the collection of products and inventory logic.
    This class demonstrates encapsulation by hiding the internal
    inventory dictionary and exposing methods to interact with it.
    """
    
    def __init__(self):
        # The inventory is "private," stored as a dictionary
        # mapping product names (str) to Product objects.
        self._inventory: dict[str, Product] = {}

    def add_or_update_product(self, product: Product):
        """
        Adds a new product or updates an existing one.
        The product name is used as the unique key.
        """
        self._inventory[product.name] = product

    def get_product(self, product_name: str) -> Product | None:
        """Retrieves a product by its name, or None if not found."""
        return self._inventory.get(product_name)

    def calculate_total_inventory_value(self) -> float:
        """Calculates the total value of all products in stock."""
        total_value = 0.0
        for product in self._inventory.values():
            total_value += product.calculate_value()
        return total_value

    def get_inventory_dataframe(self) -> pd.DataFrame:
        """
        Returns the current inventory as a pandas DataFrame
        for easy display in Streamlit.
        """
        data = []
        for product in self._inventory.values():
            data.append({
                "Product Name": product.name,
                "Price": product.price,
                "Quantity": product.quantity,
                "Stock Value": product.calculate_value()
            })
        
        if not data:
            return pd.DataFrame(columns=["Product Name", "Price", "Quantity", "Stock Value"])
            
        df = pd.DataFrame(data)
        # Sort by product name for consistent display
        df = df.sort_values(by="Product Name").reset_index(drop=True)
        return df

# --- STREAMLIT UI ---

st.set_page_config(page_title="Inventory App", layout="wide")
st.title(" Inventory Management App")

# --- STATE INITIALIZATION ---
# We must use st.session_state to store the InventoryManager instance.
# Otherwise, it would be re-created on every script rerun (i.e., every interaction).
if 'inventory_manager' not in st.session_state:
    st.session_state.inventory_manager = InventoryManager()

# Get the single, persistent manager instance
manager = st.session_state.inventory_manager

# --- SIDEBAR (About) ---
st.sidebar.header("About This App")
st.sidebar.info(
    "This app demonstrates Object-Oriented Programming (OOP) with Streamlit.\n\n"
    "1.  **`Product` class**: A data class holding `name`, `price`, and `quantity`.\n"
    "2.  **`InventoryManager` class**: Encapsulates all logic. It holds a 'private' dictionary of products and provides methods like `add_or_update_product` and `calculate_total_inventory_value`.\n"
    "3.  **`st.session_state`**: This is the key to making OOP work in Streamlit. It persists the `InventoryManager` object across user interactions."
)

# --- MAIN PAGE LAYOUT ---
col1, col2 = st.columns([1, 2])  # 1/3 width for input, 2/3 for display

# --- Column 1: Add/Update Products ---
with col1:
    st.header("Add / Update Product")
    
    # Using a form batches inputs and prevents reruns on every widget change
    with st.form("product_form", clear_on_submit=True):
        name = st.text_input("Product Name")
        price = st.number_input("Price ($)", min_value=0.01, format="%.2f")
        quantity = st.number_input("Quantity", min_value=0, step=1)
        
        submitted = st.form_submit_button("Submit")

        if submitted:
            if not name:
                st.error("Please enter a product name.")
            else:
                try:
                    # 1. Create the Product object (data validation happens here)
                    product = Product(name=name, price=price, quantity=quantity)
                    
                    # 2. Use the manager to handle the data
                    manager.add_or_update_product(product)
                    st.success(f"Successfully added/updated '{name}'!")
                    
                except ValueError as e:
                    # Catch validation errors from the Product class
                    st.error(f"Error: {e}")

# --- Column 2: Display Inventory ---
with col2:
    st.header("Current Inventory")
    
    # Get data *from the manager*
    inventory_df = manager.get_inventory_dataframe()
    
    if inventory_df.empty:
        st.info("Your inventory is empty. Add a product to get started.")
    else:
        # Display the data
        st.dataframe(
            inventory_df.style.format({"Price": "${:,.2f}", "Stock Value": "${:,.2f}"}), 
            use_container_width=True
        )
        
        st.divider()
        
        # --- Display Total Value ---
        st.header("Inventory Summary")
        total_value = manager.calculate_total_inventory_value()
        
        st.metric(label="Total Inventory Worth", value=f"${total_value:,.2f}")
import streamlit as st
import backend
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Inventory Management System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .success-box {
        background-color: #e6f7e6;
        border-left: 5px solid #4CAF50;
        padding: 1rem;
        margin: 1rem 0;
        color: #2d3b2d !important;
    }
    .error-box {
        background-color: #ffebee;
        border-left: 5px solid #F44336;
        padding: 1rem;
        margin: 1rem 0;
        color: #5f2120 !important;
    }
    .info-box {
        background-color: #e3f2fd;
        border-left: 5px solid #2196F3;
        padding: 1rem;
        margin: 1rem 0;
        color: #1e3d59 !important;
    }
    /* Ensure all text is visible */
    body {
        color: #333333 !important;
    }
    /* Make sure form labels are visible */
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        color: #333333 !important;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'bom_rows' not in st.session_state:
    st.session_state.bom_rows = 1

# Helper functions
def get_material_choices():
    return {name: id for id, name, _ in backend.get_inventory()}

def get_product_choices():
    return {name: id for id, name in backend.get_products()}

# Main app
def main():
    # Sidebar navigation
    with st.sidebar:
        st.markdown("""
        <style>
            .big-nav {
                font-size: 1.1rem !important;
                padding: 12px 20px !important;
                margin: 8px 0 !important;
                border-radius: 8px !important;
            }
            .big-nav:hover {
                background-color: #3b4a62 !important;
            }
            .big-nav-icon {
                font-size: 1.3rem !important;
                margin-right: 12px !important;
            }
            .sidebar-title {
                font-size: 1.8rem !important;
                font-weight: 700 !important;
                margin-bottom: 30px !important;
                color: white !important;
                padding-top: 20px !important;
            }
        </style>
        
        <div class="sidebar-title">📊 Teta Consulting </div>
        """, unsafe_allow_html=True)
        
        page = st.radio(
            "Navigation",
            ["🏠 Dashboard", "📦 Inventory", "🛠️ Products/BOM", "🛒 Orders", "📜 Order History"],
            label_visibility="collapsed"
        )

    # Dashboard
    if page == "🏠 Dashboard":
        st.markdown('<div class="header">📊 Dashboard</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="card"><h3>Total Materials</h3><h2 style="color: #4CAF50;">' + 
                         str(len(backend.get_inventory())) + '</h2></div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card"><h3>Total Products</h3><h2 style="color: #2196F3;">' + 
                         str(len(backend.get_products())) + '</h2></div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="card"><h3>Total Orders</h3><h2 style="color: #FF9800;">' + 
                         str(len(backend.get_order_history())) + '</h2></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="subheader">Recent Orders</div>', unsafe_allow_html=True)
        history = backend.get_order_history()
        if history:
            recent_orders = history[:5]
            st.table([{
                "Order ID": order_id,
                "Product": pname,
                "Quantity": qty,
                "Date": ts.split()[0]
            } for order_id, pname, qty, ts, _, _ in recent_orders])
        else:
            st.markdown('<div class="info-box">No orders placed yet</div>', unsafe_allow_html=True)

    # Inventory Management
    elif page == "📦 Inventory":
        st.markdown('<div class="header">📦 Inventory Management</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2], gap="large")
        
        with col1:
            with st.container():
                st.markdown('<div class="subheader">Manage Materials</div>', unsafe_allow_html=True)
                
                with st.expander("➕ Add New Material", expanded=True):
                    with st.form("add_material"):
                        name = st.text_input("Material Name", placeholder="e.g., Steel, Plastic")
                        quantity = st.number_input("Initial Quantity", min_value=0, value=0)
                        if st.form_submit_button("Add Material", use_container_width=True):
                            try:
                                backend.add_material(name, quantity)
                                st.markdown('<div class="success-box">Material added successfully!</div>', unsafe_allow_html=True)
                            except Exception as e:
                                st.markdown(f'<div class="error-box">{str(e)}</div>', unsafe_allow_html=True)
                
                with st.expander("🔄 Update Stock"):
                    materials = backend.get_inventory()
                    if materials:
                        material_id = st.selectbox(
                            "Select Material", 
                            [f"{id} - {name} (Current: {qty})" for id, name, qty in materials],
                            key="update_select"
                        )
                        selected_id = int(material_id.split(" - ")[0])
                        new_qty = st.number_input("New Quantity", min_value=0, key="update_qty")
                        if st.button("Update Quantity", use_container_width=True):
                            backend.update_material(selected_id, new_qty)
                            st.markdown('<div class="success-box">Quantity updated successfully!</div>', unsafe_allow_html=True)
                            st.experimental_rerun()
                    else:
                        st.markdown('<div class="info-box">No materials available</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="subheader">Current Inventory</div>', unsafe_allow_html=True)
            inventory = backend.get_inventory()
            
            if inventory:
                # Create a nice table with status indicators
                inventory_data = []
                for id, name, qty in inventory:
                    status = "🟢" if qty > 10 else "🟡" if qty > 0 else "🔴"
                    inventory_data.append({
                        "ID": id,
                        "Material": name,
                        "Quantity": qty,
                        "Status": status
                    })
                
                st.dataframe(
                    inventory_data,
                    column_config={
                        "Status": st.column_config.TextColumn(
                            "Stock Status",
                            help="🟢 = Good (>10), 🟡 = Low (>0), 🔴 = Out of stock"
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                with st.expander("🗑️ Delete Material"):
                    material_id = st.selectbox(
                        "Select Material to delete", 
                        [f"{id} - {name}" for id, name, _ in inventory],
                        key="delete_select"
                    )
                    selected_id = int(material_id.split(" - ")[0])
                    if st.button("Delete Material", use_container_width=True, type="primary"):
                        try:
                            backend.delete_material(selected_id)
                            st.markdown('<div class="success-box">Material deleted successfully!</div>', unsafe_allow_html=True)
                            st.experimental_rerun()
                        except Exception as e:
                            st.markdown(f'<div class="error-box">{str(e)}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box">No materials in inventory</div>', unsafe_allow_html=True)

    # Product and BOM Management
    elif page == "🛠️ Products/BOM":
        st.markdown('<div class="header">🛠️ Product & BOM Management</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["➕ Add Product", "👀 View Products", "🗑️ Delete Product"])
        
        with tab1:
            st.markdown('<div class="subheader">Add New Product</div>', unsafe_allow_html=True)
            product_name = st.text_input("Product Name", placeholder="e.g., Chair, Table")
            
            st.markdown('<div class="subheader">Bill of Materials (BOM)</div>', unsafe_allow_html=True)
            materials = backend.get_inventory()
            
            if not materials:
                st.markdown('<div class="info-box">No materials available. Please add materials first.</div>', unsafe_allow_html=True)
            else:
                # Dynamic BOM rows
                for i in range(st.session_state.bom_rows):
                    cols = st.columns([3, 1, 1])
                    with cols[0]:
                        mat_name = st.selectbox(
                            f"Material {i+1}", 
                            [name for _, name, _ in materials],
                            key=f"mat_{i}"
                        )
                    with cols[1]:
                        qty = st.number_input(
                            f"Qty", 
                            min_value=1, value=1,
                            key=f"qty_{i}"
                        )
                    with cols[2]:
                        if i > 0 and st.button("❌", key=f"remove_{i}"):
                            st.session_state.bom_rows -= 1
                            st.experimental_rerun()
                
                col_add, col_submit = st.columns([1, 3])
                with col_add:
                    if st.button("➕ Add Material", use_container_width=True):
                        st.session_state.bom_rows += 1
                        st.experimental_rerun()
                
                if st.button("Add Product", type="primary", use_container_width=True):
                    try:
                        # Get BOM entries
                        bom = []
                        material_map = {name: id for id, name, _ in materials}
                        for i in range(st.session_state.bom_rows):
                            mat_name = st.session_state[f"mat_{i}"]
                            qty = st.session_state[f"qty_{i}"]
                            bom.append((material_map[mat_name], qty))
                        
                        backend.add_product(product_name, bom)
                        st.session_state.bom_rows = 1
                        st.markdown('<div class="success-box">Product added successfully!</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f'<div class="error-box">{str(e)}</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="subheader">Existing Products</div>', unsafe_allow_html=True)
            products = backend.get_products()
            if products:
                for product_id, name in products:
                    with st.expander(f"🛠️ {name}", expanded=True):
                        bom = backend.get_bom(product_id)
                        if bom:
                            st.markdown("**Bill of Materials:**")
                            bom_data = []
                            for mid, mname, qty in bom:
                                bom_data.append({
                                    "Material": mname,
                                    "Quantity per Unit": qty
                                })
                            st.dataframe(
                                bom_data,
                                hide_index=True,
                                use_container_width=True
                            )
                        else:
                            st.markdown('<div class="info-box">No BOM defined for this product</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box">No products available</div>', unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<div class="subheader">Delete Product</div>', unsafe_allow_html=True)
            products = backend.get_products()
            if products:
                product_id = st.selectbox(
                    "Select Product to delete", 
                    [f"{id} - {name}" for id, name in products],
                    key="delete_product"
                )
                selected_id = int(product_id.split(" - ")[0])
                if st.button("Delete Product", type="primary", use_container_width=True):
                    backend.delete_product(selected_id)
                    st.markdown('<div class="success-box">Product deleted successfully!</div>', unsafe_allow_html=True)
                    st.experimental_rerun()
            else:
                st.markdown('<div class="info-box">No products available</div>', unsafe_allow_html=True)

    # Order Management
    elif page == "🛒 Orders":
        st.markdown('<div class="header">🛒 Order Management</div>', unsafe_allow_html=True)
        
        products = backend.get_products()
        
        if not products:
            st.markdown('<div class="info-box">No products available to order</div>', unsafe_allow_html=True)
        else:
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    product_id = st.selectbox(
                        "Select Product", 
                        [f"{id} - {name}" for id, name in products],
                        key="order_product"
                    )
                    selected_id = int(product_id.split(" - ")[0])
                
                with col2:
                    quantity = st.number_input(
                        "Quantity", 
                        min_value=1, 
                        value=1,
                        key="order_qty"
                    )
                
                if st.button("Place Order", type="primary", use_container_width=True):
                    success, result = backend.place_order(selected_id, quantity)
                    if success:
                        st.markdown(f"""
                        <div class="success-box">
                            <h3>Order #{result} placed successfully!</h3>
                            <p>Materials have been deducted from inventory.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        missing_items = "\n".join([f"• {name}: {qty} more needed" for name, qty in result])
                        st.markdown(f"""
                        <div class="error-box">
                            <h3>Insufficient Stock</h3>
                            <p>Cannot fulfill this order due to:</p>
                            {missing_items}
                        </div>
                        """, unsafe_allow_html=True)

    # Order History
    elif page == "📜 Order History":
        st.markdown('<div class="header">📜 Order History</div>', unsafe_allow_html=True)
        history = backend.get_order_history()
        
        if not history:
            st.markdown('<div class="info-box">No orders placed yet</div>', unsafe_allow_html=True)
        else:
            # Group order details by order ID
            orders = {}
            for order_id, pname, qty, ts, mname, used in history:
                if order_id not in orders:
                    orders[order_id] = {
                        "product": pname,
                        "quantity": qty,
                        "timestamp": ts,
                        "materials": []
                    }
                orders[order_id]["materials"].append((mname, used))
            
            # Display each order in an expander
            for order_id, details in sorted(orders.items(), key=lambda x: x[1]['timestamp'], reverse=True):
                with st.expander(f"🛒 Order #{order_id} - {details['product']} (x{details['quantity']}) - {details['timestamp']}", expanded=True):
                    st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <strong>Product:</strong> {details['product']}<br>
                        <strong>Quantity:</strong> {details['quantity']}<br>
                        <strong>Date:</strong> {details['timestamp']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("**Materials Used:**")
                    mat_data = []
                    for mname, used in details["materials"]:
                        mat_data.append({
                            "Material": mname,
                            "Quantity Used": used
                        })
                    st.dataframe(
                        mat_data,
                        hide_index=True,
                        use_container_width=True
                    )

if __name__ == "__main__":
    main()
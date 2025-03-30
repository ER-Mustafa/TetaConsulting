import streamlit as st
import backend
from datetime import datetime

from PIL import Image

image = Image.open("logo.png")

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Envanter Yönetim Sistemi",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Özel CSS stilleri
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
    /* Tüm metinlerin görünür olmasını sağla */
    body {
        color: #333333 !important;
    }
    /* Form etiketlerinin görünür olmasını sağla */
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        color: #333333 !important;
    }
</style>
""", unsafe_allow_html=True)


# Oturum durumu başlatma
if 'bom_rows' not in st.session_state:
    st.session_state.bom_rows = 1

# Yardımcı fonksiyonlar
def get_material_choices():
    return {name: id for id, name, _ in backend.get_inventory()}

def get_product_choices():
    return {name: id for id, name in backend.get_products()}

# Ana uygulama
def main():
    # Yan menü navigasyonu
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
        """, unsafe_allow_html=True)
        st.image(image, use_container_width=True)

        
        page = st.radio(
            "Navigasyon",
            ["🏠 Pano", "📦 Envanter", "🛠️ Ürünler/Ürün Ağacı", "🛒 Siparişler", "📜 Sipariş Geçmişi"],
            label_visibility="collapsed"
        )

    # Pano
    if page == "🏠 Pano":
        st.markdown('<div class="header">📊 Pano</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="card"><h3>Toplam Malzeme</h3><h2 style="color: #4CAF50;">' + 
                         str(len(backend.get_inventory())) + '</h2></div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card"><h3>Toplam Ürün</h3><h2 style="color: #2196F3;">' + 
                         str(len(backend.get_products())) + '</h2></div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="card"><h3>Toplam Sipariş</h3><h2 style="color: #FF9800;">' + 
                         str(len(backend.get_order_history())) + '</h2></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="subheader">Son Siparişler</div>', unsafe_allow_html=True)
        history = backend.get_order_history()
        if history:
            recent_orders = history[:5]
            st.table([{
                "Sipariş ID": order_id,
                "Ürün": pname,
                "Miktar": qty,
                "Tarih": ts.split()[0]
            } for order_id, pname, qty, ts in recent_orders])
        else:
            st.markdown('<div class="info-box">Henüz sipariş verilmedi</div>', unsafe_allow_html=True)

    # Envanter Yönetimi
    elif page == "📦 Envanter":
        st.markdown('<div class="header">📦 Envanter Yönetimi</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2], gap="large")
        
        with col1:
            with st.container():
                st.markdown('<div class="subheader">Malzemeleri Yönet</div>', unsafe_allow_html=True)
                
                with st.expander("➕ Yeni Malzeme Ekle", expanded=True):
                    with st.form("add_material"):
                        name = st.text_input("Malzeme Adı", placeholder="Örn: Çelik, Plastik")
                        quantity = st.number_input("Başlangıç Miktarı", min_value=0, value=0)
                        if st.form_submit_button("Malzeme Ekle", use_container_width=True):
                            try:
                                backend.add_material(name, quantity)
                                st.markdown('<div class="success-box">Malzeme başarıyla eklendi!</div>', unsafe_allow_html=True)
                            except Exception as e:
                                st.markdown(f'<div class="error-box">{str(e)}</div>', unsafe_allow_html=True)
                
                with st.expander("🔄 Stok Güncelle"):
                    materials = backend.get_inventory()
                    if materials:
                        material_id = st.selectbox(
                            "Malzeme Seç", 
                            [f"{id} - {name} (Mevcut: {qty})" for id, name, qty in materials],
                            key="update_select"
                        )
                        selected_id = int(material_id.split(" - ")[0])
                        new_qty = st.number_input("Yeni Miktar", min_value=0, key="update_qty")
                        if st.button("Miktarı Güncelle", use_container_width=True):
                            backend.update_material(selected_id, new_qty)
                            st.markdown('<div class="success-box">Miktar başarıyla güncellendi!</div>', unsafe_allow_html=True)
                            st.rerun()
                    else:
                        st.markdown('<div class="info-box">Kullanılabilir malzeme yok</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="subheader">Mevcut Envanter</div>', unsafe_allow_html=True)
            inventory = backend.get_inventory()
            
            if inventory:
                # Durum göstergeleri ile güzel bir tablo oluştur
                inventory_data = []
                for id, name, qty in inventory:
                    status = "🟢" if qty > 10 else "🟡" if qty > 0 else "🔴"
                    inventory_data.append({
                        "ID": id,
                        "Malzeme": name,
                        "Miktar": qty,
                        "Durum": status
                    })
                
                st.dataframe(
                    inventory_data,
                    column_config={
                        "Durum": st.column_config.TextColumn(
                            "Stok Durumu",
                            help="🟢 = İyi (>10), 🟡 = Az (>0), 🔴 = Stokta yok"
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                with st.expander("🗑️ Malzeme Sil"):
                    material_id = st.selectbox(
                        "Silinecek malzemeyi seç", 
                        [f"{id} - {name}" for id, name, _ in inventory],
                        key="delete_select"
                    )
                    selected_id = int(material_id.split(" - ")[0])
                    if st.button("Malzemeyi Sil", use_container_width=True, type="primary"):
                        try:
                            backend.delete_material(selected_id)
                            st.markdown('<div class="success-box">Malzeme başarıyla silindi!</div>', unsafe_allow_html=True)
                            st.rerun()
                        except Exception as e:
                            st.markdown(f'<div class="error-box">{str(e)}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box">Envanterde malzeme yok</div>', unsafe_allow_html=True)

    # Ürün ve Ürün Ağacı Yönetimi
    elif page == "🛠️ Ürünler/Ürün Ağacı":
        st.markdown('<div class="header">🛠️ Ürün & Ürün Ağacı Yönetimi</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["➕ Ürün Ekle", "👀 Ürünleri Görüntüle", "🗑️ Ürün Sil"])
        
        with tab1:
            st.markdown('<div class="subheader">Yeni Ürün Ekle</div>', unsafe_allow_html=True)
            product_name = st.text_input("Ürün Adı", placeholder="Örn: Sandalye, Masa")
            
            st.markdown('<div class="subheader">Ürün Ağacı (BOM)</div>', unsafe_allow_html=True)
            materials = backend.get_inventory()
            
            if not materials:
                st.markdown('<div class="info-box">Kullanılabilir malzeme yok. Önce malzeme ekleyin.</div>', unsafe_allow_html=True)
            else:
                # Dinamik BOM satırları
                for i in range(st.session_state.bom_rows):
                    cols = st.columns([3, 1, 1])
                    with cols[0]:
                        mat_name = st.selectbox(
                            f"Malzeme {i+1}", 
                            [name for _, name, _ in materials],
                            key=f"mat_{i}"
                        )
                    with cols[1]:
                        qty = st.number_input(
                            f"Miktar", 
                            min_value=1, value=1,
                            key=f"qty_{i}"
                        )
                    with cols[2]:
                        if i > 0 and st.button("❌", key=f"remove_{i}"):
                            st.session_state.bom_rows -= 1
                            st.rerun()
                
                col_add, col_submit = st.columns([1, 3])
                with col_add:
                    if st.button("➕ Malzeme Ekle", use_container_width=True):
                        st.session_state.bom_rows += 1
                        st.rerun()
                
                if st.button("Ürün Ekle", type="primary", use_container_width=True):
                    try:
                        # BOM girişlerini al
                        bom = []
                        material_map = {name: id for id, name, _ in materials}
                        for i in range(st.session_state.bom_rows):
                            mat_name = st.session_state[f"mat_{i}"]
                            qty = st.session_state[f"qty_{i}"]
                            bom.append((material_map[mat_name], qty))
                        
                        backend.add_product(product_name, bom)
                        st.session_state.bom_rows = 1
                        st.markdown('<div class="success-box">Ürün başarıyla eklendi!</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f'<div class="error-box">{str(e)}</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="subheader">Mevcut Ürünler</div>', unsafe_allow_html=True)
            products = backend.get_products()
            if products:
                for product_id, name in products:
                    with st.expander(f"🛠️ {name}", expanded=True):
                        bom = backend.get_bom(product_id)
                        if bom:
                            st.markdown("**Ürün Ağacı:**")
                            bom_data = []
                            for mid, mname, qty in bom:
                                bom_data.append({
                                    "Malzeme": mname,
                                    "Birim Başına Miktar": qty
                                })
                            st.dataframe(
                                bom_data,
                                hide_index=True,
                                use_container_width=True
                            )
                        else:
                            st.markdown('<div class="info-box">Bu ürün için tanımlı ürün ağacı yok</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box">Kullanılabilir ürün yok</div>', unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<div class="subheader">Ürün Sil</div>', unsafe_allow_html=True)
            products = backend.get_products()
            if products:
                product_id = st.selectbox(
                    "Silinecek ürünü seç", 
                    [f"{id} - {name}" for id, name in products],
                    key="delete_product"
                )
                selected_id = int(product_id.split(" - ")[0])
                if st.button("Ürünü Sil", type="primary", use_container_width=True):
                    backend.delete_product(selected_id)
                    st.markdown('<div class="success-box">Ürün başarıyla silindi!</div>', unsafe_allow_html=True)
                    st.rerun()
            else:
                st.markdown('<div class="info-box">Kullanılabilir ürün yok</div>', unsafe_allow_html=True)

    # Sipariş Yönetimi
    elif page == "🛒 Siparişler":
        st.markdown('<div class="header">🛒 Sipariş Yönetimi</div>', unsafe_allow_html=True)
        
        products = backend.get_products()
        
        if not products:
            st.markdown('<div class="info-box">Sipariş verilebilecek ürün yok</div>', unsafe_allow_html=True)
        else:
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    product_id = st.selectbox(
                        "Ürün Seç", 
                        [f"{id} - {name}" for id, name in products],
                        key="order_product"
                    )
                    selected_id = int(product_id.split(" - ")[0])
                
                with col2:
                    quantity = st.number_input(
                        "Miktar", 
                        min_value=1, 
                        value=1,
                        key="order_qty"
                    )
                
                if st.button("Sipariş Ver", type="primary", use_container_width=True):
                    success, result = backend.place_order(selected_id, quantity)
                    if success:
                        st.markdown(f"""
                        <div class="success-box">
                            <h3>Sipariş #{result} başarıyla verildi!</h3>
                            <p>Malzemeler envanterden düşüldü.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        missing_items = "\n".join([f"• {name}: {qty} adet daha gerekli" for name, qty in result])
                        st.markdown(f"""
                        <div class="error-box">
                            <h3>Yetersiz Stok</h3>
                            <p>Bu sipariş aşağıdaki nedenlerle tamamlanamıyor:</p>
                            {missing_items}
                        </div>
                        """, unsafe_allow_html=True)

    # Sipariş Geçmişi
    elif page == "📜 Sipariş Geçmişi":
        st.markdown('<div class="header">📜 Sipariş Geçmişi</div>', unsafe_allow_html=True)
        history = backend.get_order_history()
        
        if not history:
            st.markdown('<div class="info-box">Henüz sipariş verilmedi</div>', unsafe_allow_html=True)
        else:
            # Sipariş detaylarını ID'ye göre grupla
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
            
            # Her siparişi bir genişletilebilir alanda göster
            for order_id, details in sorted(orders.items(), key=lambda x: x[1]['timestamp'], reverse=True):
                with st.expander(f"🛒 Sipariş #{order_id} - {details['product']} (x{details['quantity']}) - {details['timestamp']}", expanded=True):
                    st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <strong>Ürün:</strong> {details['product']}<br>
                        <strong>Miktar:</strong> {details['quantity']}<br>
                        <strong>Tarih:</strong> {details['timestamp']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("**Kullanılan Malzemeler:**")
                    mat_data = []
                    for mname, used in details["materials"]:
                        mat_data.append({
                            "Malzeme": mname,
                            "Kullanılan Miktar": used
                        })
                    st.dataframe(
                        mat_data,
                        hide_index=True,
                        use_container_width=True
                    )

if __name__ == "__main__":
    main()
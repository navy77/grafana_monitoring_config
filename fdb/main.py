import streamlit as st
import time
# if "my_text" not in st.session_state:
#     st.session_state.my_text = ""

# def submit():
#     st.session_state.my_text = st.session_state.widget
#     st.session_state.widget = ""

# st.text_input("Enter text here", key="widget", on_change=submit)

# my_text = st.session_state.my_text

# st.write(my_text)
def clear_text():
    st.session_state["barcode"] = ""

def barcode():
    col1,col2,col3 = st.columns([4,2,4])
    scan = False
    with col1:
        input_text = st.text_input("Scan information here", key="barcode")
        st.button("clear", on_click=clear_text)
        if input_text:
            split_text = input_text.split('-')

            st.subheader(f'Lot : {split_text[0]}')
            st.subheader(f'Model : {split_text[1]}')
            st.subheader(f'OPT : {split_text[2]}')
            scan = True

    with col3:
         st.subheader(f'Spec :')
         st.subheader(f'max :')
         st.subheader(f'min :')
         st.subheader(f'ot :')

def serial_port():
    with col3:
        before_1 = st.text_input("",key="before_1",placeholder="before_1")
        before_2 = st.text_input("before_2", key="before_2")
        before_3 = st.text_input("before_3", key="before_3")
        before_4 = st.text_input("before_4", key="before_4")
        before_5 = st.text_input("before_5", key="before_5")
        before_6 = st.text_input("before_6", key="before_6")

    with col4:
        after_1 = st.text_input("", key="after_1",placeholder="after_1")
        after_2 = st.text_input("after_2", key="after_2")
        after_3 = st.text_input("after_3", key="after_3")
        after_4 = st.text_input("after_4", key="after_4")
        after_5 = st.text_input("after_5", key="after_5")
        after_6 = st.text_input("after_6", key="after_6")

def main():
    st.set_page_config(page_title='FDB',layout="wide",initial_sidebar_state="expanded")
    st.markdown("""<h1 style='text-align: center;'>WEIGHT SCALE AUTO INPUT</h1>""", unsafe_allow_html=True)
    barcode()
    

if __name__ == "__main__":
    main()

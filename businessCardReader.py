import easyocr
import streamlit as st
import pandas as pd
import re
from pymongo import MongoClient
from PIL import Image

st.markdown(
    """
    <style>
    .main {
    background-color: #FF9DC4;
    }
    </style>
    """,
    unsafe_allow_html=True
    )

# To Display the title for the project
st.title("BizCardX: Extract Business Card Details with OCR")
st.header('(Credit: Mayur)')

#  Input for Collection name in database
name = st.text_input("Enter Your Name")

# upload button
uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image = Image.open(uploaded_file)
        new_image = image.resize((500, 333))
        st.write("Image Preview")
        st.image(new_image)
        
        # showing the details
        show_details = st.button("Show Details")

        reader = easyocr.Reader(['en'])
        result1 = reader.readtext(bytes_data)
        
        # Creating string to iterate 
        df1 = pd.DataFrame(result1, columns=['a', 'b', 'c'])
        name_list= df1['b'].tolist()
        my_string = ', '.join(name_list)

# Creating Patterns
        pattern1 = r"[A-Za-z]+(?:\s+[A-Za-z]+)*(?:\s+(?:&|-)\s+[A-Za-z]+(?:\s+[A-Za-z]+)*)*"
        match1 = re.search(pattern1, my_string)
        if match1:
            card_holder = match1.group()
        else:
            card_holder = 'NA'

        pattern2 = r'\b([A-Z]+[ -&]+[A-Z]+?)+\b'
        match2 = re.search(pattern2, my_string)
        if match2:
            designation = match2.group()
        else:
            designation = 'NA'
            
        #pattern3 = r"^\+91-\d{10},$"
        #pattern3 = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        pattern3 = r'\d{3}-\d{3}-\d{4}'
        match3 = re.search(pattern3, my_string)
        if match3:
            mobile = match3.group()
        else:
            mobile = 'NA'

        #pattern4 = r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+"        
        pattern4 = r"\w+@\w+\.\w+"
        match4 = re.search(pattern4, my_string)
        if match4:
            email = match4.group()
        else:
            email = 'NA'

        pattern5 = r"\bglobal\.com\b"
        #pattern6 = r"https?://(?:www\.)?[A-Za-z0-9.-]+(?:\.[A-Za-z]{2,})?/?[A-Za-z0-9_./~#&=+-]*"
        match5 = re.search(pattern5, my_string)
        if match5:
            website = match5.group()
        else:
            website = 'NA'
            
        pattern6 = r"Andhra Pradesh|Arunachal Pradesh|Assam|Bihar|Chhattisgarh|Goa|Gujarat|Haryana|Himachal Pradesh|Jharkhand|Karnataka|Kerala|Madhya Pradesh|Maharashtra|Manipur|Meghalaya|Mizoram|Nagaland|Odisha|Punjab|Rajasthan|Sikkim|TamilNadu|Telangana|Tripura|Uttar Pradesh|Uttarakhand|West Bengal"
        match6 = re.search(pattern6, my_string)
        if match6:
            state = match6.group()
        else:
            state = 'NA'

        pattern7 = r"\d{6}"
        match7 = re.search(pattern7, my_string)
        if match7:
            pincode = match7.group()
        else:
            pincode = 'NA'

        l = [card_holder, designation, mobile, email, website, state, pincode]
        df = pd.DataFrame(l).T
        df.columns = ['Card_holder', 'Designation', 'Mobile', 'Email', 'Website', 'State', 'Pincode']
        
        # Showing details in dataframe form
        if show_details:
          st.write(df)
                    
        
        upload = st.button('Upload to Database')

        # Codes to Store the Datas in to the Data Base
        client = MongoClient(("mongodb://localhost:27017"))
        # Data Base
        db = client["Card_Reader"]

        if upload:
            col1, col2 = st.columns(2)
            with col1:
                mydb = db[name]
                df.reset_index(inplace=True)
                df_dict = df.to_dict("records")
                mydb.insert_one({"index": name + 'data', "data": df_dict})
                st.write("Details uploaded")
                
                
        if upload:
            # downloading the data 
             data_from_db = mydb.find_one({"index":name+'data'})
             df = pd.DataFrame(data_from_db["data"])
             df.to_csv("card.csv")
             df.to_json("card.json")
             
             col3, col4 = st.columns(2)
             with col3:
                 st.download_button("Download as CSV",
                                df.to_csv(),
                                mime = 'text/csv')
             with col4:
                 st.download_button("Download as Json",
                                df.to_json(),
                                mime='json')
import os
import re
import mysql.connector
import cv2
import mysql
import pandas as pd
import streamlit as st
from easyocr import easyocr
from matplotlib import pyplot as plt
from streamlit_option_menu import option_menu

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])


# Connecting to MySQL Database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ilovesreeraj",
    database="details",
    auth_plugin='mysql_native_password',
    charset='utf8mb4'
)

mysql_cursor = mydb.cursor(buffered=True)

# Creating table
mysql_cursor.execute('''CREATE TABLE IF NOT EXISTS card_data
                   (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    company_name TEXT,
                    card_holder TEXT,
                    designation TEXT,
                    mobile_number VARCHAR(50),
                    email TEXT,
                    website TEXT,
                    area TEXT,
                    city TEXT,
                    state TEXT,
                    pin_code VARCHAR(10),
                    image LONGBLOB
                    )''')

selected = option_menu(None, ["About", "Upload & Extract", "Database"],
                       icons=["house", "cloud-upload", "pencil-square"],
                       default_index=0,
                       orientation="horizontal")
if selected == 'About':
    st.title("Business Card Data Extraction App")
    st.markdown(
        """
        This Streamlit web application allows users to upload images of business cards 
        and extract valuable information such as company names, cardholder details, 
        contact information, and more using the EasyOCR library.

        **How It Works:**

        - **Image Upload:** Users can upload images (PNG, JPEG, JPG) of business cards.
        - **Data Extraction:** The app uses OCR to extract text details from the images.
        - **Information Display:** Extracted details are displayed along with the image preview.
        - **Database Integration:** Users can choose to save extracted data to a MySQL database.

        **Tools Used:**

        - Streamlit: Simplifies web app creation in Python.
        - EasyOCR: Enables optical character recognition on images.
        - OpenCV (cv2): Handles image processing tasks.
        - MySQL Connector: Interacts with a MySQL database.
        - Pandas: For data manipulation and creating DataFrames.
        - Matplotlib: Displays images and plots.

        Developed by Sreeraj T Surendran
        """
    )
if selected == "Upload & Extract":
    st.markdown("### Upload a Business Card")
    uploaded_card = st.file_uploader("upload here", label_visibility="collapsed", type=["png", "jpeg", "jpg"])

    if uploaded_card is not None:

        def save_uploaded_card(uploaded_card):
            with open(os.path.join("uploaded_cards", uploaded_card.name), "wb") as f:
                f.write(uploaded_card.getbuffer())

        save_uploaded_card(uploaded_card)



        def preview_image(image, res):
            for (bbox, text, prob) in res:
                # Draw bounding box and text on the image
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))
                cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                cv2.putText(image, text, (tl[0], tl[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            plt.rcParams['figure.figsize'] = (15, 15)
            plt.axis('off')
            plt.imshow(image)

        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown("#     ")
            st.markdown("#     ")
            st.markdown("### You have uploaded the card")
            st.image(uploaded_card)

        with col2:
            st.markdown("#     ")
            st.markdown("#     ")
            with st.spinner("Processing the image..."):
                st.set_option('deprecation.showPyplotGlobalUse', False)
                saved_image_path = os.path.join(os.getcwd(), "uploaded_cards", uploaded_card.name)
                image = cv2.imread(saved_image_path)
                res = reader.readtext(saved_image_path)
                st.markdown("### Image Processed and Data Extracted")
                st.pyplot(preview_image(image, res))

        saved_image_path = os.path.join(os.getcwd(), "uploaded_cards", uploaded_card.name)
        result = reader.readtext(saved_image_path, detail=0, paragraph=False)

        def image_to_binary(file):
            # Convert image data to binary format
            with open(file, 'rb') as file:
                binary_data = file.read()
            return binary_data


        extracted_data = {"company_name": [],
                          "card_holder": [],
                          "designation": [],
                          "mobile_number": [],
                          "email": [],
                          "website": [],
                          "area": [],
                          "city": [],
                          "state": [],
                          "pin_code": [],
                          "image": image_to_binary(saved_image_path)
                          }


        def extract_data(res):
            for ind, text in enumerate(res):

                # Website
                if "www " in text.lower() or "www." in text.lower():
                    extracted_data["website"].append(text)
                elif "WWW" in text:
                    extracted_data["website"] = res[4] + "." + res[5]

                # Email
                elif "@" in text:
                    extracted_data["email"].append(text)

                # Mobile number
                elif "-" in text:
                    extracted_data["mobile_number"].append(text)
                    if len(extracted_data["mobile_number"]) == 2:
                        extracted_data["mobile_number"] = " & ".join(extracted_data["mobile_number"])

                # Company Name
                elif ind == len(res) - 1:
                    extracted_data["company_name"].append(text)

                # Card holder name
                elif ind == 0:
                    extracted_data["card_holder"].append(text)

                # Designation
                elif ind == 1:
                    extracted_data["designation"].append(text)

                # Address
                if re.findall('^[0-9].+, [a-zA-Z]+', text):
                    extracted_data["area"].append(text.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+', text):
                    extracted_data["area"].append(text)

                # City
                match1 = re.findall('.+St , ([a-zA-Z]+).+', text)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', text)
                match3 = re.findall('^[E].*', text)
                if match1:
                    extracted_data["city"].append(match1[0])
                elif match2:
                    extracted_data["city"].append(match2[0])
                elif match3:
                    extracted_data["city"].append(match3[0])

                # state
                state_match = re.findall('[a-zA-Z]{9} +[0-9]', text)
                if state_match:
                    extracted_data["state"].append(text[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);', text):
                    extracted_data["state"].append(text.split()[-1])
                if len(extracted_data["state"]) == 2:
                    extracted_data["state"].pop(0)

                # pincode
                if len(text) >= 6 and text.isdigit():
                    extracted_data["pin_code"].append(text)
                elif re.findall('[a-zA-Z]{9} +[0-9]', text):
                    extracted_data["pin_code"].append(text[10:])

        extract_data(result)


        
        def create_dataframe(data):
            df = pd.DataFrame(data)
            return df


        data_frame = create_dataframe(extracted_data)
        st.success("### Data Extracted!")
        st.write(data_frame)

        if st.button("Upload to Database"):
            for i, row in data_frame.iterrows():
                # Store the image path instead of the image itself
                row['image'] = saved_image_path  # Update this with the image path

                # Perform insertion into the database
                sql = """INSERT INTO card_data(company_name, card_holder, designation, mobile_number, email, website, area, city, state, pin_code, image)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                mysql_cursor.execute(sql, tuple(row))
                mydb.commit()

            st.success("#### Uploaded to the database successfully!")

if selected == "Database":
    st.markdown("### Company Data from Database")

    # Input field for company name
    company_name_input = st.text_input("Enter Company Name:").lower()

    if st.button("Search"):
        if company_name_input:
            # Query to fetch data based on the company name
            search_query = f"SELECT * FROM card_data WHERE company_name LIKE '%{company_name_input}%'"
            mysql_cursor.execute(search_query)
            result = mysql_cursor.fetchall()

            if result:
                # Display the retrieved data
                st.success("Data Found!")
                retrieved_data = {
                    "Company Name": [row[1] for row in result],
                    "Card Holder": [row[2] for row in result],
                    "Designation": [row[3] for row in result],
                    "Mobile Number": [row[4] for row in result],
                    "Email": [row[5] for row in result],
                    "Website": [row[6] for row in result],
                    "Area": [row[7] for row in result],
                    "City": [row[8] for row in result],
                    "State": [row[9] for row in result],
                    "Pin Code": [row[10] for row in result]

                }
                retrieved_df = pd.DataFrame(retrieved_data)
                st.write(retrieved_df)
            else:
                st.warning("No data found for the given company name.")
        else:
            st.warning("Please enter a company name to search.")
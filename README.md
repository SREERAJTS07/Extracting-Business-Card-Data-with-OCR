# Business Card Data Extraction App

This Streamlit web application allows users to upload images of business cards and extract valuable information such as company names, cardholder details, contact information, and more using the EasyOCR library.

## How It Works

- **Image Upload:** Users can upload images (PNG, JPEG, JPG) of business cards.
- **Data Extraction:** The app uses OCR to extract text details from the images.
- **Information Display:** Extracted details are displayed along with the image preview.
- **Database Integration:** Users can choose to save extracted data to a MySQL database.

## Tools Used

- Streamlit: Simplifies web app creation in Python.
- EasyOCR: Enables optical character recognition on images.
- OpenCV (cv2): Handles image processing tasks.
- MySQL Connector: Interacts with a MySQL database.
- Pandas: For data manipulation and creating DataFrames.
- Matplotlib: Displays images and plots.


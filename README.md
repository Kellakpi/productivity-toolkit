# ⚒️ Productivity Toolkit


A unified desktop productivity app that brings together multiple tools developed across previous projects into a single, easy-to-use interface.
This project combines:
- A Pomodoro-style **Focus Timer**
- A searchable **Screenshot Vault** with image OCR, tagging, and notes
- An **Email Extractor** powered by regex

The goal is to create a centralised space for essential productivity tools — perfect for developers, researchers, students, or anyone who wants to stay organised and focused.

Each tool has been rebuilt and integrated from standalone prototypes (you can find on my profile), with improvements and a shared design system.

## Features

-**Focus Timer** (Pomodoro-style)
  - Customisable work/break sessions
  - Notifications when time is up

-**Screenshot Vault**
  - Upload and store image files
  - OCR support to extract text from images
  - Add **titles**, **notes**, and **tags** to images
  - Filter images by tags
  - Delete images
  - View full-size and thumbnail previews

-**Email Extractor**
  - Paste in text and extract valid email addresses using regex

## Future Plans

- Tag editing and sorting system  
- Drag-and-drop support  
- Responsive layout improvements  
- Export data and settings  
- AI, integration

## Installation and Current dependencies
tkinter

pillow

plyer

pytesseract

1. Clone the repository:
   ```bash
   git clone https://github.com/Kellakpi/productivity-toolkit.git
   cd productivity-toolkit
   pip install -r requirements.txt
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    python name_of_script(Main).py


from fastapi import FastAPI,File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import pytesseract

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post('/img')
async def get_img(file: UploadFile = File(...)):
    # Read the image file
    image_bytes = await file.read()
    # Perform OCR on the image
    text = ocr(image_bytes)
    # Return the extracted text
    return JSONResponse(content={"text": text}) 

def ocr(image_bytes):
    # Convert image bytes to PIL Image object
    image = Image.open(io.BytesIO(image_bytes))
    # Perform OCR using Tesseract
    text = pytesseract.image_to_string(image)
    return text
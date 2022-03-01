from fpdf import FPDF
from pdfrw import PageMerge, PdfReader, PdfWriter
import qrcode
from io import BytesIO
import os
from tickets.settings import BASE_DIR

IN_FILE = os.path.join(BASE_DIR, './pos/ticket_template_reduced.pdf')
OUT_FILE = './output.pdf'
ON_PAGE_INDEX = 0
UNDERNEATH = False

def new_content(serial, qr_text):
    fpdf = FPDF(orientation="landscape", format=(69,118))
    fpdf.add_page()
    fpdf.set_font("courier", size=14)
    fpdf.set_text_color(255,0,0)
    #fpdf.text(85,60, "00001")
    with fpdf.rotation(90, x=85,y=60):
        fpdf.text(84,64, "{0:05d}".format(serial))
    with fpdf.rotation(90, x=12,y=25):
        fpdf.text(12,29, "{0:05d}".format(serial))

    img = qrcode.make("https://entradas.ruralinfra.com/t/{}".format(qr_text))
    fpdf.image(img.get_image(), x=93, y=44, h=20, w=20)
    
    # Poner fecha
    #fpdf.set_text_color(75, 147, 183)
    #with fpdf.rotation(90, x=93,y=37):
    #    fpdf.text(93,41, "13")
    #with fpdf.rotation(90, x=4,y=32):
    #    fpdf.text(4,36, "13")

    reader = PdfReader(fdata=bytes(fpdf.output()))
    return reader.pages[0]

def generate_ticket(serial, qr_text):
    result = BytesIO()
    reader = PdfReader(IN_FILE)
    overlay = new_content(serial, qr_text)
    pm = PageMerge(reader.pages[0])
    pm.add(overlay, prepend=UNDERNEATH)
    pm.render()
    #PageMerge(writer.pagearray[ON_PAGE_INDEX]).add(new_content(), prepend=UNDERNEATH).render()
    writer = PdfWriter()
    writer.write(result, reader)
    result.flush()
    result.seek(0)
    return result

def new_content_complete(serial, qr_text, day):
    fpdf = FPDF(orientation="landscape", format=(69,118))
    fpdf.add_page()
    fpdf.set_font("courier", size=14)
    fpdf.set_text_color(255,0,0)
    #fpdf.text(85,60, "00001")
    with fpdf.rotation(90, x=85,y=60):
        fpdf.text(84,64, "{0:05d}".format(serial))
    with fpdf.rotation(90, x=12,y=25):
        fpdf.text(12,29, "{0:05d}".format(serial))

    img = qrcode.make("https://entradas.ruralinfra.com/t/{}".format(qr_text))
    fpdf.image(img.get_image(), x=93, y=44, h=20, w=20)
    
    # Poner fecha
    fpdf.set_text_color(75, 147, 183)
    with fpdf.rotation(90, x=93,y=37):
        fpdf.text(93,41, str(day))
    with fpdf.rotation(90, x=4,y=32):
        fpdf.text(4,36, str(day))

    reader = PdfReader(fdata=bytes(fpdf.output()))
    return reader.pages[0]

def generate_ticket_complete(serial, qr_text, day):
    result = BytesIO()
    reader = PdfReader(IN_FILE)
    overlay = new_content_complete(serial, qr_text, day)
    pm = PageMerge(reader.pages[0])
    pm.add(overlay, prepend=UNDERNEATH)
    pm.render()
    #PageMerge(writer.pagearray[ON_PAGE_INDEX]).add(new_content(), prepend=UNDERNEATH).render()
    writer = PdfWriter()
    writer.write(result, reader)
    result.flush()
    result.seek(0)
    return result
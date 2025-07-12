from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def minimal_task():
    """Solicita robots a RobotSpareBin Industries Inc.
Guarda el recibo HTML del pedido como archivo PDF.
Guarda la captura de pantalla del robot solicitado.
Incorpora la captura de pantalla del robot al recibo PDF.
Crea un archivo ZIP con los recibos y las imágenes."""
    browser.configure(
       # slowmo = 10,
    )
    open_the_intranet_website()
    get_orders()
    #fill_and_submit_orders_form()
    #click_yep()
    #order_another_robot()
    #export_as_pdf()
    archive_receipts()


###############################################################

def open_the_intranet_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()
    page.click("button:text('OK')")  
    page.click("button:text('Show model info')")

def get_orders():

    """Descarga el archivo CSV y lo guarda en la variable 'local_file' y genera un archivo .csv llamado 'Orders.csv' """
    http = HTTP()
    local_file = "orders.csv"
    http.download(url = "https://robotsparebinindustries.com/orders.csv", target_file=local_file, overwrite=True)
    
    """Lee el archivo (tabla) 'Orders.csv' y lo guarda en la variable 'table' para posteriormente 
    usarla en un formulario dentro de la pagina.
    Esta variable 'table' se usara para un for, el cuar recorre filas y columnas en las tablas y llena el formulario
    en la pagina de la forma que se encuentra en la 'fill_and_submit_orders_form' funcion """

    tables = Tables()
    table = tables.read_table_from_csv(local_file, header=True)
    
    
    for row in table:
        fill_and_submit_orders_form(row)

        
def order_another_robot():
    page = browser.page()
    page.click("#order-another")

def click_yep():
    page = browser.page()
    page.click("button:text('Yep')")

def fill_and_submit_orders_form(order):
    page = browser.page()
    head_names = {
            "1" : "Roll-a-thor head",
            "2" : "Peanut crusher head",
            "3" : "D.A.V.E head",
            "4" : "Andy Roid head",
            "5" : "Spanner mate head",
            "6" : "Drillbit 2000 head"
            }

    head_number = order["Head"]
    page.select_option("#head", head_names.get(head_number))
    page.click('//*[@id="root"]/div/div[1]/div/div[1]/form/div[2]/div/div[{0}]/label'.format(order["Body"]))
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])

    while True:
        page.click("button:text('Order')")
        order_another = page.query_selector("#order-another")

        if order_another:
            pdf_file = export_as_pdf(int(order["Order number"]))
            screenshot_file = screenshot_robot(int(order["Order number"]))
            add_pdf_screenshot(screenshot_file, pdf_file)
            order_another_robot()
            click_yep()
            break



    
def export_as_pdf(order_number):
    """Esta fun. convierte el recibo a pdf"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf_file = "output/pdf_of_receipts/receipt_number_{0}.pdf".format(order_number)
    pdf.html_to_pdf(receipt_html, pdf_file)
    return pdf_file

def screenshot_robot(order_number):
    """Takes screenshot of the ordered bot image"""
    page = browser.page()
    screenshot_file = "output/screenshots_of_robots/robot_number_{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_file)
    return screenshot_file


def add_pdf_screenshot(screenshot_file, pdf_file):
    pdf = PDF()
    pdf.open_pdf(pdf_file)
    pdf.add_watermark_image_to_pdf(image_path=screenshot_file, 
                                   source_path=pdf_file, 
                                   output_path=pdf_file)
    pdf.close_pdf()


def archive_receipts():
    lib = Archive () 
    lib.archive_folder_with_zip("./output/pdf_of_receipts" , "./output/receipts.zip")
 
    
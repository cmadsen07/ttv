import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, redirect, request, jsonify

CURRENT_PAGE = "100"
PREVIOUS_PAGE = "100"
IMAGE_SIZE_INFO = []

def scrape_site(page_num, sub_page=None):
    base_url = "https://www.dr.dk/cgi-bin/fttv2.exe/"
    sub_url = str(page_num)
    if sub_page != None:
        sub_url += "/" + sub_page
    response = requests.get(base_url + sub_url)
    soup = BeautifulSoup(response.content, "html.parser")
    map = soup.find("map")
    img = soup.find_all("img")[1]
    
    image_url = "https://www.dr.dk" + img.attrs["src"]

    
    print(map)
    return image_url, map

app = Flask(__name__)


@app.route("/")
def main():
    img_src, map = scrape_site(100)
    
    return render_template("index.html", img_src=img_src, map=map)

@app.route("/<page_num>")
def get_scrape(page_num):
    if "-" in page_num:
        main_page = page_num.split("-")[0]
        sub_page = page_num.split("-")[1]
    else:
        main_page = page_num
        sub_page = None
    
    global CURRENT_PAGE
    global PREVIOUS_PAGE
    PREVIOUS_PAGE = CURRENT_PAGE
    CURRENT_PAGE = main_page
    img_src, map = scrape_site(page_num, sub_page)
    
    
    return render_template("index.html", img_src = img_src, map=map)


@app.route("/select", methods=["GET", "POST"])
def select():
    number = request.form["number"]
   
    if number:
        try:
            int(number)
            return redirect("/"+str(number))
        except ValueError:
            return "Ikke en korrekt side."

@app.post("/tilbage")
def back():
    global CURRENT_PAGE
    temp_page = int(CURRENT_PAGE.split("-")[0])
    if temp_page > 100:
        temp_page -= 1
        
    CURRENT_PAGE = str(temp_page)
    return redirect("/"+ CURRENT_PAGE.split("-")[0])

@app.post("/frem")
def forward():
    global CURRENT_PAGE
    temp_page = int(CURRENT_PAGE.split("-")[0])
    if temp_page < 1000:
        temp_page += 1
    
    CURRENT_PAGE = str(temp_page)
    return redirect("/" + CURRENT_PAGE.split("-")[0])

@app.post("/returner")
def step_back():
    global PREVIOUS_PAGE
    
    return redirect("/" + str(PREVIOUS_PAGE))

@app.route('/get-image-size', methods=['POST'])
def get_image_size():
    data = request.get_json()
    width = data.get('width')
    height = data.get('height')
    url = data.get("url")
    
    d = url.split("/")
    page_num = [i for i in d if i][-1] # get last non-empty
    if "-" in page_num:
        main_page = page_num.split("-")[0]
        sub_page = page_num.split("-")[1]
    else:
        main_page = page_num
        sub_page = None
        
    global IMAGE_SIZE_INFO
    IMAGE_SIZE_INFO = [width, height, main_page, sub_page]
        
    return jsonify({'message': 'Image size received successfully', 'width': width, 'height': height})
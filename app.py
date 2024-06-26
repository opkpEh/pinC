from flask import Flask, request, jsonify, send_file, render_template
from pymongo import MongoClient
from bson.objectid import ObjectId
from io import BytesIO
from PIL import Image

app= Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['image_database']
images_collection = db['images']

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload/')
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error":" No Image file"}), 400

    image_file= request.files['image']

    if image_file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if image_file:
        image_binary = image_file.read()
        
        image_id = images_collection.insert_one({
            "filename": image_file.filename,
            "data": image_binary
        }).inserted_id
        
        return jsonify({"message": "Image uploaded successfully", "id": str(image_id)}), 201
        

@app.route('/image/<image_id>')
def get_image(image_id):
    image = images_collection.find_one({"_id": ObjectId(image_id)})
    
    if image:
        return send_file(
            BytesIO(image['data']),
            mimetype='image/jpeg', 
            as_attachment=True,
            download_name=image['filename']
        )
    else:
        return jsonify({"error": "Image not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
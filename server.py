from flask import Flask, request, jsonify
from flask import render_template
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId

app = Flask(__name__)

# Inisialisasi variabel global untuk MongoDB client
client = None
db = None
users_collection = None
products_collection = None

def init_mongodb():
    global client, db, users_collection, products_collection
    try:
        # MongoDB connection setup - menggunakan koneksi lokal
        MONGO_URI = "mongodb+srv://rifkialaudin5:rioad123@cluster1.kbick.mongodb.net/?retryWrites=true&w=majority&appName=cluster1"
        client = MongoClient(MONGO_URI)
        db = client.test_mongodb
        users_collection = db.users
        products_collection = db.products
        
        # Check MongoDB connection
        client.admin.command('ping')
        print("MongoDB connection successful!")
        return True
    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
        return False

# Inisialisasi MongoDB saat aplikasi dimulai
if not init_mongodb():
    print("Failed to initialize MongoDB. Exiting...")
    exit(1)

# Helper function to convert MongoDB Object to JSON-compatible format
def object_to_dict(obj):
    obj['_id'] = str(obj['_id'])
    return obj

@app.route('/')
def home():
    return render_template('index.html')

# CRUD routes for products
@app.route('/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        name = data.get('name')
        price = data.get('price')
        description = data.get('description', '')

        if not name or not price:
            return jsonify({'message': 'Name and price are required!'}), 400

        product = {
            'name': name,
            'price': float(price),
            'description': description
        }

        result = products_collection.insert_one(product)
        return jsonify({
            'message': 'Product created!', 
            'product_id': str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({'message': f'Error creating product: {str(e)}'}), 500

@app.route('/products', methods=['GET'])
def get_products():
    try:
        products = products_collection.find()
        products_list = [object_to_dict(product) for product in products]
        return jsonify(products_list), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching products: {str(e)}'}), 500

@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = products_collection.find_one({'_id': ObjectId(product_id)})
        if not product:
            return jsonify({'message': 'Product not found!'}), 404
        return jsonify(object_to_dict(product)), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching product: {str(e)}'}), 500

@app.route('/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.get_json()
        name = data.get('name')
        price = data.get('price')
        description = data.get('description')

        update_data = {}
        if name:
            update_data['name'] = name
        if price:
            update_data['price'] = float(price)
        if description:
            update_data['description'] = description

        if not update_data:
            return jsonify({'message': 'No fields to update!'}), 400

        result = products_collection.update_one(
            {'_id': ObjectId(product_id)}, 
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'message': 'Product not found!'}), 404

        return jsonify({'message': 'Product updated successfully!'}), 200
    except Exception as e:
        return jsonify({'message': f'Error updating product: {str(e)}'}), 500

@app.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        result = products_collection.delete_one({'_id': ObjectId(product_id)})
        if result.deleted_count == 0:
            return jsonify({'message': 'Product not found!'}), 404
        return jsonify({'message': 'Product deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'message': f'Error deleting product: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
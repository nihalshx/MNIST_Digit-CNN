from flask import Flask, render_template, request, jsonify
import torch
from PIL import Image
from torchvision.transforms import ToTensor, Normalize, Compose
from model import ImageClassifier  # Ensure model.py is in the same directory

app = Flask(__name__)
# Set the maximum file size to 16 MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# Load the model
clf = ImageClassifier()
clf.load_state_dict(torch.load('model_state.pt', map_location=torch.device('cpu')))
clf.eval()

# Define the transformation
transform = Compose([
    ToTensor(),  # Convert image to tensor
    Normalize((0.5,), (0.5,))  # Normalize according to MNIST dataset specifics
])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    try:
        img = Image.open(file).convert('L')  # Convert the image to grayscale (L mode for MNIST)
        img_tensor = transform(img).unsqueeze(0)  # Apply the transform and add batch dimension
        with torch.no_grad():
            prediction = torch.argmax(clf(img_tensor)).item()  # Get the predicted digit
    except Exception as e:
        return jsonify({'error': str(e)})

    return jsonify({'digit': prediction})

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, render_template
import numpy as np
from PIL import Image
import tensorflow as tf
from background_remover_function import generate_mask, remove_background, postprocess, extract_foreground
from waitress import serve

app = Flask(__name__)
#app.debug = True  # Enable debug mode for detailed error messages

# Load the trained model
model = tf.keras.models.load_model(r'background_remover_model.h5')
# Define the desired input and output dimensions
input_dimension = (64, 64)  # Adjust according to your model's input size
output_dimension = (64, 64)  # Adjust according to your desired output size

print('Model loaded. Start serving...')
print('Model loaded. Check http://127.0.0.1:8000/')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/prediction', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            # Get the uploaded file
            file = request.files['file']
            # Load the image from file
            img = Image.open(file).convert('RGB')
            # Resize the image to match the input size of the model
            resized_img = img.resize(input_dimension)
            # Perform background removal
            mask = generate_mask(np.array(resized_img))
            foreground = extract_foreground(np.array(resized_img), mask)
            background = remove_background(np.array(resized_img), mask)
            result = postprocess(foreground)
            resized_result = Image.fromarray(result).resize(output_dimension)
            # Convert the result back to a PIL Image
            #result_image = Image.fromarray(result)
            
            # Render the template with the input and output image arrays as base64 strings
            input_image = image_to_base64(resized_img)
            output_image = image_to_base64(resized_result)
            return render_template('result.html', input_image=input_image, output_image=output_image)
        except Exception as e:
            return f"An error occurred: {str(e)}"

def image_to_base64(image):
    # Convert PIL Image to base64 string
    from io import BytesIO
    import base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

"""if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8000,channel_timeout=600)
    #serve(app, host='0.0.0.0', port=8000, threads=1, channel_timeout=600)"""
if __name__ == '__main__':
    #app.run(port=8000)
    serve(app, host='0.0.0.0', port=8000,channel_timeout=600)

# Nama : Zelda Elisa Hijry
# NIM : 230401010046
# Kelas : IF502
# Mata Kuliah : Kriptografi dan Steganografi


# Secret message
secret_message = 'AKU'

def text_to_binary(text):
    binary_representation = ''
    for char in text:
        ascii_value = ord(char)
        binary_char = f'{ascii_value:08b}'
        binary_representation += binary_char
    return binary_representation

binary_representation = text_to_binary(secret_message)

print(f"Original message: {secret_message}")
print(f"Binary representation: {binary_representation}")

import numpy as np

red_channel = 120   # 01111000
green_channel = 150 # 10010110
blue_channel = 200  # 11001000

print(f"Original Pixel Channel Values:\n")
print(f"Red Channel:   {red_channel} (binary: {red_channel:08b})")
print(f"Green Channel: {green_channel} (binary: {green_channel:08b})")
print(f"Blue Channel:  {blue_channel} (binary: {blue_channel:08b})\n")

secret_bit_red = int(binary_representation[0]) # '0'
secret_bit_green = int(binary_representation[1]) # '1'
secret_bit_blue = int(binary_representation[2]) # '0'

print(f"Secret Message Bits for embedding (first 3 bits of 'AKU' binary):\n")
print(f"Secret Bit for Red Channel:   {secret_bit_red}")
print(f"Secret Bit for Green Channel: {secret_bit_green}")
print(f"Secret Bit for Blue Channel:  {secret_bit_blue}\n")

def illustrate_lsb_modification(original_value, secret_bit, channel_name):
    original_binary = f'{original_value:08b}'
    original_lsb = int(original_binary[-1])

    modified_binary = original_binary[:-1] + str(secret_bit)
    modified_value = int(modified_binary, 2)

    print(f"--- {channel_name} Channel ---")
    print(f"Original decimal: {original_value}")
    print(f"Original 8-bit binary: {original_binary}")
    print(f"Original LSB: {original_lsb}")
    print(f"Secret bit to embed: {secret_bit}")
    print(f"Modified 8-bit binary: {modified_binary}")
    print(f"Modified decimal: {modified_value}")
    print(f"Difference: {modified_value - original_value}\n")

print(f"\n--- LSB Embedding Illustration ---\n")
illustrate_lsb_modification(red_channel, secret_bit_red, "Red")
illustrate_lsb_modification(green_channel, secret_bit_green, "Green")
illustrate_lsb_modification(blue_channel, secret_bit_blue, "Blue")

import imageio.v3 as iio
import numpy as np

cover_image_path = 'cover_image.png'
try:
    original_image = iio.imread(cover_image_path)
    print(f"Image loaded successfully from {cover_image_path}. Shape: {original_image.shape}, Dtype: {original_image.dtype}")
except FileNotFoundError:
    print(f"Error: The file '{cover_image_path}' was not found. Please upload it to your Colab environment.")
    original_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    print("Using a dummy image for demonstration purposes.")

if original_image.ndim == 2: # Grayscale image
    original_image = np.stack([original_image, original_image, original_image], axis=-1) # Convert to RGB
    print("Converted grayscale image to RGB.")

delimiter = '1111111111111110' # 14 '1's followed by a '0'

data_to_embed = binary_representation + delimiter

print(f"\nBinary representation of 'AKU': {binary_representation}")
print(f"Delimiter: {delimiter}")
print(f"Data to embed (binary 'AKU' + delimiter): {data_to_embed}")
print(f"Total bits to embed: {len(data_to_embed)}")

def embed_message(image, binary_message):
    # 1. Create a writable copy of the input image
    stego_image = np.copy(image).astype(np.uint8) # Ensure it's uint8 for operations
    height, width, channels = stego_image.shape
    image_capacity = height * width * channels

    # Check if the message can fit in the image
    if len(binary_message) > image_capacity:
        print(f"Error: Message is too large to embed. Image capacity: {image_capacity} bits, Message length: {len(binary_message)} bits.")
        print("Embedding partial message.")
        # Trim the message to fit the image capacity
        binary_message = binary_message[:image_capacity]

    data_idx = 0
    message_length = len(binary_message)

    # 2. Iterate through the binary_message bit by bit and embed into LSBs
    for row in range(height):
        for col in range(width):
            for channel in range(channels):
                if data_idx < message_length:
                    pixel_value = stego_image[row, col, channel]
                    secret_bit = int(binary_message[data_idx])

                    # Clear the LSB of the pixel_value using 0xFE (254) for uint8
                    # This avoids the OverflowError caused by ~1 resulting in -2
                    pixel_value = (pixel_value & 0xFE)

                    # Embed the secret bit into the LSB of the pixel_value
                    pixel_value = pixel_value | secret_bit

                    # Update the stego_image with the new pixel_value
                    stego_image[row, col, channel] = pixel_value
                    data_idx += 1
                else:
                    # All bits embedded
                    print(f"Successfully embedded {data_idx} bits into the image.")
                    return stego_image

    print(f"Successfully embedded {data_idx} bits into the image.")
    return stego_image

# Call the embed_message function
steganographic_image = embed_message(original_image, data_to_embed)

# Print a message indicating whether the embedding was successful and the shape
if steganographic_image is not None:
    print(f"Steganographic image created successfully. Shape: {steganographic_image.shape}, Dtype: {steganographic_image.dtype}")
else:
    print("Steganographic image creation failed.")

stego_image_path = 'steganographic_image.png'
iio.imwrite(stego_image_path, steganographic_image)
print(f"Steganographic image saved successfully as '{stego_image_path}'.")

import imageio.v3 as iio

# Load the steganographic image
loaded_stego_image = iio.imread(stego_image_path)

print(f"Steganographic image loaded successfully from '{stego_image_path}'. Shape: {loaded_stego_image.shape}, Dtype: {loaded_stego_image.dtype}")

def extract_message(image, delimiter):
    binary_message = []
    height, width, channels = image.shape
    delimiter_len = len(delimiter)

    for row in range(height):
        for col in range(width):
            for channel in range(channels):
                # Extract the LSB from the pixel value
                pixel_value = image[row, col, channel]
                lsb = pixel_value & 1  # Get the last bit
                binary_message.append(str(lsb))

                # Check if the delimiter has been found
                if len(binary_message) >= delimiter_len:
                    current_segment = "".join(binary_message[-delimiter_len:])
                    if current_segment == delimiter:
                        # Remove the delimiter from the extracted message
                        return "".join(binary_message[:-delimiter_len])

    # If delimiter not found or message too long to fit
    print("Warning: Delimiter not found in the image or message is incomplete.")
    return "".join(binary_message)

# Helper function to convert binary string back to text
def binary_to_text(binary_string):
    message = []
    # Group binary string into 8-bit chunks
    for i in range(0, len(binary_string), 8):
        byte = binary_string[i:i+8]
        if len(byte) == 8:
            message.append(chr(int(byte, 2)))
    return "".join(message)

# Extract the hidden message
extracted_binary = extract_message(loaded_stego_image, delimiter)

# Convert the extracted binary message back to text
extracted_message = binary_to_text(extracted_binary)

print(f"Extracted binary message: {extracted_binary}")
print(f"Extracted text message: {extracted_message}")
print(f"Original secret message: {secret_message}")

# Verify if the extracted message matches the original
if extracted_message == secret_message:
    print("Message extraction successful! The extracted message matches the original.")
else:
    print("Message extraction failed. The extracted message does not match the original.")

import matplotlib.pyplot as plt

# Create a figure with two subplots
fig, axes = plt.subplots(1, 2, figsize=(12, 6))

# Display the original image
axes[0].imshow(original_image)
axes[0].set_title('Original Image')
axes[0].axis('off')

# Display the steganographic image
axes[1].imshow(steganographic_image)
axes[1].set_title('Steganographic Image (with hidden message)')
axes[1].axis('off')

plt.tight_layout()
plt.show()

print("Visual comparison of Original and Steganographic Images.")
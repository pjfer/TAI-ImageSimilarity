import sys
import io
import gzip
import bz2
import lzma
from PIL import Image




class Ncd:

    algorithm = ""

    def __init__(self, algorithm):

        self.algorithm = algorithm

    # convert image to byte array
    def image_to_byte_array(self, image):
        byteIO = io.BytesIO()
        image.save(byteIO, format='PPM')
        # return the byte array
        return byteIO.getvalue()


    # compresse a byte array, given an algorithm
    def compress_image(self, image_byte_array):
        if self.algorithm == "gzip":
            return gzip.compress(image_byte_array)
        elif self.algorithm == "bzip2":
            return bz2.compress(image_byte_array)
        elif self.algorithm == "lzma":
            return lzma.compress(image_byte_array)
        else:
            print("Invalid compressing algorithm")
            sys.exit(1)



    # with the bytes arrays, computes the value of the ncd
    def compute_ncd(self, compressed_concat_image, compressed_image_x, compressed_image_y):
        compressed_concat_image_bits = sys.getsizeof(compressed_concat_image) * 8
        compressed_image_x_bits = sys.getsizeof(compressed_image_x) * 8
        compressed_image_y_bits = sys.getsizeof(compressed_image_y) * 8
        return (compressed_concat_image_bits - min([compressed_image_x_bits, compressed_image_y_bits]))/max([compressed_image_x_bits, compressed_image_y_bits])


    def classify(self, train_set, image_y):
        # concat the 2 images 
        # this will result in a RGB image, instead of a PPM image
        # later, we will also convert the 2 images to RGB, so we can compare all of them
        results = []
        for image_x in train_set:
            total_width = image_x.size[0] + image_y.size[0]
            max_height = image_x.size[1] if  image_x.size[1] > image_y.size[1] else image_y.size[1]
            
            concatenated_image = Image.new('RGB', (total_width, max_height))

            # paste the 2 images together (horizontally)
            x_offset = 0
            for im in [image_x, image_y]:
                concatenated_image.paste(im, (x_offset,0))
                x_offset += im.size[0]

            # image_x to RGB
            width, height = image_x.size
            image_x_rgb = Image.new('RGB', (width, height))  
            image_x_rgb.paste(image_x)

            # image_y to RGB
            width, height = image_y.size
            image_y_rgb = Image.new('RGB', (width, height))  
            image_y_rgb.paste(image_y)

            # all images to byte arrays
            concatenated_image_byte_array = self.image_to_byte_array(concatenated_image)
            image_x_byte_array = self.image_to_byte_array(image_x_rgb)
            image_y_byte_array = self.image_to_byte_array(image_y_rgb)

            # compress images
            concatenated_image_compressed = self.compress_image(concatenated_image_byte_array)
            image_x_compressed = self.compress_image(image_x_byte_array)
            image_y_compressed = self.compress_image(image_y_byte_array)

            # compute NCD
            results.append(self.compute_ncd(concatenated_image_compressed, image_x_compressed, image_y_compressed))
        return min(results)
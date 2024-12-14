import os  #Import the os module for file and directory operations
import pygame  

def import_folder(path):
    surface_list = []  #Initialize an empty list to hold the surfaces

    #Walk through the directory at the specified path
    for _, _, img_files in os.walk(path): 
        for image in img_files:  #Iterate over each image file found
            full_path = path + '/' + image  #Construct the full path to the image file
            image_surf = pygame.image.load(full_path).convert_alpha()  #Load the image and convert it for better performance
            surface_list.append(image_surf)  #Add the loaded surface to the list
    return surface_list  #Return the list of surfaces

def import_folder_dict(path):
    surface_dict = {}  #Initialize an empty dictionary to hold the surfaces

    #Walk through the directory at the specified path
    for _, __, img_files in os.walk(path):
        for image in img_files:  #Iterate over each image file found
            full_path = path + '/' + image  #Construct the full path to the image file
            image_surf = pygame.image.load(full_path).convert_alpha()  #Load the image and convert it for better performance
            surface_dict[image.split('.')[0]] = image_surf  #Use the image filename (without extension) as the key and the surface as the value

    return surface_dict  
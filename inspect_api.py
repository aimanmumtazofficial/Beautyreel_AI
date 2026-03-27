from gradio_client import Client 


#connect to the space 
client = Client("multimodalart/stable-video-diffusion")

#This will print out all available functions
print(client.view_api)
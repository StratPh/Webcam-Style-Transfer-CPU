# Live Webcam Style Transfer (Docker + TensorFlow)

This project applies real-time neural style transfer to a webcam feed using TensorFlow Hub and streams the processed video live to your browser using Flask. The project was developed entirely on Linux using Docker, so there may be compatibility issues depending on the webcam or operating system you are using.

##Building
Using Docker, build the image from the project root with:

docker build -t webcam_styletransfer .


## Running the Container
### Linux
After building the image, you should be able to run the container with:

docker run --rm -it \
  --device=/dev/video0:/dev/video0 \
  -p 8000:8000 \
  webcam_styletransfer

### Windows
After building the image, you should be able to run the container with:

docker run --rm -it `
  -p 8000:8000 `
  webcam_styletransfer

## Viewing the Feed
After Running Access the Feed on your Browser with:

http://localhost:8000

## Note 
This project was created purely for learning and practice purposes. Performance is very limited, as the entire pipeline runs on the CPU. Performance could be significantly improved by enabling CUDA and running the model on a GPU.

### Issues 
If the webcam is not detected on Linux, list the available video devices with:

ls /dev/video*

Then update the --device flag in the run command to match the desired device:

 docker run --rm -it \
  --device=/dev/video0:/dev/video0 \ 
  -p 8000:8000 \
  webcam_styletransfer

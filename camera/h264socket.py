import socket, time
import picamera

# Start a socket listening for connections on 0.0.0.0:8554 (0.0.0.0 means
# all interfaces)
server_socket = socket.socket()

server_socket.bind(('0.0.0.0', 8000))
#server_socket.close()
server_socket.listen(0)
print("Connection initialisée. En attente de client")

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.preview_fullscreen = False
camera.preview_window = (100,100,640,400)

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('rwb')
       
# Start a preview and let the camera warm up for 2 seconds
#camera.start_preview()
time.sleep(2)
# Start recording
       
camera.start_recording(connection, format='h264')

try:
    while 1:
        camera.wait_recording()
 
except KeyboardInterrupt:
    camera.close()
    connection.close()
    server_socket.close()
    print("Keyboard Interrupt !")
           
finally:
    connection.close()
    server_socket.close()
    print("Normal close")
# python-auto-painter

Auto painter and timelapse maker for the drawings in my IG page [@aqueleangelo](https://www.instagram.com/aqueleangelo/)

![](banner.png)

It gets a linework (if there's any) from a folder in my google drive, paints it, makes a collage, video time lapse of the process and then places it in another drive folder.
With some modification, could be used to paint other styles.

Results posted daily at [@aqueleangelo](https://www.instagram.com/aqueleangelo/)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This was built in python 3.8, with the lasted versions of all modules as today *(2020/7/6)*. 

It uses two different APIS tho get color pallets and names. See 'Built with' section.

#### Modules
You will need a bunch of different modules, check the 'autopainter.py' and 'gdriveservice.py' for the names.
#### How and what images to feed the program
* The image input need to be located at a drive folder in root called 'bloob_buffer' (you could change this).
* The image input need to be in the '.jpg' (you could change this) .
* The image input feed need to be in 'portrait mode' (that is the height of the image > width) (you "can't" change this).
The program will run fine with landscape images, but it will rotate it to portrait. It's a fix, don't question it.
* The cleaner the input, the better the result (and least likeliness that it breaking horribly)
* The optimal number of whole 'pictures' inside the image is 4 (see the image above)
* The results will be uploaded back to drive in a folder called 'Bloobs' (you could change this).
#### Timelapse audio
* The audio clips need to be '.mp3' and called 'tune_' + random.choice(blob.blob(audioFolderPath + '*.mp3') + '.mp3'. I can't decribe it a better way (also you could change this).
* Check the folder, there are examples.
* The audio needs to be about 10 seconds long to get the intended result.

### Installing

1. Download or clone the repository
2. You will need 3 additional folders named 'Images', 'Lines' and 'Frames' at the root folder, create them.
2. 


## Deployment

I implemented this in a [pythonanywhere](https://www.pythonanywhere.com/) live server to get advantage from the task schedule, 
so I don't have to mannualy start the process for new lines daily. Thats easily achievable, just copy all the code, folders and follow the installing accordingly. Change paths as needed.

*OBS.: If you have any problem related to sockets there, reinstalling the pysockets module solved it here. Also Google is your friend.*

## Built With

* Python with a bunch of modules. Most notably the 'requests', 'PIL', 'cv2', 'moviepy' and the google drive ones.

## Authors

* **Angelo Leite** - *Initial work* - [angelolmg](https://github.com/angelolmg)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* People from [colormind.com](http://colormind.io/)
* People from [herokuapp.com](https://random-word-api.herokuapp.com/home)
* People from [pythonanywhere.com](https://www.pythonanywhere.com/)


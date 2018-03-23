# Instagram-Net
Ever had trouble choosing a picture to post on Instagram? Look no further... let ML do the work for you.

## Getting Started

Download the repo, create a directory called "examples" in the root folder, add your potential pictures into that directory, and then call the Python 3 predict.py script inside the "Predict Score" subfolder. As of now, the project only has a script version, so stay tuned for an easier to use alternative.

URGENT: As of now predict won't work because of issues with loading weights for a model that was trained as a multi_gpu_model. I only just realized this as my previous predict runs took place on my Desktop, on which I could use the multi_gpu_model directly. I am currently in the process of retraining, reuploading, and fixing the script.

### Prerequisites

Python, Glob, Keras, tensorflow, associated essentials.

## Built With

* [Keras](https://keras.io) - The deep learning framework used
* [Tensorflow](https://www.tensorflow.org) - The Keras backend used
* [Age/Gender Prediction Model](https://github.com/yu4u/age-gender-estimation) - Used to separate dataset into male/female subsets

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* yu4u's Age/Gender Prediction model — helped me save a lot of time and provided another type of model to try out when finetuning
* All my friends who kept asking me to judge their Instagram pictures to the point where I just had to try this out

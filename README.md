# Clearing bubbles and translating them

This project is made for manga/manhwa/webtoons and its main purpose is to clear the contaiment of the bubble and translate it

## Usage

Clone the GitHub project into your computer

```bash
# Clone the repository
git clone https://github.com/AnnaSusak/textInBubbleDetecting
```

Install libraries from *requirements.txt*

```commandline
pip install -r requirements.txt
```

## What's used

We're using:
1) **Roboflow**
   * [Self-made dataset](https://universe.roboflow.com/nekkon/bubble-text-detector/model/3) of bubbles from manga in 5 languages(English, Japanese, Chinese, Korean and Russian) for text scan in the bubble
   * [Self made dataset](https://universe.roboflow.com/rely/bubble-nd1xn/model/2) of manga/webtoon images with splitted bubbles.
2) **ChatGPT 3.5 API** for translation
3) **Google API** for translation
4) **Yandex translate API** for translation


## How to start
How we've said earlier, we use API of ChatGPT, Roboflow, Yandex and ChatGPT. To set up our code on your device you need to upload 2 files.
First file - **api_keys.json**, with this setup:
```
{
  "chat_gpt": "-",
  "yandex": "-",
  "roboflow": "-"
}
#Instead of "-" use your own keys
```

Also, you need to use other file with Google API and name it **google_api.json**. How to do that you can learn from [this website](https://developers.google.com/maps/documentation/javascript/get-api-key?hl=en)


## Why this project works
To put it simply, we use 2 models:
1) First one can split a page into pieces and return a list of text bubbles or back text(text on the page without any bubbles)
2) Second one takes the piece from the first model and finds text on it.

After that we just use the coordinates of found bound and fill it
For fill you can choose from two variants:
* Plain color, you can choose for you own, but at the setup program will automatically choose the best variant. Better to choose this variant then you are working with plain-colored bubbles
* *Smart* variant from OpenCV library, that fills space by itself.

## Made by:
1) [Nekkon](https://github.com/NELKIO)
2) [Anna Susak](https://github.com/AnnaSusak)
3) [Sundew](https://github.com/Sundew999666)
4) [Danosito](https://github.com/danosito)

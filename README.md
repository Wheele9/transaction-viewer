# transaction-viewer

This project contains a python based program, which allows to inspect account history

## Backstory

My bank (OTP Bank Nyrt) does not allow to watch my transactions on the internet, only a period of a month at once. Unfortunately the start of this period can not be older than three months. These artifical restrictions's aim is to be less conscious about my finances, so I wrote this application.

## Inner workings

The inputs of this program are .csv files exported from my netbank. I parse them using pandas, numpy, and I create the plots using matplotlib. This program is tested on python3.6 on Ubuntu 16.04 and Win7. On Windows it is pretty laggy, I try to solve that.

## Contact

Feel free to try it. I uploaded two dummy csv-s to play with. The parser class, and the plotting class are a bit tangled into each other right now. But it's not that hard to write your own parser based on your own csv-s, and with a little modification on the plotting class, it shall work. Contact me if you have any questions.

## Current features

### Zooming

![alt tag](https://github.com/Wheele9/transaction-viewer/blob/master/images/blrFigure_1-1.png)

### Showing attributes of selected transaction

![alt tag](https://github.com/Wheele9/transaction-viewer/blob/master/images/blurredwindow.png)

### Scaling can be selected



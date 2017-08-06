# transaction-viewer

This program allows you to inspect your bank account history

## Backstory

My bank (OTP Bank Nyrt) does not allow to watch my transactions on the internet, only a period of a month at once. Unfortunately the start of this period can not be older than three months. These artifical restrictions's aim is to be less conscious about my finances, so I wrote this application.

## Inner workings

The inputs of this program are .csv files exported from my netbank. I parse them using some awesome python packages, like pandas, numpy, and I create the plots using matplotlib. This program is tested on python3.6 on Ubuntu 16.04 and Win7. On Windows it is pretty laggy, I try to solve that.

On the upper plot you can see the whole range of transactions, which were parsed. On the bottom plot you can see the whole range, or a part of it, as you wish. Use the radio buttons to change properties and enjoy :)

## Features

### Zooming

You can select with the mouse any period on the upper plot, and zoom into it. The details will be more clear on the bottom plot now.

![alt tag](https://github.com/Wheele9/transaction-viewer/blob/master/images/select.png)

### Scale selection

You can change between linear and logarithmic view, using the radiobuttons on the right. Try both of them! :)

![alt tag](https://github.com/Wheele9/transaction-viewer/blob/master/images/scales.png)

### Selection between balance view vs transaction view

With the radiobuttins, you can select whether you wanna see the transactions, or your balance on the upper plot. Zooming works in both ways.

![alt tag](https://github.com/Wheele9/transaction-viewer/blob/master/images/balance.png)

### Inspection

On the bottom plot, you can click into any of the rectangles (each of them represents a single transaction), and you can see some
basic information about this transaction, such as date, sum, comment.

![alt tag](https://github.com/Wheele9/transaction-viewer/blob/master/images/selection.png)

More features are on the way, feel free to suggest one, if you need something.

## Contact

Feel free to try it. If you are not at OTP Bank, you can rewrite the parser class, and things should work.



# Salary chart

Take a look at the purchasing power of your salary.

The very beta shitty version is here.

```{sh}
git clone https://github.com/neseleznev/salary-chart
cd salary-chart

pip3 install -U -r requirements.txt
python3 chart_builder.py
```

Change the hardcoded array in the bottom of **chart_builder.py** and here you go


## Example

Consider Wasёq, typique worker at 'Zavod, LLC'.

He though he was gaining his wage every two years, 
however, real money he's getting (adjusted by purchasing power) increased just a little.

Moreover, in USD equivalent, Vasiliy lost more than 25&nbsp;% of his salary.  

![Sad Wasёq story](https://github.com/neseleznev/salary-chart/blob/master/wasek.svg "Sad Wasёq story")


## Purchasing power data

I've serialized and added all available data from 1991 till Mar, 2020.

Everytime script is runned, all the latest data will be automatically downloaded.

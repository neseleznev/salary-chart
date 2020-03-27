# Especially for @Komdosh

The very beta shitty version is here

```{sh}
pip3 install -U -r requirements.txt
python3 chart_builder.py
```

Change the hardcoded array in the bottom of **chart_builder.py** and here you go


## Update purchasing power data

I've serialized and added all available data from 1991 till Aug, 2019.
You may update the data running the following script

```{sh}
python3 download_purchasing_power.py
```

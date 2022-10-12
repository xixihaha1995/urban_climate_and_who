'''
1. Request gif from url, daily temperature plot
2. Extract temperature data from gif
3. Save data to csv
'''
from PIL import Image

# Import modules
import requests
import numpy as np
import pandas as pd


# Define functions
def get_gif(url, filename):
    '''
    1. Request gif from url, daily temperature plot
    2. Save gif to file
    '''
    # Request gif from url
    r = requests.get(url, stream=True)
    # Save gif to file
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    return filename

def extract_data(filename):
    '''
    1. Display gif
    2. get lines of data
    3. get data from lines
    4. save data to csv
    '''
    # Display gif
    im = Image.open(filename)
    im.show()
    # Extract temperature data from gif
    data = np.array(Image.open(filename))
    # Save data to csv
    df = pd.DataFrame(data)
    df.to_csv('Vancouver_temperature.csv', index=False)
    return df

# Main
if __name__ == '__main__':
    # Request gif from url, daily temperature plot
    url = 'https://ibis.geog.ubc.ca/~epicc/webdata/resources/images/WI_DT_2008_360.gif'
    filename = 'Vancouver_temperature.gif'
    get_gif(url, filename)
    # Extract temperature data from gif
    extract_data(filename)
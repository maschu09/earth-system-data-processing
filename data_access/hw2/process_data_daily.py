import requests
from datetime import datetime
import pandas as pd

url = 'https://jsonplaceholder.typicode.com/posts'
response = requests.get(url)

if response.status_code == 200:
    print("Request was successful!")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")


# convert response to JSON format
data = response.json()

if response.status_code == 200:
    data = response.json()
    print(f'Retrieved {len(data)} posts.')

    # Create a DataFrame from the JSON data
    df = pd.DataFrame(data)
    print(df.head())
else:
    print(f'Failed to retrieve data: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    print(f'Retrieved {len(data)} posts.')
    df = pd.DataFrame(data)
    # Save DataFrame to CSV
    df.to_csv('posts_data.csv', index=False)
else:
    print(f'Failed to retrieve data: {response.status_code}')    
from datetime import datetime, timedelta
import xarray as xr
import rioxarray as rx
import pandas as pd

import multiprocessing
from functools import partial

from concurrent.futures import ThreadPoolExecutor


def generate_yearly_dates(start_date_str, end_date_str):
    """
    Generates start and end dates for each year within a given range.

    Args:
        start_date_str (str): The start date in "YYYY-MM-DD" format.
        end_date_str (str): The end date in "YYYY-MM-DD" format.

    Returns:
        list: A list of tuples, where each tuple contains the start and end dates
              for a year in "YYYY-MM-DD" format.
    """

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    yearly_dates = []
    current_year = start_date.year

    while current_year <= end_date.year:
        year_start = datetime(current_year, 1, 1)
        year_end = datetime(current_year, 12, 31)

        if year_start < start_date:
            year_start = start_date

        if year_end > end_date:
            year_end = end_date

        yearly_dates.append((year_start.strftime("%Y-%m-%d"), year_end.strftime("%Y-%m-%d")))
        current_year += 1

    return yearly_dates

measurements = ["rainfall"]
crs = "EPSG:4326"
resolution = 0.05
bbox = [30.80, 2.48, 32.04, 3.87]

def query_data(start_date,end_date,catalog,bbox,collections):
    
    query = catalog.search(
        bbox=bbox,
        collections=collections,
        datetime=f"{start_date}/{end_date}",
    )
    
    items = list(query.items())
    print(f"Found: {len(items):d} datasets")
    return items
    
def process_item(item):
    """Processes a single item and returns the resulting data_array or None."""
    try:
        data_array = rx.open_rasterio(item.assets['rainfall'].href)#, chunks={'x': 1024, 'y': 1024})
        timestamp = item.properties['start_datetime']
        data_array['time'] = timestamp
        data_array = data_array.expand_dims(dim='time')
        data_array = data_array.squeeze('band')
        data_array.name = 'rainfall'
        return data_array
    except Exception as e:
        print(f"Error loading item {item.id}: {type(e)}, {e}")
        return None

def process_query_result(items,num_threads = 20):

    datasets = []
    # for item in items:
    #     try:
    #         # data_array = rx.open_rasterio(item.assets['rainfall'].href, chunks={'x': 25, 'y': 29})
    #         data_array = rx.open_rasterio(item.assets['rainfall'].href, chunks={}) #accesses a dictionary named 'assets' within the current item. then access entry in the 'assets' dictionary that corresponds to the key 'rainfall'
    #         # timestamp = item.properties['datetime']
    #         timestamp = item.properties['start_datetime'] #access properties dictioinary, access value associated with start_datetime key
    #         data_array['time'] = timestamp # adds a coordinate named 'time' = timestamp to the data_array
    #         data_array = data_array.expand_dims(dim='time') #increases the dimensionality of the data_array by adding a new dimension named 'time'.
    #         data_array = data_array.squeeze('band') #remove "band" dimenion. 
    #         data_array.name = 'rainfall' # set the name of the DataArray
    #         datasets.append(data_array)
    #         # print(f"Data appended for {item}")
    #     except Exception as e:
    #         print(f"Error loading item {item.id}: {type(e)}, {e}")
    print('processing items...')
    with multiprocessing.Pool() as pool:
        results = pool.map(process_item, items)

    # Filter out None values (items that failed to process)
    datasets = [result for result in results if result is not None]

    # with ThreadPoolExecutor(max_workers=num_threads) as executor:
    #     results = list(executor.map(process_item, items))  # Use list() to force evaluation

    # # Filter out None values (items that failed to process)
    # datasets = [result for result in results if result is not None]

    print('processing datasets...')
    if datasets:
        try:
            ds_manual_array = xr.concat(datasets, dim='time') # Concatenate into a DataArray
            ds_manual = ds_manual_array.to_dataset(name='rainfall') # Convert to a Dataset with 'rainfall' as the variable
            ds_manual = ds_manual.rio.write_crs(crs)
            ds_manual = ds_manual.rio.reproject(crs, resolution=resolution, transform=None)
            ds_manual = ds_manual.sel(x=slice(bbox[0], bbox[2]), y=slice(bbox[3], bbox[1])) # Apply bbox for consistency
        except Exception as e:
            print(f"Error concatenating datasets: {e}")
            ds_manual = None
    else:
        ds_manual = None
    print('aggregating...')
    regional_rainfall_average = ds_manual['rainfall'].mean(dim=['x', 'y'])
    daily_rainfall = regional_rainfall_average.to_dataframe().sort_index().drop(["band","spatial_ref"], axis = 1)
    # daily_rainfall
    print('indexing...')
    daily_rainfall.index = pd.to_datetime(daily_rainfall.index)
    return daily_rainfall




    

# Example usage
# start_date = "1981-01-01"
# end_date = "2022-12-31"

# yearly_ranges = generate_yearly_dates(start_date, end_date)

# for start, end in yearly_ranges:
#     print(f"Year: {start[:4]}, Start: {start}, End: {end}")
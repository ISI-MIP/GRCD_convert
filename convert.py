#!/usr/bin/python3.8

# author: Matthias Büchner, buechner@pik-potsdam.de

import netCDF4 as nc
import numpy as np

ref_year = '1700'

file = 'GRDC-Monthly.nc'

dataset = nc.Dataset(file)

n_stations = dataset.dimensions['id'].size
n_timesteps = dataset.dimensions['time'].size

for id in range(0, n_stations):
    ds_lat = dataset.variables['geo_x'][id]
    ds_lon = dataset.variables['geo_y'][id]
    ds_height = dataset.variables['geo_z'][id]
    ds_owner = dataset.variables['owneroforiginaldata'][id]
    ds_river = dataset.variables['river_name'][id].replace(' RIVER','')
    if ds_river == 'PARANA, RIO':
        ds_river = 'RIO PARANA'

    ds_station_name = dataset.variables['station_name'][id]
    ds_timezone = dataset.variables['timezone'][id]
    ds_grdc_number = dataset.variables['id'][id]
    print(id + 1,',',ds_lat,',',ds_lon,',',ds_height,',',ds_owner,',',ds_river,',',ds_station_name,',',ds_grdc_number,',',ds_timezone)
    ds_discharge = dataset.variables['runoff_mean'][:,id]
    ds_flag = dataset.variables['flag'][:,id]
    ds_time = dataset.variables['time'][:]

    # some adjustments for the output file names
    ds_station_name_netcdf = ds_station_name.replace(' - ', '-').replace('VICKSBURG, MS', 'VICKSBURG-MS').replace('(764.8 KM)', '764.8KM').replace('VIOOLSDRIF (27811003)', 'VIOOLSDRIF')

    ncout = nc.Dataset('netcdf/' + str(ds_grdc_number) + '_' +ds_river.replace(" ", "-").lower() + '_' + ds_station_name_netcdf.replace(" ", "-").lower() + '.nc', 'w',format='NETCDF4_CLASSIC')
    ncout.createDimension('time', n_timesteps)
    ncout.createDimension('lon', 1)
    ncout.createDimension('lat', 1)

    time = ncout.createVariable('time',np.dtype('float32').char,('time'))
    lat = ncout.createVariable('lat',np.dtype('float32').char,('lat'))
    lon = ncout.createVariable('lon',np.dtype('float32').char,('lon'))
    var = ncout.createVariable('dis',np.dtype('float32').char,('time','lat','lon'), zlib=True, complevel=5, fill_value=1e+20)
    flag = ncout.createVariable('flag',np.dtype('float32').char,('time','lat','lon'), zlib=True, complevel=5, fill_value=1e+20)

    time.standard_name = 'time'
    time.long_name = 'Time'
    time.axis = 'T'
    time.calendar = 'standard'
    time.units = 'days since ' + ref_year + '-01-01 00:00:00'
    time.timezone = int(ds_timezone)
    time[:] = ds_time

    lat.long_name = 'Latitude'
    lat.standard_name = 'latitude'
    lat.units = 'degrees_north'
    lat.axis = 'Y'
    lat[:] = ds_lat

    lon.long_name = 'Longitude'
    lon.standard_name = 'longitude'
    lon.units = 'degrees_east'
    lon.axis = 'X'
    lon[:] = ds_lon

    var.standard_name = 'discharge'
    var.long_name = 'Discharge'
    var.comment = 'GRDC calculated from daily data'
    var.units = 'm3 s-1'
    var[:] = ds_discharge

    flag.long_name = 'percentage of valid values used for calculation from daily data'
    flag[:] = ds_flag

    ncout.title = 'Mean daily discharge (Q)'
    ncout.references = 'grdc.bafg.de'
    ncout.institution = 'GRDC'
    ncout.history = 'Download from GRDC Database, 29/07/2021'
    ncout.owner = ds_owner
    ncout.river = ds_river
    ncout.station = ds_station_name
    ncout.height = ds_height
    ncout.grdc_number = ds_grdc_number

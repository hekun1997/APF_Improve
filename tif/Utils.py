from TifDataSet import Dataset


def get_elevation(latitude, longitude):
    file = ''  # search file.
    tif_data_set = Dataset(file)
    site_latlng = {'lat': latitude, 'lng': longitude}
    return tif_data_set.get_elevation(site_latlng)


if __name__ =="__main__":
    tif_data_set = Dataset('..Data/ASTGTM2_N31E103/ASTGTM2_N31E103_dem.tif')
    print()

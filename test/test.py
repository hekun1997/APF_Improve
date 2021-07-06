from osgeo import gdal

if __name__ == '__main__':
    ele_dict = dict()
    dataset = gdal.Open(r'C:\D-drive-37093\PycharmWorkSpace\apf_enemy\Data\ASTGTM2_N26E100\ASTGTM2_N26E100_dem.tif')
    print(dataset)
    ele_dict[1] = dataset
    print()

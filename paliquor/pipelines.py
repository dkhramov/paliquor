import csv
import items


class PaliquorPipeline(object):
    
    def __init__(self):
        
        self.brandCategoryCsv = csv.writer(open('brandCategoryTable.csv', 'wb'))
        self.brandCategoryCsv.writerow(['brandCategoryId', 'brandCategoryName'])
        
        self.brandsCsv = csv.writer(open('brandsTable.csv', 'wb'))
        self.brandsCsv.writerow(['code', 'brandCategoryId', 'brandName', 
                                 'size', 'retailPrice'])
        self.storeStockTableCsv = csv.writer(open('storeStockTable.csv', 'wb'))
        self.storeStockTableCsv.writerow(['code', 'stateStoreNumber', 'address', 'amountInStock'])
   
            
    def process_item(self, item, spider):
        
        if isinstance(item, items.BrandCategoryItem):
            self.brandCategoryCsv.writerow([item['brandCategoryId'], item['brandCategoryName']])
            return item
                  
        if isinstance(item, items.BrandItem):
               
            try:
                item['brandCategoryId']
            except:
                item['brandCategoryId'] = "9999"
       
            try:
                item['code'][0]
            except:
                item['code'].append("")
                              
            try:
                item['brandName']
            except:
                item['brandName'].append("")
                                             
            try:
                item['size']
            except:
                item['size'].append("")
               
            try:
                item['retailPrice']
            except:
                item['retailPrice'].append("")
   
            self.brandsCsv.writerow([ item['code'], 
                                      item['brandCategoryId'], 
                                      item['brandName'], 
                                      item['size'], 
                                      item['retailPrice'] ]) 
           
            return item
           
       
        if isinstance(item, items.StockItem):
            self.storeStockTableCsv.writerow([ item['code'], 
                                               item['stateStoreNumber'], 
                                               item['address'], 
                                               item['amountInStock'] ])
            return item

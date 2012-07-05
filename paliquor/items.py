from scrapy.item import Item, Field


class BrandCategoryItem(Item):
    
    brandCategoryId = Field()
    brandCategoryName = Field()
 
    
class BrandItem(Item):
    
    code = Field()
    brandCategoryId = Field()
    brandName = Field()
    size = Field()
    retailPrice = Field()


class StockItem(Item):
    
    code = Field()
    stateStoreNumber = Field()
    address = Field()
    amountInStock = Field()
    

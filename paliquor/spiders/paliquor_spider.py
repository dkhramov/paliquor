import re
from scrapy.spider import BaseSpider
from scrapy.http import Request, FormRequest
from scrapy.selector import HtmlXPathSelector
from paliquor.items import BrandCategoryItem, BrandItem, StockItem 


class PaliquorSpider(BaseSpider):

    name = "lcb.state.pa.us"
    allowed_domains = ["www.lcbapps.lcb.state.pa.us"]
    
    def start_requests(self):
        URL = "http://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/psi_ProductDefault_inter.asp"
        brandCategoriesRequest = Request(url      = URL,
                                         callback = self.parseBrandCategories)
       
        return  [brandCategoriesRequest]


    def parseBrandCategories(self, response):
        hxs = HtmlXPathSelector(response)
        
        CategoryRows            = hxs.select('/html/body/table/tr/td/form/table/tr/td/table')
        
        SpiritCategoryNameList  = CategoryRows.select('tr/td[2]/select[@name="selTypS"]/option[position()>1]/b/text()').extract()
        SpiritCategoryValueList = CategoryRows.select('tr/td[2]/select[@name="selTypS"]/option[position()>1]/@value').extract()
        WineCategoryNameList    = CategoryRows.select('tr[2]/td/select/option[position()>1]/text()').extract()
        WineCategoryValueList   = CategoryRows.select('tr[2]/td/select/option[position()>1]/@value').extract()
        
        URL = "http://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/psi_ProductListPage_Inter.asp"
        
        for i in range( len(SpiritCategoryNameList) ):
                        
            yield FormRequest(url      = URL,
                              method   = 'GET',                         
                              formdata = {'selTypS':SpiritCategoryValueList[i],'submit':'Search'},
                              callback = self.parseBrandPages,
                              meta     = {'brandCategoryId':SpiritCategoryValueList[i],
                                          'brandCategoryName':SpiritCategoryNameList[i]})
           
            item = BrandCategoryItem()
            item['brandCategoryId']   = SpiritCategoryValueList[i]
            item['brandCategoryName'] = SpiritCategoryNameList[i]
            yield item

        for i in range( len(WineCategoryNameList) ):
            
            yield FormRequest(url      = URL,
                              method   = 'GET',                         
                              formdata = {'selTypW':WineCategoryValueList[i],'submit':'Search'},
                              callback = self.parseBrandPages,
                              meta     = {'brandCategoryId':WineCategoryValueList[i],
                                          'brandCategoryName':WineCategoryNameList[i]})
           
            item = BrandCategoryItem()
            item['brandCategoryId']   = WineCategoryValueList[i]
            item['brandCategoryName'] = WineCategoryNameList[i]
            yield item


    def parseBrandPages(self, response):

        hxs = HtmlXPathSelector(response)
        
        brandRows = hxs.select('//table/tr')

        codeList  = brandRows.select('td[1]/b/font[@size="1"]/text() | td[1]/a/b/font[@size="1"]/text()').extract()[::2]
        brandList = brandRows.select('td[1]/b/font[@size="1"]/text() | td[1]/a/b/font[@size="1"]/text()').extract()[1::2]
        sizeList  = brandRows.select('td[3]/b/font/text()').extract()
        priceList = brandRows.select('td[6]/b/font/font/text()').extract()
        
        StoreLinkList = brandRows.select('td/a[contains(@href,"psi_ProductLocation_inter.asp")]/@href').re(r'psi_ProductLocation_inter\.asp\?cdeNo=(\d+)')
        
        brandCategoryId = response.request.meta['brandCategoryId']
        
        baseURL = 'http://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/psi_ProductInventory_Inter.asp?cdeNo='
                               
        for i in range(len(codeList)):
            
            if codeList[i] in StoreLinkList:
                yield Request(url      = "".join([baseURL, codeList[i]]),
                              callback = self.parseBrandInStockPages,
                              meta     = {'code':codeList[i]})

            item = BrandItem()
            item['code']            = codeList[i]
            item['brandCategoryId'] = brandCategoryId
            item['brandName']       = brandList[i]
            item['size']            = sizeList[i]
            item['retailPrice']     = priceList[i]
            yield item
                        
        baseURL = u"http://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/"        
        nextLink = hxs.select('//table/tr/td/form/table[2]/tr/td/a[contains(text(),"Next Page")]/@href').extract()
                
        if nextLink:            
            yield Request(url      = "".join([baseURL,nextLink[0]]), 
                          callback = self.parseBrandPages,
                          meta     = {'brandCategoryId':brandCategoryId})

            
    def parseBrandInStockPages(self, response):
                     
        hxs = HtmlXPathSelector(response)
        
        stockRows = hxs.select('//table/tr')
        
        storeNumberList   = stockRows.select('td[@class="table-data"][1]/text()').extract()
        amountInStockList = stockRows.select('td[@class="table-data"][3]/text()').extract()
        addressRows       = stockRows.select('td[@class="table-data"][2]')
        
        addressList=range(len(addressRows))
        for i,address in enumerate(addressRows):
            addressList[i] = ", ".join( address.select('text()').extract() )
       
        for i in range(len(storeNumberList)):
                            
            item = StockItem()
            item['code']             = response.request.meta['code']
            item['stateStoreNumber'] = storeNumberList[i].strip()
            item['address']          = re.sub(r'\s+', ' ', addressList[i]).strip()
            item['amountInStock']    = re.sub(r'units', ' ', amountInStockList[i]).strip()
            yield item
        
        baseURL = u"http://www.lcbapps.lcb.state.pa.us"
        nextLink = hxs.select('//table/tr/td/table/tr/td/table/tr/td[4]/a/@href').extract()
                
        if nextLink:            
            yield Request(url      = "".join([baseURL,nextLink[0]]), 
                          callback = self.parseBrandInStockPages,
                          meta     = {'code':response.request.meta['code']})

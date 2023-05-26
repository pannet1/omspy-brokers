from MarketDepthRowInfo import MarketDeptRowInfo
from ApplicationMessageVersion import ApplicationMessageVersion
import struct

class MarketDepthEvent():
    def deserialize(reader,count):
        count+= 2
        messageVersion = reader.read_uint16()
        applicationType = reader.read_uint16()
        tokenID = reader.read_uint64()

        count += 8
        if (messageVersion >= ApplicationMessageVersion.Version_1_0_1_2983.value): 
            sequenceNumber =reader.read_uint64()
            count += 8
            SkipBytes = reader.read_int32()
            count += 4

        exchangeSegment = int(reader.read_int16())
        count+= 2

        exchangeInstrumentId = reader.read_int32()
        count+= 4

        exchangeTimestamp = reader.read_uint64()
        count+= 8
        bidCount = reader.read_int32()
        count += 4
       
        for x in range(0,bidCount):
            md= MarketDeptRowInfo(reader,count)
            count = md.deserialize()
        askCount = reader.read_int32()
        count += 4
        for x in range(0,askCount):
            md= MarketDeptRowInfo(reader,count)
            count = md.deserialize()
        

        md= MarketDeptRowInfo(reader,count)
        count = md.deserialize()
        

        md1= MarketDeptRowInfo(reader,count)
        count = md1.deserialize()
      
        lut = reader.read_uint64()
        count += 8

        LTP = struct.unpack('d', reader.read_bytes(8))[0]
        count += 8

        ltq = reader.read_int32()
        count += 4

        totalBuyQuantity = reader.read_uint32()
        count += 4

        totalSellQuantity = reader.read_uint32()
        count += 4

        totalTradedQuantity = reader.read_uint32()
        count += 4
        averageTradedPrice = struct.unpack('d', reader.read_bytes(8))[0]

        count += 8

        lastTradedTime = reader.read_int64()
        count += 8

        percentChange = reader.read_uint64()
        count += 8

        open =  struct.unpack('d', reader.read_bytes(8))[0]
        count += 8
        
        high = struct.unpack('d', reader.read_bytes(8))[0]
        count += 8
        
        low = struct.unpack('d', reader.read_bytes(8))[0]
        count += 8
        
        close = struct.unpack('d', reader.read_bytes(8))[0]
        count += 8

        totalvaluetraded =  struct.unpack('d', reader.read_bytes(8))[0]
        count += 8
        bbtotalbuy = reader.read_int16()
        count += 2

        bbtotalsell = reader.read_int16()
        count += 2

        Booktype = reader.read_int16()
        count += 2

        MarketType = reader.read_int16()
       
        print("MARKETDEPTH ::::exchangeSegment :",exchangeSegment,"exchangeInstrumentId:",
        exchangeInstrumentId,"exchangeTimestamp:",exchangeTimestamp,"lut:",lut,"LTP:",LTP, "ltq:",
        ltq,"totalBuyQuantity:",totalBuyQuantity,"totalSellQuantity:",totalSellQuantity,
        "totalTradedQuantity:",totalTradedQuantity,
        "averageTradedPrice:",averageTradedPrice,"lastTradedTime:",lastTradedTime,"percentChange:",percentChange,
        "open:",open ,"high:",high,"low:",low ,"close:",close, "totalvaluetraded:",totalvaluetraded ,
        "bbtotalbuy:" ,bbtotalbuy ,"bbtotalsell:",bbtotalsell,"Booktype:",Booktype,"MarketType:",MarketType )



  
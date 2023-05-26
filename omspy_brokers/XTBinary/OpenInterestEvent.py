from ApplicationMessageVersion import ApplicationMessageVersion

class OpenInterest():
    def deserialize(reader,count):
        count+= 2
        messageVersion = reader.read_uint16()
        applicationType = reader.read_uint16()
        tokenID = reader.read_uint64()

        count += 8
        if (messageVersion >= ApplicationMessageVersion.Version_1_0_1_2983.value): 
            sequenceNumber =reader.read_uint64()
            print("sequenceNumber==" ,sequenceNumber )

            count += 8
            SkipBytes = reader.read_int32()
            count += 4
        
        exchangeSegment = int(reader.read_int16())
        count+= 2

        exchangeInstrumentId = reader.read_int32()
        count+= 4

        exchangeTimestamp = reader.read_uint64()
        count+= 8

        MarketType = reader.read_int16()
        count += 2

        
        openInterest = (reader.read_int32())
        count += 4

        underlyingExchangeSegment = reader.read_int16()
        count += 2

        underlyingInstrumentID = reader.read_uint64()
        count += 8

        isStringExits =reader.read_int8()
        count += 1

        if (isStringExits == 1) :
            stringLength = reader.read_int8()
            count += 1
            count += stringLength
        

        underlyingTotalOpenInterest =reader.read_int32()
        count += 4
 
        print("OpenInterestI ::::exchangeSegment :",exchangeSegment,"exchangeInstrumentId:",
        exchangeInstrumentId,"exchangeTimestamp:",exchangeTimestamp,"openInterest:",openInterest,
         "underlyingExchangeSegment:" ,underlyingExchangeSegment, 
         "underlyingInstrumentID:" ,underlyingInstrumentID , "isStringExits: ",isStringExits, "underlyingTotalOpenInterest:",underlyingTotalOpenInterest)


#! python
# (c) DL, UTA, 2009 - 2011
import  sys, string, time
import math
wordsize = 24                                        # everything is a word
numregbits = 3                                       # actually +1, msb is indirect bit
opcodesize = 5
addrsize = wordsize - (opcodesize+numregbits+1)      # num bits in address
memloadsize = 1024                                   # change this for larger programs
numregs = 2**numregbits
regmask = (numregs*2)-1                              # including indirect bit
addmask = (2**(wordsize - addrsize)) -1
nummask = (2**(wordsize))-1
opcposition = wordsize - (opcodesize + 1)            # shift value to position opcode
reg1position = opcposition - (numregbits +1)            # first register position
reg2position = reg1position - (numregbits +1)
memaddrimmedposition = reg2position                  # mem address or immediate same place as reg2
realmemsize = memloadsize * 1                        # this is memory size, should be (much) bigger than a program
#memory management regs
codeseg = numregs - 1                                # last reg is a code segment pointer
dataseg = numregs - 2                                # next to last reg is a data segment pointer
#ints and traps
trapreglink = numregs - 3                            # store return value here
trapval     = numregs - 4                            # pass which trap/int
mem = [0] * realmemsize                              # this is memory, init to 0 
reg = [0] * numregs                                  # registers
clock = 1                                            # clock starts ticking
ic = 0                                               # instruction count
numcoderefs = 0                                      # number of times instructions read
numdatarefs = 0                                      # number of times data read
starttime = time.time()
curtime = starttime
def startexechere ( p ):
    # start execution at this address
    reg[ codeseg ] = p    
def loadmem():                                       # get binary load image
  curaddr = 0
  for line in open("a.out", 'r').readlines():
    token = string.split( string.lower( line ))      # first token on each line is mem word, ignore rest
    if ( token[ 0 ] == 'go' ):
        startexechere(  int( token[ 1 ] ) )
    else:    
        mem[ curaddr ] = int( token[ 0 ], 0 )                
        curaddr = curaddr = curaddr + 1


def getcodemem ( a ):
    global numcoderefs
    #print("in getcode mem")
    #print("a=",a)
    # get code memory at this address
    memval = mem[ a + reg[ codeseg ] ]
    #dval = a + reg[ codeseg ]
    #memval = getcache( dval)
    #print("memval",memval)
    #x = raw_input()
    numcoderefs = numcoderefs + 1
    return ( memval )

def getdatamem2 ( a ):
    # get code memory at this address
    #print("in getdata mem2")
    #print("a=",a)

    memval2 = mem[ a + reg[ dataseg ] ]
    #print("memval2",memval2)
    #x = raw_input()
    return ( memval2 )

def getdatamem ( a ):
    global seperatem
    # get code memory at this address
    #print("in getdata mem")
    #print("a=",a)

    #memval = mem[ a + reg[ dataseg ] ]
    dval = a + reg[ dataseg ]
    if seperatem == 1:
        memval = dgetcache( dval, 'd')
    else:
        memval = igetcache( dval, 'd')
    #print("memval",memval)
    #x = raw_input()
    return ( memval )
def getregval ( r ):
    # get reg or indirect value
    if ( (r & (1<<numregbits)) == 0 ):               # not indirect
       rval = reg[ r ] 
    else:
       rval = getdatamem( reg[ r - numregs ] )       # indirect data with mem address
       #mychange : incrementing data refs in case of indirect
       print("in indirect getregval")
       print("rval",rval)
       x = raw_input()
       #dval = reg[ r - numregs ]
       #print("dval=",dval)
       #rval = getcache( dval,'d')
       #print("rval",rval)
       #x = raw_input()
       global numdatarefs
       numdatarefs = numdatarefs + 1
       #end mychange
    return ( rval )

def igetcache(val,type) :
        global chit
        global cmiss
        global cir1
        global nlinesbits
        global nwordsbits

        #global indexdec
        #global worddec
        #print("in igetcache block")
        #print("val=",val)
        #print("type",type)
        """
        ipbin = '{:010b}'.format(val)
        tag = ipbin[0:7]
        indext = ipbin[7:]
        index = indext[:2]
        word = ipbin[9:]
        indexdec = int(index,2)
        worddec = int(word,2)
         """

        ipbin = '{:010b}'.format(val)

        ntagbits = 10 - nlinesbits
        ntagbits = ntagbits - nwordsbits
        print("ntagbits",ntagbits)
        print("ntagbits",nlinesbits)
        print("ntagbits",nwordsbits)
        tag = ipbin[0:ntagbits]
        indext = ipbin[ntagbits:]
        index = indext[:nlinesbits]
        wordstartb = 10 - nwordsbits
        word = ipbin[wordstartb:]
        indexdec = int(index,2)
        worddec = int(word,2)

        print("ntagbits",ntagbits)
        print("wordstartb",wordstartb)
        print("ipbin=",ipbin)
        print("tag=",tag)
        print("index=",index)
        print("word=",word)
        print("indexdec",indexdec)
        print("worddec",worddec)

        valdec = val
        startval = valdec - worddec
        worddec2 = 0
        loopc = nwords
        print("valdec",valdec)
        print("startval",startval)
        print("loopc",loopc)
        x= raw_input()
        if(icache[indexdec][worddec] != 0): #if there is entry in cache chk tag
            #print("frst if")
            if(ictags[indexdec] == tag): #if tag matchesmens its present in cache
                #print("scnd if")
                cir = icache[indexdec][worddec]
                chit = chit + 1
                #return(cir)
            else: #if its not present in cache, load from mem and update cache
                #print("frst else")
                #if type == 'i':
                cir = getcodemem( val )
                #else :
                #    cir = getdatamem2( val )
                icache[indexdec][worddec] = cir
                ictags[indexdec] = tag
                #fetch next word too only if its frst word in cahce need to think whetehr its correct?

                for x in range(0, loopc):
                    cir2 = getcodemem(startval)
                    icache[indexdec][worddec2] = cir2
                    startval = startval + 1
                    worddec2 = worddec2 + 1
                    print("in loop cir2",cir2)
                    x=raw_input()
                    #x = x + 1
                """
                if worddec == 0:
                    val1= val + 1
                    ipbin = '{:010b}'.format(val1)

                    #tag = ipbin[0:7]
                    #indext = ipbin[7:]
                    #index = indext[:2]
                    #word = ipbin[9:]
                    #indexdec = int(index,2)
                    #worddec = int(word,2)

                    ntagbits = 10 - nlinesbits
                    ntagbits = ntagbits - nwordsbits
                    print("ntagbits",ntagbits)
                    print("ntagbits",nlinesbits)
                    print("ntagbits",nwordsbits)
                    tag = ipbin[0:ntagbits]
                    indext = ipbin[ntagbits:]
                    index = indext[:nlinesbits]
                    wordstartb = 10 - nwordsbits
                    word = ipbin[wordstartb:]
                    indexdec = int(index,2)
                    worddec = int(word,2)
                    #print("ipbin=",ipbin)
                    #print("tag=",tag)
                    #print("index=",index)
                    #print("word=",word)
                    #print("indexdec",indexdec)
                    #print("worddec",worddec)
                    #if type == 'i':
                    cir1 = getcodemem( val1 )
                    #else :
                    #    cir1 = getdatamem2( val1 )
                #cir1 = getcodemem( val1 )
                    icache[indexdec][worddec] = cir1
                    ictags[indexdec] = tag
                """
                cmiss = cmiss + 1
                #return(cir)

        else:
            #print("scnd else")
            #if type == 'i':
            cir = getcodemem( val )
            #else :
            #    cir = getdatamem2( val )
            #cir = getcodemem( val )
            icache[indexdec][worddec] = cir
            ictags[indexdec] = tag
             #fetch next word too  only if its frst word in cache need to think whetehr its correct?
            for x in range(0, loopc):
                    cir2 = getcodemem(startval)
                    icache[indexdec][worddec2] = cir2
                    startval = startval + 1
                    worddec2 = worddec2 + 1
                    print("in loop cir2",cir2)
                    x=raw_input()
            """
            if worddec == 0:
                val1= val + 1
                ipbin = '{:010b}'.format(val1)

                #tag = ipbin[0:7]
                #indext = ipbin[7:]
                #index = indext[:2]
                #word = ipbin[9:]
                #indexdec = int(index,2)
                #worddec = int(word,2)

                ntagbits = 10 - nlinesbits
                ntagbits = ntagbits - nwordsbits
                print("ntagbits",ntagbits)
                print("ntagbits",nlinesbits)
                print("ntagbits",nwordsbits)
                tag = ipbin[0:ntagbits]
                indext = ipbin[ntagbits:]
                index = indext[:nlinesbits]
                wordstartb = 10 - nwordsbits
                word = ipbin[wordstartb:]
                indexdec = int(index,2)
                worddec = int(word,2)
                #print("ipbin=",ipbin)
                #print("tag=",tag)
                #print("index=",index)
                #print("word=",word)
                #print("indexdec",indexdec)
                #print("worddec",worddec)
                #if type == 'i':
                cir1 = getcodemem( val1 )
                #else :
                #    cir1 = getdatamem2( val1 )
                #cir1 = getcodemem( val1 )
                icache[indexdec][worddec] = cir1
                ictags[indexdec] = tag
            """
            cmiss = cmiss + 1
            #return(cir)

        #print("cache[indexdec][worddec]",cache[indexdec][worddec])
        #print("ctags[indexdec]",ctags[indexdec])
        #print icache
        #print ictags
        ##print dcache
        #print dctags
        #print("cir=",cir)
        #print("cir1=",cir1)
        #print("chit",chit)
        #print("cmiss",cmiss)
        #x = raw_input()
        return(cir)


def dgetcache(val,type) :
        global chit
        global cmiss
        global cir1
        global nlinesbits
        global nwordsbits
        #global indexdec
        #global worddec
        #print("in dgetcache block")
        #print("val=",val)
        #print("type",type)
        """
        ipbin = '{:010b}'.format(val)
        tag = ipbin[0:7]
        indext = ipbin[7:]
        index = indext[:2]
        word = ipbin[9:]
        indexdec = int(index,2)
        worddec = int(word,2)
        """
        ipbin = '{:010b}'.format(val)

        ntagbits = 10 - nlinesbits
        ntagbits = ntagbits - nwordsbits
        print("ntagbits",ntagbits)
        print("ntagbits",nlinesbits)
        print("ntagbits",nwordsbits)
        tag = ipbin[0:ntagbits]
        indext = ipbin[ntagbits:]
        index = indext[:nlinesbits]
        wordstartb = 10 - nwordsbits
        word = ipbin[wordstartb:]
        indexdec = int(index,2)
        worddec = int(word,2)

        print("ntagbits",ntagbits)
        print("wordstartb",wordstartb)
        print("ipbin=",ipbin)
        print("tag=",tag)
        print("index=",index)
        print("word=",word)
        print("indexdec",indexdec)
        print("worddec",worddec)

        valdec = val
        startval = valdec - worddec
        worddec2 = 0
        loopc = nwords
        print("valdec",valdec)
        print("startval",startval)
        print("loopc",loopc)

        x= raw_input()
        #print("ipbin=",ipbin)
        #print("tag=",tag)
        #print("index=",index)
        #print("word=",word)
        #print("indexdec",indexdec)
        #print("worddec",worddec)
        if(dcache[indexdec][worddec] != 0): #if there is entry in cache chk tag
            #print("frst if")
            if(dctags[indexdec] == tag): #if tag matchesmens its present in cache
                #print("scnd if")
                cir = dcache[indexdec][worddec]
                chit = chit + 1
                #return(cir)
            else: #if its not present in cache, load from mem and update cache
                #print("frst else")
                #if type == 'i':
                cir = getcodemem( val )
                #else :
                #    cir = getdatamem2( val )
                dcache[indexdec][worddec] = cir
                dctags[indexdec] = tag
                #fetch next word too only if its frst word in cahce need to think whetehr its correct?

                for x in range(0, loopc):
                    cir2 = getcodemem(startval)
                    dcache[indexdec][worddec2] = cir2
                    startval = startval + 1
                    worddec2 = worddec2 + 1
                    print("in data loop cir2",cir2)
                    x=raw_input()


                """
                if worddec == 0:
                    val1= val + 1
                    ipbin = '{:010b}'.format(val1)

                    #tag = ipbin[0:7]
                    #indext = ipbin[7:]
                    #index = indext[:2]
                    #word = ipbin[9:]
                    #indexdec = int(index,2)
                    #worddec = int(word,2)

                    ntagbits = 10 - nlinesbits
                    ntagbits = ntagbits - nwordsbits
                    print("ntagbits",ntagbits)
                    print("ntagbits",nlinesbits)
                    print("ntagbits",nwordsbits)
                    tag = ipbin[0:ntagbits]
                    indext = ipbin[ntagbits:]
                    index = indext[:nlinesbits]
                    wordstartb = 10 - nwordsbits
                    word = ipbin[wordstartb:]
                    indexdec = int(index,2)
                    worddec = int(word,2)
                    #print("ipbin=",ipbin)
                    #print("tag=",tag)
                    #print("index=",index)
                    #print("word=",word)
                    #print("indexdec",indexdec)
                    #print("worddec",worddec)
                    #if type == 'i':
                    cir1 = getcodemem( val1 )
                    #else :
                    #    cir1 = getdatamem2( val1 )
                #cir1 = getcodemem( val1 )
                    dcache[indexdec][worddec] = cir1
                    dctags[indexdec] = tag
                """
                cmiss = cmiss + 1
                #return(cir)

        else:
            #print("scnd else")
            #if type == 'i':
            cir = getcodemem( val )
            #else :
            #    cir = getdatamem2( val )
            #cir = getcodemem( val )
            dcache[indexdec][worddec] = cir
            dctags[indexdec] = tag
             #fetch next word too  only if its frst word in cache need to think whetehr its correct?

            for x in range(0, loopc):
                    cir2 = getcodemem(startval)
                    dcache[indexdec][worddec2] = cir2
                    startval = startval + 1
                    worddec2 = worddec2 + 1
                    print("in data loop cir2",cir2)
                    x=raw_input()
            """
            if worddec == 0:
                val1= val + 1
                ipbin = '{:010b}'.format(val1)

                #tag = ipbin[0:7]
                #indext = ipbin[7:]
                #index = indext[:2]
                #word = ipbin[9:]
                #indexdec = int(index,2)
                #worddec = int(word,2)

                ntagbits = 10 - nlinesbits
                ntagbits = ntagbits - nwordsbits
                print("ntagbits",ntagbits)
                print("ntagbits",nlinesbits)
                print("ntagbits",nwordsbits)
                tag = ipbin[0:ntagbits]
                indext = ipbin[ntagbits:]
                index = indext[:nlinesbits]
                wordstartb = 10 - nwordsbits
                word = ipbin[wordstartb:]
                indexdec = int(index,2)
                worddec = int(word,2)
                #print("ipbin=",ipbin)
                #print("tag=",tag)
                #print("index=",index)
                #print("word=",word)
                #print("indexdec",indexdec)
                #print("worddec",worddec)
                #if type == 'i':
                cir1 = getcodemem( val1 )
                #else :
                #    cir1 = getdatamem2( val1 )
                #cir1 = getcodemem( val1 )
                dcache[indexdec][worddec] = cir1
                dctags[indexdec] = tag
            """
            cmiss = cmiss + 1
            #return(cir)

        #print("cache[indexdec][worddec]",cache[indexdec][worddec])
        #print("ctags[indexdec]",ctags[indexdec])
        #print icache
        #print ictags
        #print dcache
        #print dctags
        #print("cir=",cir)
        #print("cir1=",cir1)
        #print("chit",chit)
        #print("cmiss",cmiss)
        #x = raw_input()
        return(cir)

def checkres( v1, v2, res):
    v1sign = ( v1 >> (wordsize - 1) ) & 1
    v2sign = ( v2 >> (wordsize - 1) ) & 1
    ressign = ( res >> (wordsize - 1) ) & 1
    if ( ( v1sign ) & ( v2sign ) & ( not ressign ) ):
      return ( 1 )
    elif ( ( not v1sign ) & ( not v2sign ) & ( ressign ) ):
      return ( 1 )
    else:
      return( 0 )
def dumpstate ( d ):
    if ( d == 1 ):
        print reg
    elif ( d == 2 ):
        print mem
    elif ( d == 3 ):
        print 'clock=', clock, 'IC=', ic, 'Coderefs=', numcoderefs,'Datarefs=', numdatarefs, 'Start Time=', starttime, 'Currently=', time.time() 
def trap ( t ):
    # unusual cases
    # trap 0 illegal instruction
    # trap 1 arithmetic overflow
    # trap 2 sys call
    # trap 3+ user
    rl = trapreglink                            # store return value here
    rv = trapval
    if ( ( t == 0 ) | ( t == 1 ) ):
       dumpstate( 1 )
       dumpstate( 2 )
       dumpstate( 3 )
    elif ( t == 2 ):                          # sys call, reg trapval has a parameter
       what = reg[ trapval ] 
       if ( what == 1 ):
           a = a        #elapsed time
    return ( -1, -1 )
    return ( rv, rl )
def loadbenchmark():
    global benchmark
    for i in range(0,19):
        for j in range(0,7):
            benchmark[i][j]= 0
            
    print("here is initialized benchmark")
    for i in range(0,19):
        for j in range(0,7):
            item = benchmark[i][j]
            print(" ", item )
            
def ife():
    global ip
    global ir
    global numcoderefs
    global ic
    global totopr
    global stalls
    global flag
    global dflag
    global bflag
    global ip2
    global flag9
    global flag11
    global chit
    global cmiss
    global ir1
   
    
    if((stalls > 0) & (flag == 1)) :
        #print("i m in if part of if")
        stalls = stalls - 1
        if stalls == 0 :
            flag = 0
            dflag = 0
    else :
        #print("i m in else part of if")
        #changes for bp
        #if(bflag == 1):
        #if( ( (bflag == 0) & (bflagw == 1) ) | ( (bflag == 1) & (bflagw == 1) ) ):
        if( (bflag == 1) & (flag9== 0)):
        #if( bflag == 1):
            if flag11 == 0:
                ip2 = ip
                #print("here is ip2",ip2)
                #x = raw_input()
                flag11 = 1
            
            #ip = ja[ip]
            #print("ja[ipb]",ja[ipb])
            ip = ja[ipb]    
            #print("ipb=",ipb)
            flag9 = 1
            #print("enter some")
            #print("ip=",ip)
            #print("ip2",ip2)
            #x = raw_input()
            #print("brnch taken ", ja[ip])

        #print("In Ife")
        #print("ip=",ip)
        #ir = getcodemem( ip )                            # - fetch

        #ip = 12

        ir = igetcache( ip, 'i' )

        #print("ir in ife=",ir)
        #x = raw_input()
        #changes for cache

        #print("cache[indexdec][worddec]",cache[indexdec][worddec])
        #print("ctags[indexdec]",ctags[indexdec])

        print("in ife again")
        print icache
        #print ictags
        print dcache
        #print dctags
        print("ir=",ir)
        print("ir1=",ir1)
        print("chit",chit)
        print("cmiss",cmiss)
        #x = raw_input()

        #mychange:adding 1 to code ref
        #numcoderefs = numcoderefs + 1
        #end of mychange
        ip = ip + 1
        ic = ic + 1
        #print("pstage    : ", pstage)
        print("ifetch    :" , "ic=",ic, "ip=",ip )
        totopr[ic] = totopr[ic] + 1
        if stalls > 0 :
            flag = 1
    return(0)
def ide() :
    global ir
    global ic
    global opcode2
    global opcode3
    global reg13
    global addr2
    global addr3
    global reg2
    global str2
    global list2
    global list3
    global benchmark
    global totalstalls
    global totstalls
    global totopr
    global stalls
    global is2
    global is21
    global is22
    global dflag
    global reg23
    global bhazards
    global dhazards
    global icbw
    global ipb
    global flags
    global brch
    global bflag
    global flag9
    #icbw = -2
    #if(stalls == 0) :
     #ics2 = ic - 1    
    if((stalls == 0) & (ic > (icbw + 2))) :
        #print("i m in if part of ide")
        opcode2 = ir >> opcposition
        opcode3 = opcode2
        # - decode
        reg12   = (ir >> reg1position) & regmask
        reg13 = reg12
        reg2   = (ir >> reg2position) & regmask
        reg23 = reg2
        addr2   = (ir) & addmask
       
            
        addr3 = addr2
        ic2 = ic
        icchk1 = ic2 - 1
        icchk2 = ic2 - 2
        #changes for benchmarking
        stalls1 = 0
        stalls2 = 0
        stalls3 = 0
        stalls = 0
        #print("reg12",reg12)
        #print("addr2=",addr2)
        if(opcode2 in list2 ):
            benchmark[ic2][reg12] = 1
        #if((opcode2 in list3) & (addr2 == 0)):
        if(opcode2 in list3):
            #print("inside list3 loop")
            #print("reg2=",reg2)
            benchmark[ic2][reg12] = 1
            if(reg2 < 6):
                if(benchmark[icchk2][reg2] == 1):
                    stalls2 = 1
                if(benchmark[icchk1][reg2] == 1):
                    stalls2 = 2    
            #else:
            #    addr2 = reg2
            #    addr3 = addr2
        if(benchmark[icchk2][reg12] == 1):
                stalls1 = 1
        if(benchmark[icchk1][reg12] == 1):
                stalls1 = 2
        if(opcode2 == 12):
              #changes for branch predictor  
                #stalls3 = 4
                #dflag = 1
                bhazards = bhazards + 1
                brch = brch + 1
                #print("ic2=",ic2)
                #x = raw_input()
                #print("ipb in ide=",ipb)
                #print("ic2",ic2)
                #print("pstage=",pstage)
                #print("bp[ipb] ", bp[ipb] )
                flag9 = 0
                
                
                
                #if flags == 0 :
                #if(bp[ic2] == 1):
                if(bp[ipb] == 1):
                    bflag = 1
                    
                    #print("flags became 1")
                #if(bp[ic2] == 0):
                if(bp[ipb] == 0):    
                    bflag = 0
                 
                    #print("flags became 1")
                #print("bflags=",bflag)
                #x = raw_input()
                #else:
                 #   if(bp[ipb] == 1):
                 #       bflag = 1                        
                 #   if(bp[ipb] == 0):
                 #       bflag = 0
                #print("bflags",bflag)       
                #x = raw_input()   
        if((stalls1 > 0) | (stalls2 > 0)):
            dhazards = dhazards + 1
            
        stalls = max(stalls1,stalls2,stalls3)
        #print("stalls in ide",stalls)
        if(stalls > 0):
            #sic = ic2 - 1
            is2 = ic2
            is21 = is2 - 1
            is22 = is2 - 2
            #print("ic2-1",is21)
            #print("ic2-2",is22)
            totstalls[ic2] = stalls
        
        totalstalls = totalstalls + stalls
        #print("stalls1=",stalls1)
        #print("stalls2=",stalls2)
        #print("stalls =",stalls)
        #assuming it will decrement in if anyways
        #if(stalls > 0):
        #    stalls = stalls + 1
        #end of assumption 
        str2 = ""
        sic = str(ic)
        sopcode2 = str(opcode2)
        sreg12 = str(reg12)
        sreg2 = str(reg2)
        #saddr2 = str(addr2)
        str2 += "Instruction = "
        str2 += sic
        str2 += " opcode= "
        str2 += sopcode2
        str2 += " reg1= "
        str2 += sreg12
        str2 += " reg2= "
        str2 += sreg2
        #print("pstage    : ", pstage)
        print("idecode   :" , "ic=",ic2)
        totopr[ic2] = totopr[ic2] + 1
    return(0)

def of() :
   global opcode3
   global opcode4
   global reg14
   global addr3
   global operand23
   global operand24
   global memdata
   global operand1
   global reg2
   global regdata
   global str2
   global numdatarefs
   global totopr
   global stalls
   global dflag
   global ics3
   global icbw
   
   ics3 = ic - 1
   #print("ics3",ics3)
   #print("totopr[ics3]",totopr[ics3])
   #if( (((dflag == 0) & (stalls == 0)) | ((dflag == 1) & (stalls == 2))) &(totopr[ics3] < 3) ) :
   if ( ((dflag == 0) & (stalls == 0)) & (ics3 > (icbw + 2))):
        
      #if (ics3 > icbw + 2) :
       #print("i m in if part of of")
       opcode4 = opcode3 
       if not (opcodes.has_key( opcode3 )):
          tval, treg = trap(0) 
          if (tval == -1):                              # illegal instruction
             return(tval) 
             #break
       memdata = 0                                      #     contents of memory for loads
       reg14 = reg13
       if opcodes[ opcode3 ] [0] == 1:                   #     dec, inc, ret type
          operand1 = getregval( reg13 )                  #       fetch operands
      
       elif opcodes[ opcode3 ] [0] == 2:                 #     add, sub type
          operand1 = getregval( reg13 )                  #       fetch operands
          #if(reg23 < 6):
          operand23 = getregval( reg23 )
          #else:
          #    operand23 = getdatamem( reg23 )
              #print("after all complication=",operand23)
          operand24 = operand23
       elif opcodes[ opcode3 ] [0] == 3:                 #     ld, st, br type
          #print("here")
          #x = raw_input()
          operand1 = getregval( reg13 )                  #     fetch operands
          operand23 = addr3
          operand24 = operand23      
       elif opcodes[ opcode3 ] [0] == 0:                 #     ? type
          return(tval) 
          #break
       if (opcode3 == 7):                                # get data memory for loads
          memdata = getdatamem( operand23 )
          #mychange : incrementing data refs in case of indirect
          numdatarefs = numdatarefs + 1
          #end mychange
          #mychane : for store 
       if (opcode3 == 8):                                # save reg content for store
          regdata = operand1 
          #mychange : incrementing data refs in case of indirect
          numdatarefs = numdatarefs + 1
          #end mychange
          #end of mychane : for store
       saddr3 = str(addr3)
       soperand1 = str(operand1)
       soperand23 = str(operand23)
       str2 += " addr= "
       if opcodes[ opcode3 ] [0] == 3:
            str2 += saddr3
       str2 += " operand1= "
       str2 += soperand1    
       str2 += " operand2= "
       str2 += soperand23
       print("trace",str2)
       ic3 = ic - 1
       #print("pstage    : ", pstage)
       print("opcode fet:", "ic=",ic3)
       totopr[ic3] = totopr[ic3] + 1
   return(0)
def ex() :
   # execute
   global opcode4
   global opcode5
   global operand24
   global operand25
   global operand1
   global ip
   global reg15
   global reg14
   global result
   global regdata
   global ic
   global numcoderefs
   global totopr
   global stalls
   global dflag
   global ics4
   global icbw
   global ipb
   global wrong
   global bflag
   global ip2
   global flag10
   
   if(dflag==0):
       ics4 = ic - 2
   elif((dflag == 1) & (stalls == 4) ):
       ics4 = ic - 2
   elif((dflag == 1) & (stalls == 1) ):
       ics4 = ic - 1    
   #print("ics4 in ex=",ics4)
   #if (totopr[ics4] < 4):
   if ( (totopr[ics4] < 4) & (ics4 > (icbw + 2)) ):  
        
       #print("i m in if part of ex")
       print(totopr[opcode4])
       reg15 = reg14
       opcode5 = opcode4
       operand25 = operand24
       if opcode4 == 1:                     # add
          result = (operand1 + operand24) & nummask
          if ( checkres( operand1, operand24, result )):
             tval, treg = trap(1)
             #decrement ic because next inst have decoded by this time
             ic = ic - 1
             if (tval == -1):                           # overflow
                #break
                return(tval) 
       elif opcode4 == 2:                   # sub
          result = (operand1 - operand24) & nummask
          if ( checkres( operand1, operand24, result )):
             tval, treg = trap(1)
             #decrement ic because next inst have decoded by this time
             ic = ic - 1
             if (tval == -1):                           # overflow
                #break
                return(tval) 
       elif opcode4 == 3:                   # dec
          result = operand1 - 1
       elif opcode4 == 4:                   # inc
          result = operand1 + 1
       elif opcode4 == 7:                   # load
          result = memdata
       #mychange   
       elif opcode4 == 8:                   # store
          result = regdata
       #end of mychange   
       elif opcode4 == 9:                   # load immediate
          result = operand24
       elif opcode4 == 12:                  # conditional branch
          result = operand1
          if result <> 0:
             #ip = operand24

             #bp[ics4] = 1
              
             #ja[ics4] = ip
             
             #ipb = ip
             if flag10 == 0:
                 ipb = ics4
                 ip = operand24
                 ja[ipb]= ip
                 flag10 = 1
             
             bp[ipb] = 1
             #print("in if part of res <> 0",ip)
             #print("ics4",ics4)
             #print("bp[ics4]",bp[ics4])
             #print("ipb",ipb)
             #print("bp[ipb]",bp[ipb])
             #x = raw_input()
             if bflag == 0:
                 #
                 #ip = operand24
                 #print("wrong")
                 bflagw = 1
                 icbw = ics4
                 #print("icbw",icbw)
                 wrong = wrong + 1;
                 ip = operand24
                 #ja[ipb]= ip
             else:
                 bflagw = 0
                 icbw = -2
             # bflag = 1
             #ja[ics4] = ip
             
             #print("new correction in ex")
             #x = raw_input()
             #print("ip=",ip)
             #print("ipb",ipb)
             #print("ics4",ics4)
             #x = raw_input()
          else:
              #print("in else of res <> 0",ip)
              #x = raw_input()
              #bp[ics4] = 0
              bp[ipb] = 0
              if bflag == 1:
                 bflagw = 1
                 icbw = ics4
                 wrong = wrong + 1;
                 #
                 #bflag = 0
                 ip = ip2
                 #print("ip2",ip2)
                 #x = raw_input()
                 
              else:
                  bflagw = 0
                  icbw = -2
              #bflag = 0 
       elif opcode4 == 13:                  # branch and link
          result = ip
          ip = operand24
       elif opcode4 == 14:                   # return
          ip = operand1
       elif opcode4 == 16:                   # interrupt/sys call
          result = ip
          #decrement ic and numcoderefs because next inst have decoded by this time
          ic = ic - 1
          numcoderefs = numcoderefs - 1
          tval, treg = trap(reg14)
          if (tval == -1):
            #break
               
            return(tval)  
          reg1 = treg
          ip = operand24
       #ic4 = ic - 2
       #print("pstage    : ", pstage)
       print("execute   :" , "ic=",ics4)
       totopr[ics4] = totopr[ics4] + 1
   return(0)

   
def wb() :
     # write back
   global opcode5
   global operand25
   global result
   global totopr
   global stalls
   global ics5
   global flag1
   global flag2
   global dflag
   global icbw
   #print("in wb stalls=",stalls)
   #print("ic=",ic)
   #print("dflag",dflag)
   #print("stalls",stalls)
   if ( (dflag == 0) & (stalls == 2)):
       #print("in 1 if")
       ics5 = ic - 3
       flag1 = 1
   elif ((dflag == 0) & (stalls == 1)):
       #print("in 2 if")
       ics5 = ic - 3
       #print("ics5",ics5)
       if (flag1 == 1):
           ics5 = ic - 2
           flag1 = 0
       else :
           flag2 = 1
   elif((dflag == 1) & (stalls == 4)):
       #print("in 3 if")
       ics5 = ic - 3
   elif((dflag == 1) & (stalls == 3)):
       #print("in 4 if")
       ics5 = ic - 2
       
   if stalls == 0:
       #print("in 5 if")
       ics5 = ic - 3
       if (flag2 == 1):
           ics5 = ic - 2
           flag2 = 0
   
   #print("ics5=",ics5)
   #print("opcode5",opcode5)        
   #print("totopr[ics5]",totopr[ics5])
   #if (totopr[ics5] < 5):
   #if ( ( (totopr[ics5] < 5) & (ics5 != (icbw + 1) )) | ( (totopr[ics5] < 5) & (ics5 != (icbw + 1) ) ) ):
   if ( ( (totopr[ics5] < 5) & (ics5 == icbw)) |  ( (totopr[ics5] < 5) & (ics5 > (icbw + 2))) ):
       #print("i m in if part of wb")
       #print(totopr[opcode5])
       if ( (opcode5 == 1) | (opcode5 == 2 ) | 
             (opcode5 == 3) | (opcode5 == 4 ) ):     # arithmetic
            reg[ reg15 ] = result
            #print("reg15=",reg15,opcode5,"result=",result)
        
       elif ( (opcode5 == 7) | (opcode5 == 9 )):     # loads
            reg[ reg15 ] = result
        
       elif (opcode5 == 8):                        # store
            mem[operand25 + reg[dataseg]] = result
        
       elif (opcode5 == 13):                        # store return address
            reg[ reg15 ] = result
        
       elif (opcode5 == 16):                        # store return address
            reg[ reg15 ] = result
       #ic5 = ic - 3
       #print("pstage    : ", pstage)
       print("write back:" , "ic=",ics5)
       totopr[ics5] = totopr[ics5] + 1
   return(0)

# opcode type (1 reg, 2 reg, reg+addr, immed), mnemonic  
opcodes = { 1: (2, 'add'), 2: ( 2, 'sub'), 
            3: (1, 'dec'), 4: ( 1, 'inc' ),
            7: (3, 'ld'),  8: (3, 'st'), 9: (3, 'ldi'),
            12: (3, 'bnz'), 13: (3, 'brl'),
            14: (1, 'ret'),
            16: (3, 'int') }
startexechere( 0 )                                  # start execution here if no "go"
loadmem()                                            # load binary executable
#loadcache()
ip = 0                                              # start execution at codeseg location 0
ir = 0
opcode2 = 0
opcode3 = 0
opcode4 = 0
opcode5 = 0
reg12 = 0
reg13 = 0
reg14 = 0
reg15 = 0
operand21 = 0
operand22 = 0
operand23 = 0
operand24 = 0
addr2 = 0
addr3 = 0
result = 0
reg2 = 0
operand1 = 0
numcoderefs = 0
pstage = 0
list2 = [9, 7, 4, 3]
list3 = [1, 2]
totalstalls = 0
stalls = 0
is2 = 0
is21 = 0
is22 = 0
flag = 0
ics5 = 0
flag1 = 0
flag2 = 0
dflag = 0
ics4 = 0
ics3 = 0
bhazards = 0
dhazards = 0
bflag = 0
icbw = -2
flags = 0
ipb = 0
wrong = 0
brch = 0
ip2 = 0
flag9 = 0
flag10 = 0
flag11 = 0
chit = 0
cmiss = 0
ir1 = 0
cir1 = 0
nlines = 0
nwords = 0
nlinesbits = 0
nwordsbits = 0
seperatem = 0
#indexdec = 0
#worddec = 0
#benchmark[20][8]
#loadbenchmark()
print("enter no of lines in cache")
nlines = int(raw_input())
print("enter no of words in cache")
nwords = int(raw_input())
print("enter 1 if inst and data cache are seperate else enter 0")
seperatem = int(raw_input())
print("seperatem",seperatem)
print("cache contains lines=" ,nlines, " words=", nwords)
icache = [[0 for x in range(nwords)] for x in range(nlines)]
print("here is initialized icache")
print icache
dcache = [[0 for x in range(nwords)] for x in range(nlines)]
print("here is initialized dcache")
print dcache
ictags = [0 for x in range(nlines)]
print("here is initialized ictags")
print ictags
dctags = [0 for x in range(nlines)]
print("here is initialized dctags")
print dctags
nlinesbits = int(math.log(nlines,2))
nwordsbits = int(math.log(nwords,2))
print("nlinebits=",nlinesbits)
print("nwordsbits=",nwordsbits)
x= raw_input()
benchmark = [[0 for x in range(8)] for x in range(50)]
print("here is initialized benchmark")
print benchmark
totopr = [0 for x in range(50)] 
print("here is initialized totopr")
print totopr
totstalls = [0 for x in range(50)] 
print("here is initialized totstalls")
print totstalls
bp = [0 for x in range(50)] 
print("here is initialized branc predictor")
print bp
ja = [0 for x in range(50)] 
print("here is initialized ja")
print ja

         
         

#for i in range(0,20):
#    for j in range(0,8):
#        item = benchmark[i][j]
#        print(item )
# while instruction is not halt
clock = 1
while( 1 ):
   
   if (clock  == 1):
       pstage = pstage + 1
       print("------||-----")
       print("pstage    : ", pstage)
       
       ife()
       
   elif (clock == 2) :
       pstage = pstage + 1
       print("------||-----")
       print("pstage    : ", pstage)
       #print("------||-----")
       ide()
       ife()
       
   elif (clock == 3):
       pstage = pstage + 1
       print("------||-----")
       print("pstage    : ", pstage)
       #print("------||-----")
       
       x=of()
       if (x == -1):
           break
       ide()
       ife()
   elif (clock == 4):
       pstage = pstage + 1
       print("------||-----") 
       print("pstage    : ", pstage)
       #print("------||-----")
       
       y = ex()
       if (y == -1):
           break
       x = of()
       if (x == -1):
           break
       ide()
       ife()
       
   elif (clock >= 5):
#       global stalls
       pstage = pstage + 1
       print("------||-----") 
       print("pstage    : ", pstage)
       #print("------||-----")
       
       #if(stalls > 0 ):
       #    is21 = is2 - 1
       #    is22 = is2 - 2
       #    print("ic2-1",is21)
       #    print("ic2-2",is22)
       #if(stalls == 0) :
       wb()
       y = ex()
       if (y == -1):               
           break
       x = of()
       if (x == -1):
           break
       ide()
       ife()
       print(stalls)
       #print("enyer something")
       #x = raw_input()
       #if(stalls > 0) :
       #    print("in 5 cycles", "stalls = ", stalls)
       #    if((stalls > 0) & (totopr[is22] < 5)):
       #        wb()
       #    if((stalls > 0) & (totopr[is21] < 5)):
       #        y = ex()
       #        if (y == -1):
       #            break
       #    stalls = stalls - 1      
       #    if(stalls <= 0):
       #        x = of()
        #       if (x == -1):
        #           break
        #       ide()
        #       ife()
        #       #stalls = stalls + 1        
                 
           
   #stalls = stalls - 1
   #print totopr
   #print("enyer something")
   #x = raw_input()
   clock = clock + 1 
   #mychange for trace
   #print("Instruction =",ic," opcode=",opcode2," reg1=",reg12," reg2=",reg2," addr=",addr2," operand1=",operand1," operand2=",operand23)
   # end of instruction loop
   
# end of execution
print("here is final scoreboard")
print benchmark
print("totalstalls",totalstalls )
print("here is final totopr")
print totopr
print("here is final totstalls")
print totstalls
print("here is final branch hazards")
print bhazards
print("here is final data hazards")
print dhazards
print("here is final bp")
print bp
print("here is final ja")
print ja
print("here is final icache")
print icache
print("here is final dcache")
print dcache
print("brch=",brch)
print("wrong=",wrong)
acc = brch - wrong
print("predictor is accurate  ", acc , "times", "out of", brch)
print("total cache hit =",chit," and cache miss = ",cmiss)
#chitratio = ( chit / (chit + cmiss) ) * 100
tothit = chit + cmiss
#print("tothit",tothit)
cratio = float (chit) / tothit
#print("cratio",cratio)
chitratio = cratio * 100
print("hit ratio = ", chitratio, " %")



curtime =  time.time()
tottime= curtime - starttime
clockrate = 2.1 * 1000
print("clock rate of computer is 2.1 GHz")
print("clocks= ", clock)
print("ic= ",ic)
print("total Pipeline Stages=",pstage)
cpi = float(clock)  / ic
print("cpi = ",cpi)
print("elapsed time = ",tottime)
ips = float(ic)/tottime
#mips = float (clockrate) / cpi
#print("mips=",mips)
print("ips=",ips)
   

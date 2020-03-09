import socket, glob, json

port = 53

ip = '127.0.0.1'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, port))

#Function to load zone files
def  load_zones():
        zonefiles  = glob.glob('zones/*.zone')
        #print (zonefiles)

        jsonzone = {}
        for zone in zonefiles:
                with open(zone) as zonedata:
                        data = json.load(zonedata)
                        zonename = data["$origin"]
                        jsonzone[zonename] = data
        return  (jsonzone)

#Global variable Zonedata
zonedata = load_zones()

#Function to set the flags
def  getflags(flags):

        byte1 = bytes(flags[:1])
        byte2 = bytes(flags[1:2])

        rflags = ''

        #QR flag
        QR =  '1'

        #Opcode
        OPCODE = ''

        for  bit in range(1,5):
                OPCODE += str(ord(byte1)&(1<<bit))

        #AA Authoritative Answer
        AA='1'

        #Truncation  
        TC = '0'

        #Recursion Desired We are not supporting this therefore RD = '0'
        RD = '0'

        #Recursion available is zero
        RA = '0'

        #Reserve bits
        Z = '000'

        #Response Code
        RCODE = '0000'

        return int(QR + OPCODE + AA + TC + RD, 2).to_bytes(1, byteorder='big') + int(RA + Z + RCODE, 2).to_bytes(1, byteorder='big')


#FUNCTION TO GET DOMAIN
def  getquestiondomain(data):

        state =  0
        expectedlength = 0
        domainstring = ''
        domainparts = []
        x = 0
        y = 0

        for byte in data:
                if state == 1:
                        domainstring += chr(byte)
                        x += 1
                        if byte == 0:
                                break
                        if x == expectedlength:
                                domainparts.append(domainstring)
                                domainstring = ''
                                state = 0
                                x = 0
                else:
                        state = 1
                        expectedlength = byte
                        y +=  (expectedlength + 1)

        questiontype = data[y:y+2]
        #print (questiontype)
        return (domainparts, questiontype)


#Function to get zone records
def  getzone(domain):
        global zonedata

        zone_name = '.'.join(domain) + '.'
        return (zonedata[zone_name])

#Function to get the records
def  getrecs(data):
        domain, questiontype = getquestiondomain(data)

        QT = ''
        if questiontype == b'\x00\x01':
                QT = 'a'

        zone = getzone(domain)
        return  (zone[QT], QT, domain)

#Function to build question
def  buildquestion(domainname, rectype):
        qbytes = b''

        for part in domainname:
                length = len(part)
                qbytes += bytes([length])

                for char in part:
                        qbytes += ord(char).to_bytes(1, byteorder='big')

                #Bytes required for A record
                if rectype == 'a':
                        qbytes +=  (1).to_bytes(2, byteorder='big')

                #Bytes required for Class record
                qbytes += (1).to_bytes(2, byteorder='big')

        return qbytes

#Function to convert records to bytes
def  rectobytes(domainname, rectype, recttl, recval):

        rbytes = b'\xc0\x0c'

        if rectype == 'a':
                rbytes += rbytes + bytes([0]) + bytes([1])

        #For class
        rbytes += rbytes + bytes([0]) + bytes([1])

        #For TTL
        rbytes += int(recttl).to_bytes(4, byteorder='big')

        #Record length as A record in an IPv4 address and it is 4 bytes but the length of data itelf is 2 bytes
        if rectype == 'a':
                rbytes += rbytes + bytes([0]) + bytes([4])

        for part in recval.split('.'):
                rbytes += bytes([int(part)])

        return rbytes

#Fucntion to build response
def  buildresponse(data):

        #Transaction ID
        TransactionID = data[:2]
        TID  = ''
        for byte in TransactionID: 
                TID +=(hex(byte))
        #print (TID)
        #print('\n')

        #Get the Flags
        Flags = getflags(data[2:4])
        #print(Flags)

        #Question Count
        QDCOUNT =  b'\x00\x01'

        #Answer Count
        #getquestiondomain(data[12:])
        ANCOUNT = len(getrecs(data[12:])[0]).to_bytes(2, byteorder='big')
        print (ANCOUNT)

        #Name Server Count
        NSCOUNT = (0).to_bytes(2, byteorder='big')

        #Additional Count
        ADCOUNT = (0).to_bytes(2, byteorder='big')

        #DNS Header
        dnsheader =  TransactionID + Flags + QDCOUNT + ANCOUNT + NSCOUNT + ADCOUNT

        #Create DNS body
        dnsbody = b''

        #Get answer  from query
        records, rectype, domainname = getrecs(data[12:])

        #DNS Question
        dnsquestion = buildquestion(domainname, rectype)

        for record in records:
                dnsbody += rectobytes(domainname, rectype, record['ttl'], record['value'])

        return dnsheader + dnsquestion + dnsbody

while 1:
        data, addr = sock.recvfrom(512)
        r = buildresponse(data)
        sock.sendto(r, addr)

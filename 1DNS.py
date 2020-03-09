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
        print (questiontype)
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
                QT = 'A'

        zone = getzone(domain)
        return  (zone, QT, domain)

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
        print(getrecs(data[12:]))

while 1:
        data, addr = sock.recvfrom(512)
        r = buildresponse(data)
        sock.sendto(r, addr)

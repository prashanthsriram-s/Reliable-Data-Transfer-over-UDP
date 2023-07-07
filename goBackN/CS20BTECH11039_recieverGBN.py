import socket
recieverIP = "10.0.0.2"
recieverPort   = 20002

payloadSize  = 1024
packetSize = 5 + 2 + payloadSize 
lastFlag = '1'
notLastFlag = '0'
# Create a UDP socket
socket_udp = None

def main():
    socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # Bind socket to localIP and localPort
    socket_udp.bind((recieverIP, recieverPort))
    print("UDP socket created successfully....." )
    while True:
        # packetList = []
        expected_seqnum = 1
        f =  open('outputFile.jpg', 'wb')
        lastRecvdPacket = None
        while True:
            #wait to recieve message from the server
            bytesAddressPair = socket_udp.recvfrom(packetSize)
            print("Received a packet")
            recvdMsg = bytesAddressPair[0]
            recvdSeqNum = int(recvdMsg[0:5].decode())
            recvdLastFlag = recvdMsg[5:6].decode()
            print("Recvdseq: "+str(recvdSeqNum)+", expected: "+str(expected_seqnum))
            if recvdSeqNum == expected_seqnum:
                # We have received the expected Packet
                # Send the ack
                lastRecvdPacket = recvdMsg
                ackMsg = recvdMsg[0:6] + '1'.encode() + recvdMsg[7:]
                socket_udp.sendto(ackMsg, bytesAddressPair[1]) 
                # Write this packet to our file
                print("Writing, "+str(len(recvdMsg[7:]))+ "bytes")
                f.write(recvdMsg[7:])
                print("WROTE!")
                # packetList.append(recvdMsg)
                expected_seqnum+=1
                if recvdLastFlag == '1':
                    # We have received the last packet
                    print("Received Last Packet")
                    f.close()
                    print("Write complete, wrote "+str(expected_seqnum-1)+" packets")
            else:
                # We have received a Duplicate/Out of order Packet, So, resend the acknowledgment for the last recvd packet
                if lastRecvdPacket:
                    ackMsg = lastRecvdPacket[0:6] + '1'.encode() + lastRecvdPacket[7:]
                    socket_udp.sendto(ackMsg, bytesAddressPair[1])
                    

if __name__ == '__main__':
    main()
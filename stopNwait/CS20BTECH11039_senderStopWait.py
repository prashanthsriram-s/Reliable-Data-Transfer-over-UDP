import socket
import time
import signal
import os
senderIP = "10.0.0.1"
senderPort   = 20001
recieverAddressPort = ("10.0.0.2", 20002)

payloadSize  = 1024
packetSize = 5 + 1 + 1 + payloadSize # Seqnum + LastPacketFlag + IsAckFlag + payload 
lastFlag = '1'
notLastFlag = '0'
normalFlag = '0'
ackFlag = '1'
default_timeout = 0.100
socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
num_retransmissions = 0

def str_from_seq(seqnum: int) -> str:
    assert seqnum <= 99999
    if seqnum <= 9 :
        return '0000' + str(seqnum)
    elif seqnum <= 99:
        return '000' + str(seqnum)
    elif seqnum <= 999:
        return '00' + str(seqnum)
    elif seqnum <= 9999:
        return '0' + str(seqnum)
    else: return str(seqnum)

def bin_from_seq(seqnum: int):
    return str_from_seq(seqnum).encode()
# Given the file to send, returns a list of packet objects (whose class is defined above)
def prepare_packet_list(filename: str) -> list:
    packetList = []
    seqnum = 1
    prevdata = None
    with open(filename, "rb") as f:
        data = f.read(payloadSize) # Total Packet size = 1000 from data + 16 from seqnum + 8 from flag
        while data:
            packetList.append(bin_from_seq(seqnum) + '00'.encode() + data)
            seqnum+=1
            prevdata = data
            data = f.read(payloadSize)
    packetList[len(packetList)-1] = bin_from_seq(seqnum-1) + '10'.encode() + prevdata
    return packetList

def timeout_handler(signum, frame):
        raise Exception("timeout occurred!")

def try_to_send(packet, timeout = default_timeout):
    global num_retransmissions
    signal.signal(signal.SIGALRM, timeout_handler)
    # Now, send the packet
    seqofPacket = packet[0:5].decode()
    # print("Trying to send pkt "+str(seqofPacket))
    socket_udp.sendto(packet, recieverAddressPort)
    # signal.alarm(timeout) 
    signal.setitimer(signal.ITIMER_REAL, timeout) # Create the timer for timeout
    try:
        while True:
            recvd = socket_udp.recvfrom(packetSize)
            msg = recvd[0]
            ackFlag = msg[6:7].decode()
            seqofAck = msg[0:5].decode()
            if ackFlag == '1' and seqofAck == seqofPacket:
                # We received the correct Ack, So, stop the timer, then have to move to the next packet
                # print("ACK Received for "+str(seqofPacket))
                signal.alarm(0) # Stop the timer
                break
            elif ackFlag == '1' and seqofAck < seqofPacket:
                # We are receiving duplicate Ack, so just keep waiting
                print("Duplicate ack for "+str(seqofAck))
                continue
            else:
                # We have received Something other than ACK????, Just ignore and keep waiting
                print("Wrong ack for "+str(seqofAck))
                continue
    except:
        # A Timeout Exception was made, so we need to resend the packet
        # Simply, call this same fn again
        print("Timed out for "+str(seqofPacket))
        num_retransmissions = num_retransmissions + 1
        try_to_send(packet=packet)
        pass
    else:
        # Packet was successfully sent
        pass

def main():
    # Create a UDP socket at reciever side
    # Send to server using created UDP socket
    packetList = prepare_packet_list('testFile.jpg')
    start_time = time.time()
    for packet in packetList:
        try_to_send(packet)
    end_time = time.time()
    print("Sent!, " + str(len(packetList)) + " packets was sent")
    print("Number of re-transmissions : "+str(num_retransmissions))
    filesize = os.path.getsize('testFile.jpg')
    time_taken = end_time - start_time
    print("Throughput = "+str((filesize/time_taken)/1024))

if __name__ == '__main__':
    main()




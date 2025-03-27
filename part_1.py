from dataclasses import dataclass
import dataclasses
import struct


@dataclass
class Header:
    id: int
    flags: int
    questions_count: int = 0
    answers_count: int = 0
    namer_servers_count: int = 0
    additional_records_count: int = 0

def header_to_bytes(header):
    fields = dataclasses.astuple(header)
    return struct.pack('!HHHHHH', *fields)


@dataclass
class Question:
    qname: bytes
    qtype: int
    qclass: int


def question_to_bytes(question):
    return question.qname + struct.pack('!HH', question.qtype, question.qclass)


# TODO
# Wo ist das festgelegt? 
#   1.) Erst Länge, dann Teil der Domain 
#   2.) 0er Byte zum Schluss?
# Anschauen: RFC 1035
# TODO: Warum ist von dns name und nicht von domain name die Rede?
def encode_dns_name(domain_name):
    encoded = b''
    for part in domain_name.encode('ascii').split(b'.'):
        encoded += bytes([len(part)]) + part
    return encoded + b'\x00'


import random
random.seed(1)
TYPE_A = 1
CLASS_IN = 1


def build_query(domain_name, record_type):
    name = encode_dns_name(domain_name)
    id = random.randint(0, 65535)
    RECURSION_DESIRED = 1 << 8
    header = Header(id=id, questions_count=1, flags=RECURSION_DESIRED)
    question = Question(qname=name, qtype=record_type, qclass=CLASS_IN)
    return header_to_bytes(header) + question_to_bytes(question)


import socket

query = build_query("example.com", TYPE_A)
# hex query for example.com:
# 44cb01000001000000000000076578616d706c6503636f6d0000010001
# hex query for google.com:
# 44cb0100000100000000000006676f6f676c6503636f6d0000010001
if query.hex() == "44cb01000001000000000000076578616d706c6503636f6d0000010001":
    print("QUERY PASST!")
else:
    print("QUERY FALSCH!!!")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(query, ("8.8.8.8", 53))
response, _ = sock.recvfrom(1024)
from dataclasses import dataclass
import dataclasses
from typing import ClassVar
import struct
import random
import socket


# TODO: Setup linter/formatter
# TODO: Add missing type annotations


@dataclass
class Header:
    id: int
    flags: int
    questions_count: int = 1
    answers_count: int = 0
    namer_servers_count: int = 0
    additional_records_count: int = 0

    def to_bytes(self):
        fields = dataclasses.astuple(self)
        return struct.pack('!HHHHHH', *fields)


@dataclass
class Question:
    qname: bytes
    qtype: int
    qclass: int = 1

    # TODO  there may be more query types to come ...
    # TODO Maybe use enum instead of dictionary?
    qtypes: ClassVar =  {'A':1}

    def to_bytes(self):
        return self.qname + struct.pack('!HH', self.qtype, self.qclass)



# TODO Was macht @dataclass genau?? Kann ich trotzdem nen Konstruktor haben?
class Resolver:
    def __init__(self, domain_name, qtype):
        self.domain_name = domain_name
        self.qtype = Question.qtypes[qtype]
        random.seed(1)

    def resolve(self):
        query = self.build_query()
        response, _ = self.send(query)

    def build_query(self):
        id = random.randint(0, 65535)
        flags = 1 << 8 # only the 'Recursion Desired' flag is set
        header = Header(id=id, flags=flags)

        qname = self.__encode_domain_name(self.domain_name)
        question = Question(qname=qname, qtype=self.qtype)
                
        return header.to_bytes() + question.to_bytes()
    
    def send(self, query):
        # hex query for example.com:
        # 44cb01000001000000000000076578616d706c6503636f6d0000010001
        # hex query for google.com:
        # 44cb0100000100000000000006676f6f676c6503636f6d0000010001
        #print( f"Query falsch:  {query.hex()}")
        #print("Query korrekt: 44cb01000001000000000000076578616d706c6503636f6d0000010001")
        if query.hex() == "44cb01000001000000000000076578616d706c6503636f6d0000010001":
            print("QUERY PASST!")
        else:
            print("QUERY FALSCH!!!")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(query, ("8.8.8.8", 53))
        return sock.recvfrom(1024)


    
    def __encode_domain_name(self, domain_name):
        encoded = b''
        for part in domain_name.encode('ascii').split(b'.'):
            encoded += bytes([len(part)]) + part
        return encoded + b'\x00'
    

if __name__ == "__main__":
    # TODO: Read from command line
    domain_name = "example.com"
    qtype = "A"

    Resolver(domain_name, qtype).resolve()
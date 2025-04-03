from dataclasses import dataclass
import dataclasses
from typing import ClassVar
import struct
import random
import socket


@dataclass
class Header:
    id: int
    flags: int
    questions_count: int = 1
    answers_count: int = 0
    namer_servers_count: int = 0
    additional_records_count: int = 0

    def to_bytes(self) -> bytes:
        fields = dataclasses.astuple(self)
        return struct.pack('!HHHHHH', *fields)


@dataclass
class Question:
    qname: bytes
    qtype: int
    qclass: int = 1

    # TODO  there may be more query types to come ...
    # TODO Maybe use enum instead of dictionary?
    qtypes: ClassVar = {'A': 1}

    def to_bytes(self) -> bytes:
        return self.qname + struct.pack('!HH', self.qtype, self.qclass)


class Resolver:
    def __init__(self, domain_name: str, qtype: str):
        self.domain_name: str = domain_name
        self.qtype: int = Question.qtypes[qtype]
        random.seed(1)

    def query(self, name_server: str) -> bytes:
        query = self.__build_query()
        response, _ = self.__send(query, name_server)
        return response

    def __build_query(self) -> bytes:
        id = random.randint(0, 65535)
        flags = 1 << 8  # only the 'Recursion Desired' flag is set
        header = Header(id=id, flags=flags)

        qname = self.__encode_domain_name(self.domain_name)
        question = Question(qname=qname, qtype=self.qtype)

        return header.to_bytes() + question.to_bytes()

    def __send(self, query: bytes, name_server: str) -> tuple[bytes, tuple]:
        # hex query for example.com:
        # 44cb01000001000000000000076578616d706c6503636f6d0000010001
        # hex query for google.com:
        # 44cb0100000100000000000006676f6f676c6503636f6d0000010001
        # print( f"Query falsch:  {query.hex()}")
        # print("Query korrekt: 44cb01000001000000000000076578616d706c6503636f6d0000010001")
        if query.hex() == "44cb01000001000000000000076578616d706c6503636f6d0000010001":
            print("QUERY PASST!")
        else:
            print("QUERY FALSCH!!!")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(query, (name_server, 53))
        return sock.recvfrom(1024)

    def __encode_domain_name(self, domain_name: str) -> bytes:
        encoded = b''
        for part in domain_name.encode('ascii').split(b'.'):
            encoded += bytes([len(part)]) + part
        return encoded + b'\x00'


if __name__ == "__main__":
    # TODO: Read from command line
    domain_name = "example.com"
    qtype = "A"
    name_server = "8.8.8.8"

    Resolver(domain_name, qtype).query(name_server)

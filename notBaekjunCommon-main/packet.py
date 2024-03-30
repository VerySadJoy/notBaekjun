class Packet:
    """
    Packet class for direct socket communication
    between modules. Member field should not be changed directly.

    16 byte header
        - 8 byte length unsigned little endian
        - 1 byte type
        - 7 byte options (null-padded)
    n byte body

    Specifying constant for packet type:
    - Use upper nibble for control message  (ptype & 0xf0 != 0)
        - No data beyond the header
    - Use lower nibble for data message     (ptype & 0xf != 0)
        - Have additional data in the packet body
    """

    T_PING = b"\x10"
    T_CTRL = {T_PING}
    assert all(x[0] & 0xf == 0 and x[0] &0xf0 != 0 for x in T_CTRL)

    T_RESULT = b"\x01"
    T_DATA = {T_RESULT}
    assert all(x[0] & 0xf != 0 and x[0] &0xf0 == 0 for x in T_DATA)

    T_TYPES = T_CTRL | T_DATA
    assert all(type(x) == bytes and len(x) == 1 for x in T_TYPES)

    PING: 'Packet' = None   # Const instance defined below


    def __init__(self, ptype: bytes, length: int, body: str | None, opts = b""):
        """
        body = None only if unknown (if known to be empty, use empty string)
        """
        assert ptype in Packet.T_TYPES
        assert len(opts) <= 7
        assert body is None or len(body) == length
        self.type = ptype
        self.length = length
        self.opts = opts
        self.body = body


    @classmethod
    def from_body(cls, ptype: bytes, body: str):
        assert ptype in Packet.T_DATA
        return cls(ptype, len(body), body)


    @classmethod
    def parse_header(cls, raw: bytes):
        assert len(raw) == 16

        packet_length = int.from_bytes(raw[:8], "little", signed=False)
        opts = raw[9:16]

        header_type = raw[8]
        assert header_type in Packet.T_TYPES

        return cls(header_type, packet_length, None, opts)


    def is_control(self) -> bool:
        return self.type in Packet.T_CTRL


    def is_data(self) -> bool:
        return self.type in Packet.T_DATA


    def raw(self) -> bytes:
        assert self.body is not None
        return self.length.to_bytes(8, "little") + self.type + self.opts.ljust(7, b"\x00") + self.body.encode()


Packet.PING: Packet = Packet(Packet.T_PING, 0, "")

import struct
from dataclasses import dataclass, InitVar
from io import BufferedReader
from pathlib import Path
from loguru import logger as log


@dataclass
class DatHeader:
    f: BufferedReader

    def __post_init__(self):
        self.start_position = self.f.seek(8)
        (
            self.total_length,
            self.region_pointer_offset,
            self._unknown1,
            self.no_records,
        ) = struct.unpack("IIII", self.f.read(16))
        self.f.seek(self.region_pointer_offset)
        if self.f.read(2) != b"\xfe\xfe":
            raise RuntimeError("Pointer Region Incorrect")
        (
            self.region_pointer_length,
            self.unknown2,
            self._unknown3,
            self.pointer_metadata_region,
            self.pointer_records_region,
        ) = struct.unpack("IIIII", self.f.read(20))
        self.f.seek(self.pointer_records_region)
        if self.f.read(2) != b"\xfe\xfe":
            raise RuntimeError("Record Region Incorrect")
        self.record_header_length = struct.unpack("I", self.f.read(4))[0]
        self.start_records_position = (
            self.pointer_records_region + self.record_header_length
        )
        self.f.seek(self.start_position)


@dataclass
class DatRecord:
    f: BufferedReader

    def __post_init__(self):
        if self.f.read(2) != b"\xfa\xfa":
            raise RuntimeError("Pointer Region Incorrect")
        self.record_length, self.remaining_bytes = struct.unpack("II", self.f.read(8))

        # SbRegion Specific Record
        self.unknown1 = self.f.read(6)
        self.identification = self.f.read(41).decode("utf-8")
        self.rung_length = struct.unpack("I", self.f.read(4))[0]
        self.rung = self.f.read(self.rung_length).decode("utf-16")
        log.debug(self.rung)


@dataclass
class DbExtract:
    filename: InitVar[str]

    def __post_init__(self, filename):
        self._filename = Path(filename)
        self._read()

    def _read_magic_number(self, f: BufferedReader):
        if f.read(2) != b"\xfe\xff":
            raise RuntimeError("File isn't a Rockwell database (Dat) file")
        f.seek(0, 0)

    def _read_header(self, f: BufferedReader):
        self.header: DatHeader = DatHeader(f)

    def _read_records(self, f: BufferedReader):
        self.records = []
        f.seek(self.header.start_records_position)
        for i in range(0, self.header.no_records):
            self.records.append(DatRecord(f))

    def _read(self):
        with open(self._filename, "rb") as f:
            # Check the file's magic number to confirm an DAT file
            self._read_magic_number(f)
            self._read_header(f)
            self._read_records(f)
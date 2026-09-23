"""Integrity checks shared by the personal USB build and boot verification."""
import json
import stat
import struct
import uuid
import zlib
from build import digest


def verify_image(path, expected):
    if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode):
        raise ValueError('Expected a regular image file')
    actual = digest(path)
    if actual != expected:
        raise ValueError('Image checksum differs from the build manifest')
    return actual


def esp_offset(path):
    with path.open('rb') as f:
        f.seek(512)
        header = bytearray(f.read(512))
        if header[:8] != b'EFI PART':
            raise ValueError('Missing GPT header')
        length, crc = struct.unpack_from('<II', header, 12)
        if not 92 <= length <= 512:
            raise ValueError('Invalid GPT header size')
        struct.pack_into('<I', header, 16, 0)
        if zlib.crc32(header[:length]) != crc:
            raise ValueError('GPT header checksum mismatch')
        entries_lba, count, size, entries_crc = struct.unpack_from('<QIII', header, 72)
        if not 1 <= count <= 4096 or size < 128 or size > 4096:
            raise ValueError('Invalid GPT entry dimensions')
        f.seek(entries_lba * 512)
        entries = f.read(count * size)
        if len(entries) != count * size or zlib.crc32(entries) != entries_crc:
            raise ValueError('GPT partition array checksum mismatch')
        matches = []
        for i in range(count):
            entry = entries[i*size:(i+1)*size]
            if entry[:16] == uuid.UUID('c12a7328-f81f-11d2-ba4b-00a0c93ec93b').bytes_le:
                start, end = struct.unpack_from('<QQ', entry, 32)
                if start < 34 or end < start or (end + 1)*512 > path.stat().st_size:
                    raise ValueError('EFI partition outside image')
                matches.append(start*512)
        if len(matches) != 1:
            raise ValueError('Expected exactly one EFI system partition')
        return matches[0]


def cache_inputs(recipe, bootstrap_sha256, base_identity):
    return {'recipe_sha256': digest(recipe), 'bootstrap_sha256': bootstrap_sha256,
            'base_identity': base_identity}


def verify_cache(directory, expected):
    state = json.loads((directory/'inputs.json').read_text())
    if state['inputs'] != expected:
        raise ValueError('Cached USB builder inputs changed; rebuild its state directory')
    if state['image'] != (directory/'image-id').read_text().strip():
        raise ValueError('Cached USB builder image identity mismatch')
    return state


def verify_firmware_provenance(provenance, files):
    for key in ('origin', 'device_profile', 'revision', 'license_status'):
        if not isinstance(provenance.get(key), str) or not provenance[key].strip():
            raise ValueError('Firmware provenance missing '+key)
    if provenance.get('redistribution_allowed') is not False:
        raise ValueError('This pipeline accepts personally provisioned firmware only')
    if provenance.get('files') != files:
        raise ValueError('Firmware files differ from the supplied provenance manifest')

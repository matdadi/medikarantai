import hashlib

def generate_hash(id, pasien_id, sistolik, diastolik, bpm, waktu, prev_hash):
    raw_string = f"{id}{pasien_id}{sistolik}{diastolik}{bpm}{waktu}{prev_hash}"
    return hashlib.sha256(raw_string.encode()).hexdigest()
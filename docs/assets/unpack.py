import sys, hashlib, subprocess, os, zipfile

if len(sys.argv) != 4:
    print("Usage: python unpack.py <filename> <key> <iv>")
    sys.exit(1)

filepath = sys.argv[1]
key = sys.argv[2].upper()
iv = sys.argv[3].upper()

if hashlib.sha256(key.encode()).hexdigest() != "71f1dd02796351fcdcf27e12ae578eec46411234a4a4fcb91d3caa498788c303":
    print("Invalid key")
    sys.exit(1)

if hashlib.sha256(iv.encode()).hexdigest() != "a4d8ffb1b39dde120a951f27fa71bf99e5435df20196ccd4a131d181a8cda7b6":
    print("Invalid iv")
    sys.exit(1)

with open(filepath, "rb") as f:
    data = f.read()

expected_md5 = data[0x10:0x20]
data = data[0x20:]

print("Expected MD5 hash:", expected_md5.hex())

if hashlib.md5(data).digest() != expected_md5:
    print("MD5 hash does not match")
    sys.exit(1)

print("Hash OK")

with open("stage1.bin", "wb") as f:
    f.write(data)

subprocess.run(["openssl", "enc", "-d", "-aes-256-cbc", "-d", "-in", "stage1.bin", "-out", "firmware.zip", "-K", key, "-iv", iv, "-nopad"])

os.unlink("stage1.bin")

with zipfile.ZipFile("firmware.zip", "r") as zip_ref:
    with open("update.swu", "wb") as f:
        f.write(zip_ref.read("update/update.swu"))

os.unlink("firmware.zip")
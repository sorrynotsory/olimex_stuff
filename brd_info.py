#!/usr/bin/python3
import smbus;
import subprocess;

# Runs the command completely silently
subprocess.run('echo "2-0050" | sudo tee /sys/bus/i2c/drivers/at24/unbind', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL);

bus = smbus.SMBus(2);    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1

block = bus.read_i2c_block_data(0x50, 0, 32);
print ("Raw data: {}".format(block));
Header = (block[3] << 24) | (block[2] << 16) | (block[1] << 8) | block[0];
if (Header!=0x4f4caa55):
  print ("Invalid EEPROM data");
  print ("Header = {}; should be 0x4f4caa55".format(hex(Header)));
  exit();

BoardID = (block[7] << 24) | (block[6] << 16) | (block[5] << 8) | block[4];

BoardSerial = (block[13] << 24) | (block[12] << 16) | (block[11] << 8) | block[10];

# --- A20-OLinuXino-LIME Variants ---
if (BoardID==7739): BoardName = "A20-OLinuXino-LIME";
if (BoardID==7743): BoardName = "A20-OLinuXino-LIME-n4GB";
if (BoardID==8934): BoardName = "A20-OLinuXino-LIME-n8GB";
if (BoardID==9076): BoardName = "A20-OLinuXino-LIME-s16MB";

# --- T2-OLinuXino-LIME Industrial Variants ---
if (BoardID==9211): BoardName = "T2-OLinuXino-LIME-IND";
if (BoardID==9215): BoardName = "T2-OLinuXino-LIME-s16MB-IND";
if (BoardID==9219): BoardName = "T2-OLinuXino-LIME-e4GB-IND";

# --- A20-OLinuXino-LIME2 Variants ---
if (BoardID==7701): BoardName = "A20-OLinuXino-LIME2";
if (BoardID==7624): BoardName = "A20-OLinuXino-LIME2-n4GB";
if (BoardID==8910): BoardName = "A20-OLinuXino-LIME2-n8GB";
if (BoardID==8340): BoardName = "A20-OLinuXino-LIME2-e4GB";
if (BoardID==9166): BoardName = "A20-OLinuXino-LIME2-e16GB";
if (BoardID==9604): BoardName = "A20-OLinuXino-LIME2-e16Gs16M";

# --- T2-OLinuXino-LIME2 Industrial Variants ---
if (BoardID==9223): BoardName = "T2-OLinuXino-LIME2-IND";
if (BoardID==9227): BoardName = "T2-OLinuXino-LIME2-s16MB-IND";
if (BoardID==9231): BoardName = "T2-OLinuXino-LIME2-e4GB-IND";
if (BoardID==9538): BoardName = "T2-OLinuXino-LIME2-e16Gs16M-IND";

# --- A20-OLinuXino-MICRO Variants ---
if (BoardID==4614): BoardName = "A20-OLinuXino-MICRO";
if (BoardID==4615): BoardName = "A20-OLinuXino-MICRO-n4GB";
if (BoardID==9042): BoardName = "A20-OLinuXino-MICRO-e4GB";
if (BoardID==8828): BoardName = "A20-OLinuXino-MICRO-IND";
if (BoardID==8661): BoardName = "A20-OLinuXino-MICRO-e4GB-IND";

# --- A20-SOM (System on Module) Variants ---
if (BoardID==6317): BoardName = "A20-SOM";
if (BoardID==6515): BoardName = "A20-SOM-n4GB";
if (BoardID==8811): BoardName = "A20-SOM-e4GB";
if (BoardID==9100): BoardName = "A20-SOM-IND";
if (BoardID==8824): BoardName = "A20-SOM-e4GB-IND";

# --- A20-SOM204 Variants ---
if (BoardID==8958): BoardName = "A20-SOM204";
if (BoardID==8991): BoardName = "A20-SOM204-1G-e4GB";
if (BoardID==10257): BoardName = "A20-SOM204-IND";

# --- Additional LIME2 Specialized Variants ---
if (BoardID==8978): BoardName = "A20-OLinuXino-Lime2-Light-e4GB";
if (BoardID==8946): BoardName = "A20-OLinuXino-LIME2-s16MB";

# --- Additional MICRO Storage Variants ---
if (BoardID==8832): BoardName = "A20-OLinuXino-MICRO-e4GB";
if (BoardID==8918): BoardName = "A20-OLinuXino-MICRO-n8GB";

if (block[9] == 255):
  block[9] = 0;

print ("Board: {} Rev.{}{}, Serial: {}, ID: {}".format(BoardName, chr(block[8]), chr(block[9]), hex(BoardSerial), BoardID));

if (block[14] == 0x00):
  print ("External memory: None");
else:
  Type = "";
  if (block[14] == 0x65):  #0x65 = 'e'
    Type = "eMMC";
  if (block[14] == 0x6E):  #0x6E = 'n'
    Type = "NAND";
  if (block[14] == 0x73):  #0x73 = 's'
    Type = "SPI Flash"
  if (block[15] >= 30):
    Size = 1<<(block[15]-30);
    SizeMeasure = "GB";
  else:
    if (block[15] >= 20):
      Size = 1<<(block[15]-20);
      SizeMeasure = "MB";
    else:
      if (block[15] >= 10):
        Size = 1<<(block[15]-10);
        SizeMeasure = "KB";
      else:
        Size = 1<<block[15];
        SizeMeasure = "B";
  print ("External memory: {} {} {}".format(Type, Size, SizeMeasure));

if (block[16] >= 30):
  print ("RAM size = {} GB".format(1<<(block[16]-30)));
else:
  if (block[16] >= 20):
    print ("RAM size = {} MB".format(1<<(block[16]-20)));
  else:
    if (block[16] >= 10):
      print ("RAM size = {} KB".format(1<<(block[16]-10)));
    else:
      print ("RAM size = {} B".format(1<<block[16]));

print ("MAC address: {}{}:{}{}:{}{}:{}{}:{}{}:{}{}".format(chr(block[18]), chr(block[19]), chr(block[20]), chr(block[21]), chr(block[22]), chr(block[23]), chr(block[24]), chr(block[25]), chr(block[26]), chr(block[27]), chr(block[28]), chr(block[29])));


if (block[17] == 1):
  print ("Industrial grade (-45+85) degrees Celsius");
else:
  print ("Commercial grade (0-70) degrees Celsius");

# Runs the command completely silently
subprocess.run('echo "2-0050" | sudo tee /sys/bus/i2c/drivers/at24/bind', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL);

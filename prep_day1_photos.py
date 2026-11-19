"""Crops the owner's Bumrah cut-outs to their subject (and removes the stump fragment left beside the 2020 bowler) for the Day 1 photo scenes.   python3 prep_day1_photos.py"""
from PIL import Image, ImageDraw
C = "data/licensed/cut/"
a = Image.open(C + "nz_day1_bumrah_appeal.png").convert("RGBA"); a.crop(a.getbbox()).save(C + "nz_day1_bumrah_appeal_crop.png")
b = Image.open(C + "bumrah_wellington_2020.png").convert("RGBA"); al = b.split()[3]; ImageDraw.Draw(al).rectangle((272, 1135, 338, 1585), fill=0); b.putalpha(al); b.crop(b.getbbox()).save(C + "bumrah_wellington_2020_crop.png")
print("ok")

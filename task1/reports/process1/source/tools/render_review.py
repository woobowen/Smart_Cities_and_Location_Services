"""Render every final PDF page at 200 dpi. No screenshot reconstruction/OCR."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import fitz,json,hashlib
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
def render_chunk(numbers):
    doc=fitz.open(R/'build/main.pdf');out=R/'review/render_200dpi'
    for n in numbers:doc[n].get_pixmap(dpi=200,alpha=False).save(out/f'p{n+1:03}.png')
    return numbers

def main():
    out=R/'review/render_200dpi';out.mkdir(parents=True,exist_ok=True)
    count=len(fitz.open(R/'build/main.pdf'))
    chunks=[list(range(i,min(i+4,count))) for i in range(0,count,4)]
    with ProcessPoolExecutor(max_workers=4) as pool:list(pool.map(render_chunk,chunks))
    for p in out.glob('p*.png'):
        if int(p.stem[1:])>count:p.unlink()
    try:font=ImageFont.truetype('DejaVuSans.ttf',17)
    except OSError:font=ImageFont.load_default()
    for batch in range(0,count,8):
        sheet=Image.new('RGB',(1440,1080),'#dadada');dr=ImageDraw.Draw(sheet)
        for j,pn in enumerate(range(batch,min(batch+8,count))):
            with Image.open(out/f'p{pn+1:03}.png') as source:
                im=source.convert('RGB');im.thumbnail((348,496))
            x=(j%4)*360;y=(j//4)*540;sheet.paste(im,(x,y+26));dr.text((x+5,y+3),f'PAGE {pn+1}',fill='black',font=font)
        sheet.save(R/f'review/layout_{batch//8+1:02}.jpg',quality=95)
    record={'pdf_sha256':hashlib.sha256((R/'build/main.pdf').read_bytes()).hexdigest(),'dpi':200,'page_count':count,'renderer':'PyMuPDF','scope':'All pages of the current PDF','note':'Rendered page images are review derivatives, never used as chat evidence inputs.'}
    (R/'provenance/render_record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
    print('Rendered',count,'pages at 200 dpi',flush=True)
if __name__=='__main__':main()

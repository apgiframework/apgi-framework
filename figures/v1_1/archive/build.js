const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, ImageRun, HeadingLevel, AlignmentType, PageBreak,
        CommentRangeStart, CommentRangeEnd, CommentReference, Footer, PageNumber, BorderStyle } = require('docx');
const sizeOf = (p) => { const b = fs.readFileSync(p); return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) }; };

const F = JSON.parse(fs.readFileSync('content.json', 'utf8'));
const FONT = 'Arial';
const AUTHOR = 'Claude (figure audit)';

// markup → runs: **bold**, _{sub}, ^{sup}, ~{italic}
function runs(text, base = {}) {
  const out = []; let i = 0; let bold = false; let buf = '';
  const push = (t, extra = {}) => { if (t) out.push(new TextRun({ text: t, font: FONT, bold: bold || base.bold, size: base.size, ...extra })); };
  while (i < text.length) {
    if (text.startsWith('**', i)) { push(buf); buf = ''; bold = !bold; i += 2; continue; }
    const m = /^([_^~])\{([^}]*)\}/.exec(text.slice(i));
    if (m) {
      push(buf); buf = '';
      const kind = m[1], val = m[2];
      if (kind === '_') push(val, { subScript: true });
      else if (kind === '^') push(val, { superScript: true });
      else push(val, { italics: true });
      i += m[0].length; continue;
    }
    buf += text[i]; i++;
  }
  push(buf);
  return out;
}

let cid = 0; const comments = [];
function para(text, opts = {}, cmts = []) {
  const children = [];
  const mine = cmts.filter((c) => !c.used && text.includes(c[0])); mine.forEach(c => c.used = true);
  const ids = mine.map(([, c]) => { const id = cid++; comments.push({ id, author: AUTHOR, initials: 'CA', date: new Date('2026-10-04T12:00:00Z'), children: [new Paragraph({ children: [new TextRun({ text: c, font: FONT, size: 18 })] })] }); return id; });
  ids.forEach(id => children.push(new CommentRangeStart(id)));
  children.push(...runs(text, { size: opts.size || 20 }));
  ids.forEach(id => { children.push(new CommentRangeEnd(id)); children.push(new TextRun({ children: [new CommentReference(id)] })); });
  return new Paragraph({ children, spacing: { after: 120, line: 276 }, alignment: AlignmentType.JUSTIFIED, ...(opts.p || {}) });
}
const label = (t) => new Paragraph({ children: [new TextRun({ text: t, font: FONT, bold: true, size: 18, color: '555555', allCaps: true })], spacing: { before: 120, after: 60 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: 'BBBBBB', space: 2 } } });

const body = [];
body.push(new Paragraph({ heading: HeadingLevel.TITLE, alignment: AlignmentType.CENTER, children: [new TextRun({ text: 'APGI Series Figures', font: FONT })], spacing: { after: 240 } }));
let lastSection = null;
F.forEach((f, idx) => {
  if (f.section !== lastSection) {
    body.push(new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: idx > 0, children: [new TextRun({ text: f.section, font: FONT })], spacing: { before: 120, after: 160 } }));
    lastSection = f.section;
  }
  const newPage = f.section === F[idx - 1]?.section;
  if (f.heading) body.push(new Paragraph({ heading: HeadingLevel.HEADING_2, pageBreakBefore: newPage, children: runs(f.heading), spacing: { after: 120 }, keepNext: true }));
  const p = 'out/' + f.image; const { w, h } = sizeOf(p);
  const W = Math.round(f.width * 96); const H = Math.round(W * h / w);
  const maxH = 8.0 * 96; const scale = H > maxH ? maxH / H : 1;
  body.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { after: 120 }, children: [new ImageRun({ type: 'png', data: fs.readFileSync(p),
    transformation: { width: Math.round(W * scale), height: Math.round(H * scale) },
    altText: { title: (f.heading || 'Graphical abstract').replace(/[_^~]\{([^}]*)\}/g, '$1'), description: f.alt, name: f.id } })] }));
  body.push(label('Caption'));
  f.caption.forEach(t => body.push(para(t, {}, f.comments || [])));
  body.push(label('Source data & statistics'));
  f.source.forEach(t => body.push(para(t, { size: 18 }, f.comments || [])));
});

const doc = new Document({
  creator: 'APGI', title: 'APGI Series Figures', description: 'Figure compendium for the APGI paper series',
  comments: { children: comments },
  styles: {
    default: { document: { run: { font: FONT, size: 20 } } },
    paragraphStyles: [
      { id: 'Title', name: 'Title', basedOn: 'Normal', run: { size: 40, bold: true, font: FONT } },
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 30, bold: true, font: FONT, color: '1F3B57' }, paragraph: { outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 23, bold: true, font: FONT }, paragraph: { outlineLevel: 1 } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: '777777' })] })] }) },
    children: body,
  }],
});
F.forEach(f => (f.comments || []).forEach(c => { if (!c.used) console.log('UNMATCHED', f.id, c[0]); }));
Packer.toBuffer(doc).then(b => { fs.writeFileSync('Final-Figures.docx', b); console.log('written', b.length, 'comments', comments.length); });

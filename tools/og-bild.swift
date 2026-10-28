// Vorschaubild für Teaser (og:image, 1200 × 630) in der hellen CI der App-Store-Bilder („abend-hell“ aus
// store/screenshots.swift im App-Repo): Abendverlauf, Icon, Name, Etikett, Claim mit goldener zweiter Zeile, Pille.
//
//   swift tools/og-bild.swift <icon-1024.png> <ausgabeordner>
//
// Schreibt <ausgabeordner>/og-de.png und og-en.png (ohne Alphakanal).
import AppKit

let width: CGFloat = 1200, height: CGFloat = 630

func rgb(_ r: Int, _ g: Int, _ b: Int, _ a: CGFloat = 1) -> NSColor {
    NSColor(srgbRed: CGFloat(r) / 255, green: CGFloat(g) / 255, blue: CGFloat(b) / 255, alpha: a)
}

let text = rgb(26, 22, 20), accent = rgb(128, 74, 18)
let panorama = [rgb(250, 243, 230), rgb(247, 219, 168), rgb(238, 172, 122)]
let sunlight = rgb(255, 246, 222), glow = rgb(255, 236, 200)
let pillFill = rgb(26, 22, 20), pillText = rgb(250, 240, 222)

struct Card { let file: String, name: String, label: String, claim: [String], pill: String }
let cards = [
    Card(file: "og-de.png", name: "Auszeit", label: "App-Blocker für iPhone und Android",
         claim: ["Abends das Handy weglegen,", "ohne Kampf mit der Willenskraft."],
         pill: "Kein Konto · Keine Daten · Keine Werbung"),
    Card(file: "og-en.png", name: "Off Hours", label: "App blocker for iPhone and Android",
         claim: ["Put the phone down in the evening,", "without a fight with your willpower."],
         pill: "No account · No data · No ads"),
]

func serif(_ size: CGFloat, _ weight: NSFont.Weight = .semibold) -> NSFont {
    let base = NSFont.systemFont(ofSize: size, weight: weight)
    if let d = base.fontDescriptor.withDesign(.serif), let f = NSFont(descriptor: d, size: size) { return f }
    return base
}

/// Zeichnet von oben gemessen und gibt die Höhe zurück.
@discardableResult
func draw(_ s: String, _ font: NSFont, _ color: NSColor, x: CGFloat, top: CGFloat, width w: CGFloat,
          kern: CGFloat = 0, lineHeight: CGFloat = 1, align: NSTextAlignment = .left) -> CGFloat {
    let p = NSMutableParagraphStyle(); p.alignment = align; p.lineHeightMultiple = lineHeight
    let a: [NSAttributedString.Key: Any] = [.font: font, .foregroundColor: color, .paragraphStyle: p, .kern: kern]
    let h = ceil((s as NSString).boundingRect(with: NSSize(width: w, height: 2000), options: [.usesLineFragmentOrigin], attributes: a).height)
    (s as NSString).draw(in: NSRect(x: x, y: height - top - h, width: w, height: h), withAttributes: a)
    return h
}

func radial(_ color: NSColor, strength: CGFloat, center: NSPoint, radius: CGFloat, inner: CGFloat = 0.35) {
    let g = NSGradient(colors: [color.withAlphaComponent(strength), color.withAlphaComponent(strength * inner), color.withAlphaComponent(0)],
                       atLocations: [0, 0.42, 1], colorSpace: .sRGB)!
    g.draw(fromCenter: center, radius: 0, toCenter: center, radius: radius, options: [])
}

let args = CommandLine.arguments
guard args.count == 3, let icon = NSImage(contentsOfFile: args[1]) else {
    FileHandle.standardError.write(Data("Aufruf: swift tools/og-bild.swift <icon-1024.png> <ausgabeordner>\n".utf8))
    exit(1)
}
let output = URL(fileURLWithPath: args[2])

for card in cards {
    let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: Int(width), pixelsHigh: Int(height), bitsPerSample: 8,
                               samplesPerPixel: 3, hasAlpha: false, isPlanar: false, colorSpaceName: .deviceRGB,
                               bytesPerRow: 0, bitsPerPixel: 32)!
    rep.size = NSSize(width: width, height: height)
    NSGraphicsContext.saveGraphicsState()
    let context = NSGraphicsContext(bitmapImageRep: rep)!
    NSGraphicsContext.current = context
    context.imageInterpolation = .high

    NSGradient(colors: panorama)!.draw(in: NSRect(x: 0, y: 0, width: width, height: height), angle: -18)
    radial(sunlight, strength: 0.8, center: NSPoint(x: 330, y: height - 170), radius: 760, inner: 0.37)
    radial(glow, strength: 0.35, center: NSPoint(x: 160, y: height - 130), radius: 320)

    let margin: CGFloat = 72, textWidth = width - 2 * margin
    // Icon mit Schatten wie die Geräte auf den Store-Bildern, daneben der Name.
    let s: CGFloat = 112
    let iconRect = NSRect(x: margin, y: height - 64 - s, width: s, height: s)
    let tile = NSBezierPath(roundedRect: iconRect, xRadius: s * 0.225, yRadius: s * 0.225)
    NSGraphicsContext.saveGraphicsState()
    let shadow = NSShadow(); shadow.shadowColor = NSColor.black.withAlphaComponent(0.34); shadow.shadowBlurRadius = 28
    shadow.shadowOffset = NSSize(width: 0, height: -10)
    shadow.set(); text.setFill(); tile.fill()
    NSGraphicsContext.restoreGraphicsState()
    NSGraphicsContext.saveGraphicsState()
    tile.addClip(); icon.draw(in: iconRect)
    NSGraphicsContext.restoreGraphicsState()
    let nameFont = serif(76)
    let nameHeight = (card.name as NSString).size(withAttributes: [.font: nameFont]).height
    draw(card.name, nameFont, text, x: margin + s + 30, top: 64 + (s - nameHeight) / 2 - 2, width: textWidth - s - 30)

    var top: CGFloat = 64 + s + 54
    top += draw(card.label.uppercased(), .systemFont(ofSize: 22, weight: .bold), accent, x: margin, top: top, width: textWidth, kern: 3.5) + 16
    var size: CGFloat = 70
    while size > 40, card.claim.contains(where: { ($0 as NSString).size(withAttributes: [.font: serif(size)]).width > textWidth - 8 }) { size -= 1 }
    for (i, line) in card.claim.enumerated() {
        top += draw(line, serif(size), i == card.claim.count - 1 ? accent : text, x: margin, top: top, width: textWidth, lineHeight: 0.92) - 2
    }

    let pillFont = NSFont.systemFont(ofSize: 24, weight: .semibold)
    let w = (card.pill as NSString).size(withAttributes: [.font: pillFont]).width + 56
    let r = NSRect(x: margin, y: 56, width: w, height: 54)
    pillFill.setFill(); NSBezierPath(roundedRect: r, xRadius: 27, yRadius: 27).fill()
    let pillHeight = (card.pill as NSString).size(withAttributes: [.font: pillFont]).height
    draw(card.pill, pillFont, pillText, x: r.minX, top: height - r.maxY + (54 - pillHeight) / 2, width: r.width, align: .center)

    NSGraphicsContext.restoreGraphicsState()
    let url = output.appendingPathComponent(card.file)
    try rep.representation(using: .png, properties: [:])!.write(to: url)
    print("\(url.path): Claim \(Int(size)) pt")
}

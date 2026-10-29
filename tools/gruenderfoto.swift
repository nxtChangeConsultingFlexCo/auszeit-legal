// Gründerfoto fürs Pressematerial: aus dem quadratischen Porträt ein Querformat 3:2 (1800 × 1200 px) für die Presse
// und eine kleinere Fassung für die Website (1200 × 800 px), beide auf dem Abendverlauf der Auszeit-CI („abend-hell“
// aus store/screenshots.swift im App-Repo, dieselben Werte wie im Teaserbild tools/og-bild.swift). Die Person wird mit
// der Personenerkennung von Core Image (CIPersonSegmentation) vom Studiohintergrund gelöst; die Maske wird um ein paar
// Pixel verkleinert und weich gezeichnet, damit kein heller Saum bleibt. Das Porträt sitzt rechtsbündig, weil schon die
// Quelle die rechte Schulter am Bildrand abschneidet. Der dunkle Balken am unteren Rand der Quelle fällt weg.
// Bildnachweis und Bildtext stehen als IPTC-, TIFF- und XMP-Metadaten in beiden JPEGs; ohne Zeitstempel, damit ein
// erneuter Lauf dieselben Dateien erzeugt.
//
//   swift tools/gruenderfoto.swift <portraet.jpg> <presse.jpg> <web.jpg> "<Bildnachweis>" "<Bildtext>"
import AppKit
import CoreImage
import ImageIO
import UniformTypeIdentifiers

let args = CommandLine.arguments
guard args.count == 6, let data = try? Data(contentsOf: URL(fileURLWithPath: args[1])),
      let rep = NSBitmapImageRep(data: data), rep.bitsPerSample == 8, let bytes = rep.bitmapData,
      let cg = rep.cgImage else {
    FileHandle.standardError.write(Data("Aufruf: swift tools/gruenderfoto.swift <portraet.jpg> <presse.jpg> <web.jpg> \"<Bildnachweis>\" \"<Bildtext>\"\n".utf8))
    exit(1)
}
let credit = args[4], caption = args[5]
let w = rep.pixelsWide, h = rep.pixelsHigh, bpr = rep.bytesPerRow
let bpp = bpr / w   // Byte je Pixel aus der Zeilenlänge: JPEGs liegen hier meist auf 4 Byte aufgefüllt

func luminance(_ x: Int, _ y: Int) -> Double {   // Zeile 0 ist oben
    let p = bytes + y * bpr + x * bpp
    return 0.299 * Double(p[0]) + 0.587 * Double(p[1]) + 0.114 * Double(p[2])
}

// Dunkler Balken unten (Rest einer Website-Gestaltung): Zeilen, deren linker Rand dunkel ist, von unten gezählt.
var band = 0
while band < h / 4, (0..<6).contains(where: { luminance($0, h - 1 - band) < 150 }) { band += 1 }
if band > 0 { band += 2 }
print("Quelle \(w) × \(h) px, Balken unten \(band) px")

let outW: CGFloat = 1800, outH: CGFloat = 1200
let canvas = CGRect(x: 0, y: 0, width: outW, height: outH)
let W = CGFloat(w), H = CGFloat(h), U = CGFloat(h - band)
// Core Image zählt von unten: die oberen Zeilen ohne Balken liegen bei y = H − U … H.
let crop = CIImage(cgImage: cg).cropped(to: CGRect(x: 0, y: H - U, width: W, height: U))
    .transformed(by: CGAffineTransform(translationX: 0, y: -(H - U)))

func filter(_ name: String, _ image: CIImage, _ values: [String: Any] = [:]) -> CIImage {
    let f = CIFilter(name: name)!
    f.setValue(image, forKey: kCIInputImageKey)
    for (k, v) in values { f.setValue(v, forKey: k) }
    return f.outputImage!
}
func lanczos(_ image: CIImage, scale: CGFloat) -> CIImage {
    filter("CILanczosScaleTransform", image, [kCIInputScaleKey: scale, kCIInputAspectRatioKey: 1.0])
}

// Porträt auf 1200 px Höhe, rechtsbündig; Maske der Person auf der Quelle gerechnet und genauso platziert.
let scale = outH / U
let photoW = (W * scale).rounded()
let place = CGAffineTransform(translationX: outW - photoW, y: 0)
let photo = lanczos(crop, scale: scale).cropped(to: CGRect(x: 0, y: 0, width: photoW, height: outH)).transformed(by: place)
let rawMask = filter("CIPersonSegmentation", crop, ["inputQualityLevel": 0])   // 0 = genau
let maskScale = CGAffineTransform(scaleX: photoW / rawMask.extent.width, y: outH / rawMask.extent.height)
var mask = rawMask.transformed(by: maskScale).transformed(by: place).clampedToExtent()
mask = filter("CIMorphologyMinimum", mask, [kCIInputRadiusKey: 3])            // Saum des alten Freistellers weg
mask = filter("CIGaussianBlur", mask, [kCIInputRadiusKey: 1.2]).cropped(to: canvas)

// Abendverlauf wie auf den Store-Bildern und dem Teaserbild: Verlauf von links oben nach rechts unten, Abendlicht
// links oben, warmer Schein hinter der Person.
func rgb(_ r: Int, _ g: Int, _ b: Int) -> NSColor { NSColor(srgbRed: CGFloat(r) / 255, green: CGFloat(g) / 255, blue: CGFloat(b) / 255, alpha: 1) }
func radial(_ color: NSColor, strength: CGFloat, center: NSPoint, radius: CGFloat, inner: CGFloat = 0.35) {
    let g = NSGradient(colors: [color.withAlphaComponent(strength), color.withAlphaComponent(strength * inner), color.withAlphaComponent(0)],
                       atLocations: [0, 0.42, 1], colorSpace: .sRGB)!
    g.draw(fromCenter: center, radius: 0, toCenter: center, radius: radius, options: [])
}
let bgRep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: Int(outW), pixelsHigh: Int(outH), bitsPerSample: 8,
                             samplesPerPixel: 3, hasAlpha: false, isPlanar: false, colorSpaceName: .deviceRGB,
                             bytesPerRow: 0, bitsPerPixel: 32)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: bgRep)
NSGradient(colors: [rgb(250, 243, 230), rgb(247, 219, 168), rgb(238, 172, 122)])!.draw(in: NSRect(x: 0, y: 0, width: outW, height: outH), angle: -18)
radial(rgb(255, 246, 222), strength: 0.8, center: NSPoint(x: 480, y: outH - 230), radius: 1000, inner: 0.37)
radial(rgb(255, 236, 200), strength: 0.35, center: NSPoint(x: outW - photoW / 2, y: outH - 520), radius: 640)
NSGraphicsContext.restoreGraphicsState()
let background = CIImage(cgImage: bgRep.cgImage!)

// Die Maske der Personenerkennung liegt nur im Rotkanal, deshalb der Rot-Mischer.
let blend = CIFilter(name: "CIBlendWithRedMask")!
blend.setValue(photo, forKey: kCIInputImageKey)
blend.setValue(background, forKey: kCIInputBackgroundImageKey)
blend.setValue(mask, forKey: kCIInputMaskImageKey)
let press = blend.outputImage!.cropped(to: canvas)
let web = lanczos(press, scale: 1200 / outW).cropped(to: CGRect(x: 0, y: 0, width: 1200, height: 800))

let srgb = CGColorSpace(name: CGColorSpace.sRGB)!
let context = CIContext(options: [.workingColorSpace: srgb, .outputColorSpace: srgb])

func write(_ image: CIImage, to path: String, quality: Double) {
    guard let out = context.createCGImage(image, from: image.extent, format: .RGBA8, colorSpace: srgb),
          let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.jpeg.identifier as CFString, 1, nil) else {
        FileHandle.standardError.write(Data("Konnte \(path) nicht schreiben.\n".utf8)); exit(1)
    }
    let iptc: [CFString: Any] = [kCGImagePropertyIPTCCredit: credit, kCGImagePropertyIPTCCopyrightNotice: credit,
                                 kCGImagePropertyIPTCObjectName: "Karl Maier, MA", kCGImagePropertyIPTCCaptionAbstract: caption]
    let tiff: [CFString: Any] = [kCGImagePropertyTIFFCopyright: credit, kCGImagePropertyTIFFImageDescription: caption]
    let properties: [CFString: Any] = [kCGImageDestinationLossyCompressionQuality: quality,
                                       kCGImagePropertyIPTCDictionary: iptc, kCGImagePropertyTIFFDictionary: tiff]
    CGImageDestinationAddImage(dest, out, properties as CFDictionary)
    guard CGImageDestinationFinalize(dest) else { FileHandle.standardError.write(Data("Konnte \(path) nicht schreiben.\n".utf8)); exit(1) }
    let size = (try? FileManager.default.attributesOfItem(atPath: path)[.size] as? Int) ?? 0
    print("\(path): \(out.width) × \(out.height) px, \(size / 1024) KB")
}
write(press, to: args[2], quality: 0.88)
write(web, to: args[3], quality: 0.82)

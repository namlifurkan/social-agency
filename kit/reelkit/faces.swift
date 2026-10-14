import Foundation
import Vision
import AppKit

for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { print("\(path)\t[]"); continue }
    let req = VNDetectFaceRectanglesRequest()
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
    let faces = (req.results ?? []).filter { $0.confidence > 0.6 }.map { f -> String in
        let b = f.boundingBox
        return String(format: "[%.3f,%.3f,%.3f,%.3f]", b.minX, 1 - b.maxY, b.width, b.height)
    }
    print("\(path)\t[\(faces.joined(separator: ","))]")
}

// Rechnet die App-Vorschau (886 × 1920, 22 s, etwa 12 MB) für die Website herunter: H.264 auf 554 × 1200, AAC, mit
// Ton, „fast start“ für das Abspielen im Browser. Nur AVFoundation, kein ffmpeg.
//
//   swift tools/video.swift <quelle.mp4> <ziel.mp4> [videobitrate in kbit/s, Vorgabe 850]
//
// Quelle: ~/Documents/Auszeit Store-Video 2026-10-20/store-video-de.mp4 bzw. -en.mp4 (aus store/video im App-Repo).
import AVFoundation

let args = CommandLine.arguments
guard args.count >= 3 else {
    FileHandle.standardError.write(Data("Aufruf: swift tools/video.swift <quelle.mp4> <ziel.mp4> [kbit/s]\n".utf8))
    exit(1)
}
let source = URL(fileURLWithPath: args[1]), target = URL(fileURLWithPath: args[2])
let videoBitrate = (args.count > 3 ? Int(args[3]) ?? 850 : 850) * 1000
let width = 554, height = 1200
try? FileManager.default.removeItem(at: target)

final class Pump: @unchecked Sendable {
    let output: AVAssetReaderOutput, input: AVAssetWriterInput
    init(_ output: AVAssetReaderOutput, _ input: AVAssetWriterInput) { self.output = output; self.input = input }
}

func run() async throws {
    let asset = AVURLAsset(url: source)
    let reader = try AVAssetReader(asset: asset)
    let writer = try AVAssetWriter(outputURL: target, fileType: .mp4)
    writer.shouldOptimizeForNetworkUse = true
    var pumps: [Pump] = []

    guard let videoTrack = try await asset.loadTracks(withMediaType: .video).first else { throw NSError(domain: "video", code: 1) }
    let videoOut = AVAssetReaderTrackOutput(track: videoTrack, outputSettings: [
        kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_420YpCbCr8BiPlanarVideoRange])
    videoOut.alwaysCopiesSampleData = false
    reader.add(videoOut)
    let videoIn = AVAssetWriterInput(mediaType: .video, outputSettings: [
        AVVideoCodecKey: AVVideoCodecType.h264,
        AVVideoWidthKey: width, AVVideoHeightKey: height,
        AVVideoScalingModeKey: AVVideoScalingModeResizeAspectFill,
        AVVideoColorPropertiesKey: [AVVideoColorPrimariesKey: AVVideoColorPrimaries_ITU_R_709_2,
                                    AVVideoTransferFunctionKey: AVVideoTransferFunction_ITU_R_709_2,
                                    AVVideoYCbCrMatrixKey: AVVideoYCbCrMatrix_ITU_R_709_2],
        AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: videoBitrate,
                                          AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel,
                                          AVVideoMaxKeyFrameIntervalKey: 60,
                                          AVVideoExpectedSourceFrameRateKey: 30],
    ])
    videoIn.transform = try await videoTrack.load(.preferredTransform)
    videoIn.expectsMediaDataInRealTime = false
    writer.add(videoIn)
    pumps.append(Pump(videoOut, videoIn))

    if let audioTrack = try await asset.loadTracks(withMediaType: .audio).first {
        let audioOut = AVAssetReaderTrackOutput(track: audioTrack, outputSettings: [
            AVFormatIDKey: kAudioFormatLinearPCM, AVSampleRateKey: 48000, AVNumberOfChannelsKey: 2,
            AVLinearPCMBitDepthKey: 16, AVLinearPCMIsFloatKey: false, AVLinearPCMIsBigEndianKey: false,
            AVLinearPCMIsNonInterleaved: false])
        reader.add(audioOut)
        let audioIn = AVAssetWriterInput(mediaType: .audio, outputSettings: [
            AVFormatIDKey: kAudioFormatMPEG4AAC, AVSampleRateKey: 48000, AVNumberOfChannelsKey: 2,
            AVEncoderBitRateKey: 96000])
        audioIn.expectsMediaDataInRealTime = false
        writer.add(audioIn)
        pumps.append(Pump(audioOut, audioIn))
    }

    guard reader.startReading(), writer.startWriting() else {
        throw reader.error ?? writer.error ?? NSError(domain: "video", code: 2)
    }
    writer.startSession(atSourceTime: .zero)
    await withTaskGroup(of: Void.self) { group in
        for (i, pump) in pumps.enumerated() {
            group.addTask {
                await withCheckedContinuation { (done: CheckedContinuation<Void, Never>) in
                    pump.input.requestMediaDataWhenReady(on: DispatchQueue(label: "pump\(i)")) {
                        while pump.input.isReadyForMoreMediaData {
                            if let sample = pump.output.copyNextSampleBuffer() {
                                pump.input.append(sample)
                            } else {
                                pump.input.markAsFinished()
                                done.resume()
                                return
                            }
                        }
                    }
                }
            }
        }
    }
    await writer.finishWriting()
    if writer.status != .completed { throw writer.error ?? NSError(domain: "video", code: 3) }
    let size = (try FileManager.default.attributesOfItem(atPath: target.path)[.size] as? Int) ?? 0
    print("\(target.path): \(width) × \(height), \(size / 1024) KB")
}

let semaphore = DispatchSemaphore(value: 0)
Task {
    do { try await run() } catch { FileHandle.standardError.write(Data("Fehler: \(error)\n".utf8)); exit(1) }
    semaphore.signal()
}
semaphore.wait()

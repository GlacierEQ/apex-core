import Foundation

let path = "/Users/kcbflux/Library/CloudStorage/Dropbox-Cyber.lazer.mermicor"
let url = URL(fileURLWithPath: path)

do {
    try FileManager.default.evictUbiquitousItem(at: url)
    print("Success")
} catch {
    print("Error: \(error)")
}

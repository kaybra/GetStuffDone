import UIKit
import Capacitor

/// Lets the web app switch between the alternate home-screen icons
/// (AppIconLight, AppIconRainbow). Passing no name restores the default icon.
@objc(AppIconPlugin)
public class AppIconPlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "AppIconPlugin"
    public let jsName = "AppIcon"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "setIcon", returnType: CAPPluginReturnPromise)
    ]

    @objc func setIcon(_ call: CAPPluginCall) {
        let name = call.getString("name")
        DispatchQueue.main.async {
            let app = UIApplication.shared
            guard app.supportsAlternateIcons else {
                call.reject("Alternate icons are not supported on this device")
                return
            }
            if app.alternateIconName == name {
                call.resolve()
                return
            }
            app.setAlternateIconName(name) { error in
                if let error = error {
                    call.reject(error.localizedDescription)
                } else {
                    call.resolve()
                }
            }
        }
    }
}

/// Lets the web app match the iOS status bar text (clock, battery) and the
/// overscroll background to the chosen theme. Without this the status bar
/// follows the phone's light/dark mode, which can leave dark text on the
/// dark Synth Wave / Dark themes, or white text on the Light theme.
@objc(ChromePlugin)
public class ChromePlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "ChromePlugin"
    public let jsName = "Chrome"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "setStyle", returnType: CAPPluginReturnPromise)
    ]

    @objc func setStyle(_ call: CAPPluginCall) {
        let lightContent = call.getBool("lightContent") ?? true
        let hex = call.getString("background")
        DispatchQueue.main.async {
            if let vc = self.bridge?.viewController as? CAPBridgeViewController {
                vc.setStatusBarStyle(lightContent ? .lightContent : .darkContent)
            }
            if let hex = hex, let color = ChromePlugin.color(fromHex: hex) {
                self.bridge?.webView?.backgroundColor = color
                self.bridge?.webView?.scrollView.backgroundColor = color
                self.bridge?.viewController?.view.backgroundColor = color
            }
            call.resolve()
        }
    }

    private static func color(fromHex hex: String) -> UIColor? {
        var value = hex.trimmingCharacters(in: .whitespacesAndNewlines)
        if value.hasPrefix("#") { value.removeFirst() }
        guard value.count == 6, let rgb = UInt32(value, radix: 16) else { return nil }
        return UIColor(
            red: CGFloat((rgb >> 16) & 0xFF) / 255.0,
            green: CGFloat((rgb >> 8) & 0xFF) / 255.0,
            blue: CGFloat(rgb & 0xFF) / 255.0,
            alpha: 1.0
        )
    }
}

/// Main view controller: the standard Capacitor bridge plus the app icon and chrome plugins.
class AppViewController: CAPBridgeViewController {
    override func capacitorDidLoad() {
        bridge?.registerPluginInstance(AppIconPlugin())
        bridge?.registerPluginInstance(ChromePlugin())
    }
}

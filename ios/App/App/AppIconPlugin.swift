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

/// Main view controller: the standard Capacitor bridge plus the app icon plugin.
class AppViewController: CAPBridgeViewController {
    override func capacitorDidLoad() {
        bridge?.registerPluginInstance(AppIconPlugin())
    }
}

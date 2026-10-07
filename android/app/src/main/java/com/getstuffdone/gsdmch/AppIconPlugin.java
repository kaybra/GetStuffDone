package com.getstuffdone.gsdmch;

import android.content.ComponentName;
import android.content.pm.PackageManager;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * Lets the web app switch between the alternate home-screen icons
 * (AppIconLight, AppIconRainbow). Passing no name restores the default icon.
 *
 * Same JS API as the iOS plugin: AppIcon.setIcon({ name: 'AppIconLight' | 'AppIconRainbow' | null }).
 * On Android each icon is an <activity-alias> in AndroidManifest.xml; exactly one is enabled at a time.
 */
@CapacitorPlugin(name = "AppIcon")
public class AppIconPlugin extends Plugin {

    // alias class name, icon name used by the web app (null = default), enabled in the manifest by default
    private static final String[][] ALIASES = {
        { ".LauncherDefault", null, "true" },
        { ".LauncherLight", "AppIconLight", "false" },
        { ".LauncherRainbow", "AppIconRainbow", "false" }
    };

    @PluginMethod
    public void setIcon(PluginCall call) {
        String name = call.getString("name");
        if (name != null && name.isEmpty()) name = null;

        String target = null;
        for (String[] alias : ALIASES) {
            if ((alias[1] == null && name == null) || (alias[1] != null && alias[1].equals(name))) {
                target = alias[0];
            }
        }
        if (target == null) {
            call.reject("Unknown icon: " + name);
            return;
        }

        PackageManager pm = getContext().getPackageManager();
        String pkg = getContext().getPackageName();

        // Enable the chosen alias first, then disable the others, so there is never a moment with no launcher icon.
        for (String[] alias : ALIASES) {
            if (alias[0].equals(target)) setEnabled(pm, new ComponentName(pkg, pkg + alias[0]), "true".equals(alias[2]), true);
        }
        for (String[] alias : ALIASES) {
            if (!alias[0].equals(target)) setEnabled(pm, new ComponentName(pkg, pkg + alias[0]), "true".equals(alias[2]), false);
        }
        call.resolve();
    }

    private void setEnabled(PackageManager pm, ComponentName component, boolean enabledByDefault, boolean enable) {
        int current = pm.getComponentEnabledSetting(component);
        boolean isEnabled =
            current == PackageManager.COMPONENT_ENABLED_STATE_ENABLED ||
            (current == PackageManager.COMPONENT_ENABLED_STATE_DEFAULT && enabledByDefault);
        if (isEnabled == enable) return; // nothing to do (the web app calls this on every launch)
        pm.setComponentEnabledSetting(
            component,
            enable ? PackageManager.COMPONENT_ENABLED_STATE_ENABLED : PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
            PackageManager.DONT_KILL_APP
        );
    }
}
